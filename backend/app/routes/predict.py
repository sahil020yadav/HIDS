from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import Prediction, User, get_db
from app.schemas.prediction import ModelInfoResponse, PredictionOut, PredictRequest, PredictResponse
from app.services.ml_service import get_model_info, run_prediction
from app.utils.security import get_current_user
from ml.preprocessing.model_loader import ModelNotFoundError

router = APIRouter(prefix="/api", tags=["prediction"])


@router.get("/model/info", response_model=ModelInfoResponse)
def model_info(current_user: User = Depends(get_current_user)):
    try:
        return get_model_info()
    except ModelNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        record = run_prediction(db, current_user, payload.values)
    except ModelNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return record


@router.get("/predictions", response_model=list[PredictionOut])
def list_predictions(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.id.desc())
        .limit(limit)
        .all()
    )


@router.get("/predictions/{prediction_id}", response_model=PredictionOut)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id, Prediction.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return record