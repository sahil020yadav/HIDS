from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.database import SecurityLog, User
from app.schemas.user import LoginRequest, RegisterRequest
from app.utils.security import create_access_token, hash_password, verify_password


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="analyst",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(SecurityLog(user_id=user.id, event_type="REGISTER", message=f"New account created: {user.email}", severity="INFO"))
    db.commit()

    return user


def authenticate_user(db: Session, payload: LoginRequest) -> tuple[User, str]:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        db.add(SecurityLog(user_id=None, event_type="LOGIN_FAILED", message=f"Failed login for {payload.email}", severity="WARNING"))
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    db.add(SecurityLog(user_id=user.id, event_type="LOGIN", message=f"User logged in: {user.email}", severity="INFO"))
    db.commit()

    token = create_access_token(user.id, user.email)
    return user, token