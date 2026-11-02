"""
Loads your trained HIDS model exactly as you saved it and exposes a single
ModelBundle that the rest of the backend calls into. This module never
trains anything, never guesses feature names, and never silently reorders
inputs.

Two supported save styles, auto-detected:

1. **Full sklearn Pipeline** (e.g. `joblib.dump(pipeline, "hids_model.pkl")`
   where `pipeline = Pipeline([("scaler", StandardScaler()), ("clf", ...)])`).
   If the loaded object has a `.steps` / `.named_steps` attribute, we treat
   it as a Pipeline and call `.predict()` / `.predict_proba()` on it
   directly - the pipeline handles its own scaling/encoding internally, so
   we do NOT apply anything separately (that would double-preprocess).

2. **Bare estimator + separate preprocessing objects.** If SCALER_PATH /
   ENCODER_PATH / FEATURE_SELECTOR_PATH point to files that exist, they are
   loaded and applied, in that order, before calling the bare model's
   `.predict()`.

Feature-name resolution order (first one found wins):
    1. SELECTED_FEATURES_PATH file (explicit list you saved)
    2. model.feature_names_in_ (auto-recorded by scikit-learn when fit on a
       DataFrame - also present on a Pipeline's final/first step in most
       scikit-learn versions)
    3. generic feature_0..feature_{n-1} sized to model.n_features_in_
"""

import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from app.utils.config import settings


class ModelNotFoundError(RuntimeError):
    pass


