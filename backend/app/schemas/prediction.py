from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class PredictRequest(BaseModel):
    # Arbitrary feature_name -> numeric value map. Validated server-side
    # against the model's actual expected feature list (see ml_service.py) -
    # we deliberately do NOT hardcode field names here, since they must come
    # from the trained model, not be guessed by the schema.
    values: Dict[str, float]


class PredictResponse(BaseModel):
    id: int
    prediction: int
    label: str
    attack_type: Optional[str] = None
    confidence: float
    risk_level: str
    created_at: datetime


class PredictionOut(BaseModel):
    id: int
    prediction: int
    label: str
    attack_type: Optional[str] = None
    confidence: float
    risk_level: str
    input_data: str
    created_at: datetime

    class Config:
        from_attributes = True


class ModelInfoResponse(BaseModel):
    model_file: str
    model_type: str
    is_pipeline: bool
    n_features: int
    features: List[str]
    class_labels: List[str]
    supports_attack_type: bool


class DashboardStats(BaseModel):
    total_predictions: int
    normal_count: int
    attack_count: int
    attack_percentage: float
    risk_distribution: Dict[str, int]
    attack_type_distribution: Dict[str, int]
    trend: List[Dict[str, object]]
    latest_predictions: List[PredictionOut]