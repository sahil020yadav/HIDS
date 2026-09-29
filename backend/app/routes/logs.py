from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import SecurityLog, User, get_db
from app.schemas.log import SecurityLogOut
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=list[SecurityLogOut])
def list_logs(
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(SecurityLog)
        .filter(SecurityLog.user_id == current_user.id)
        .order_by(SecurityLog.id.desc())
        .limit(limit)
        .all()
    )