class ModelBundle:
    def __init__(self):
        self.model = None
        self.model_filename: str = ""
        self.is_pipeline: bool = False
        self.scaler = None
        self.encoder = None
        self.selector = None
        self.feature_names: List[str] = []
        self.class_labels: List[str] = []
        self.supports_attack_type: bool = False  # True if the model is multi-class
        self._load()

    # ------------------------------------------------------------------ #
    def _load(self):
        model_path = settings.resolve(settings.MODEL_PATH)
        if not os.path.exists(model_path):
            raise ModelNotFoundError(
                f"No trained model found at {model_path}. "
                "Place your .pkl file there or update MODEL_PATH in .env. See README.md."
            )

        self.model = joblib.load(model_path)
        self.model_filename = os.path.basename(model_path)

        # --- detect a full sklearn Pipeline -------------------------------
        self.is_pipeline = hasattr(self.model, "steps") and hasattr(self.model, "named_steps")

        if not self.is_pipeline:
            # Only load separate preprocessing objects for a BARE estimator.
            # A Pipeline already encapsulates its own preprocessing steps.
            for attr, path_setting in (
                ("scaler", settings.SCALER_PATH),
                ("encoder", settings.ENCODER_PATH),
                ("selector", settings.FEATURE_SELECTOR_PATH),
            ):
                full_path = settings.resolve(path_setting)
                if os.path.exists(full_path):
                    setattr(self, attr, joblib.load(full_path))

        # --- resolve feature names/order ----------------------------------
        features_path = settings.resolve(settings.SELECTED_FEATURES_PATH)
        estimator_for_introspection = self._final_estimator()

        if os.path.exists(features_path):
            self.feature_names = list(joblib.load(features_path))
        elif hasattr(self.model, "feature_names_in_"):
            self.feature_names = list(self.model.feature_names_in_)
        elif estimator_for_introspection is not None and hasattr(estimator_for_introspection, "feature_names_in_"):
            self.feature_names = list(estimator_for_introspection.feature_names_in_)
        elif hasattr(self.model, "n_features_in_"):
            self.feature_names = [f"feature_{i}" for i in range(self.model.n_features_in_)]
        elif estimator_for_introspection is not None and hasattr(estimator_for_introspection, "n_features_in_"):
            self.feature_names = [f"feature_{i}" for i in range(estimator_for_introspection.n_features_in_)]
        else:
            raise ModelNotFoundError(
                "Could not determine the model's expected input features. "
                "Save selected_features.joblib alongside the model, or set SELECTED_FEATURES_PATH."
            )

        # --- resolve class labels / multi-class support ---------------------
        classes_source = estimator_for_introspection if estimator_for_introspection is not None else self.model
        if hasattr(classes_source, "classes_"):
            raw_classes = list(classes_source.classes_)
            if set(raw_classes) == {0, 1}:
                self.class_labels = ["Normal", "Attack"]
                self.supports_attack_type = False
            else:
                self.class_labels = [str(c) for c in raw_classes]
                # More than 2 classes (or non-binary labels) means the model
                # itself distinguishes attack subtypes.
                self.supports_attack_type = len(raw_classes) > 2
        else:
            self.class_labels = ["Normal", "Attack"]
            self.supports_attack_type = False

    def _final_estimator(self):
        """For a Pipeline, return its last step (the actual classifier) for
        attribute introspection (classes_, feature_names_in_, etc.)."""
        if self.is_pipeline:
            return self.model.steps[-1][1]
        return None

    # ------------------------------------------------------------------ #
    def info(self) -> Dict[str, Any]:
        return {
            "model_file": self.model_filename,
            "model_type": type(self._final_estimator() or self.model).__name__,
            "is_pipeline": self.is_pipeline,
            "n_features": len(self.feature_names),
            "features": self.feature_names,
            "class_labels": self.class_labels,
            "supports_attack_type": self.supports_attack_type,
        }

    def predict(self, values: Dict[str, float]) -> Dict[str, Any]:
        missing = [f for f in self.feature_names if f not in values]
        if missing:
            raise ValueError(f"Missing required feature(s): {missing}")

        row = pd.DataFrame([[float(values[f]) for f in self.feature_names]], columns=self.feature_names)

        if self.is_pipeline:
            # The pipeline handles scaling/encoding/selection internally.
            model_input = row
            predictor = self.model
        else:
            # Apply separate preprocessing objects, in a fixed, explicit order.
            # NOTE: feature_selector.pkl is intentionally NOT applied here. It was
            # fit on the full raw feature set to CHOOSE the winning columns, but
            # selected_features.pkl already gives us that selector's OUTPUT - the
            # model was trained directly on those columns. Re-running .transform()
            # would require the original ~58 raw columns again, causing a
            # "feature names ... missing" error. The selector is kept loaded only
            # for inspection/debugging, never re-applied at inference.
            model_input = row
            if self.encoder is not None:
                model_input = pd.DataFrame(self.encoder.transform(model_input), columns=model_input.columns)
            if self.scaler is not None:
                model_input = pd.DataFrame(self.scaler.transform(model_input), columns=model_input.columns)
            predictor = self.model

        pred = predictor.predict(model_input)[0]
        pred_int = int(pred) if not isinstance(pred, str) else pred
        label_index = self.class_labels.index(str(pred)) if isinstance(pred, str) else pred_int
        label = self.class_labels[label_index] if 0 <= label_index < len(self.class_labels) else str(pred)

        confidence = 1.0
        if hasattr(predictor, "predict_proba"):
            proba = predictor.predict_proba(model_input)[0]
            confidence = float(np.max(proba))

        is_attack = label.lower() != "normal"
        attack_type = None
        if is_attack:
            attack_type = label if self.supports_attack_type else (
                "Not classified by this model (binary Normal/Attack classifier)"
        )

        risk_level = self._risk_level(is_attack, confidence)

        return {
            "prediction": label_index if isinstance(label_index, int) else 0,
            "label": "Attack" if is_attack else "Normal",
            "attack_type": attack_type,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
        }

    @staticmethod
    def _risk_level(is_attack: bool, confidence: float) -> str:
        if not is_attack:
            return "Low"
        if confidence >= 0.9:
            return "Critical"
        if confidence >= 0.75:
            return "High"
        if confidence >= 0.6:
            return "Medium"
        return "Low"


_bundle: Optional[ModelBundle] = None


def get_model_bundle() -> ModelBundle:
    global _bundle
    if _bundle is None:
        _bundle = ModelBundle()
    return _bundle

##hbelherjhern erbhrhfurhfurffrfirfirfrnfirur
def reload_model_bundle() -> ModelBundle:
    """Force a reload - useful after swapping in a new model file without
    restarting the server."""
    global _bundle
    _bundle = ModelBundle()
    return _bundle
