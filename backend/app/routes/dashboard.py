from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.database import Prediction, User, get_db
from app.schemas.prediction import DashboardStats
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Prediction).filter(Prediction.user_id == current_user.id)

    total = q.count()
    normal_count = q.filter(Prediction.label == "Normal").count()
    attack_count = q.filter(Prediction.label == "Attack").count()
    attack_percentage = round((attack_count / total * 100), 2) if total else 0.0

    risk_rows = (
        db.query(Prediction.risk_level, func.count(Prediction.id))
        .filter(Prediction.user_id == current_user.id)
        .group_by(Prediction.risk_level)
        .all()
    )
    risk_distribution = {level: count for level, count in risk_rows}

    attack_type_rows = (
        db.query(Prediction.attack_type, func.count(Prediction.id))
        .filter(Prediction.user_id == current_user.id, Prediction.attack_type.isnot(None))
        .group_by(Prediction.attack_type)
        .all()
    )
    attack_type_distribution = {atype: count for atype, count in attack_type_rows if atype}

    # Build the day-by-day trend in Python rather than SQL, so it stays
    # correct regardless of which database backend is configured.
    all_rows = q.order_by(Prediction.created_at).all()
    trend_map: dict[str, dict[str, int]] = {}
    for r in all_rows:
        day = r.created_at.strftime("%Y-%m-%d")
        bucket = trend_map.setdefault(day, {"day": day, "normal_count": 0, "attack_count": 0})
        if r.label == "Normal":
            bucket["normal_count"] += 1
        else:
            bucket["attack_count"] += 1
    trend = list(trend_map.values())[-14:]

    latest = q.order_by(Prediction.id.desc()).limit(8).all()

    return DashboardStats(
        total_predictions=total,
        normal_count=normal_count,
        attack_count=attack_count,
        attack_percentage=attack_percentage,
        risk_distribution=risk_distribution,
        attack_type_distribution=attack_type_distribution,
        trend=trend,
        latest_predictions=latest,
    )