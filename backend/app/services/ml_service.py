import json

from sqlalchemy.orm import Session

from app.models.database import Prediction, SecurityLog, User
from ml.preprocessing.model_loader import get_model_bundle


def get_model_info() -> dict:
    return get_model_bundle().info()


def run_prediction(db: Session, user: User, values: dict) -> Prediction:
    bundle = get_model_bundle()
    result = bundle.predict(values)  # raises ValueError on missing features

    record = Prediction(
        user_id=user.id,
        prediction=result["prediction"],
        label=result["label"],
        attack_type=result["attack_type"],
        confidence=result["confidence"],
        risk_level=result["risk_level"],
        input_data=json.dumps(values),
    )
    db.add(record)

    severity = "ALERT" if result["label"] == "Attack" else "INFO"
    db.add(
        SecurityLog(
            user_id=user.id,
            event_type="PREDICTION",
            message=f"{user.email} ran a prediction: {result['label']} ({result['confidence']*100:.1f}% confidence)",
            severity=severity,
        )
    )

    db.commit()
    db.refresh(record)
    return record