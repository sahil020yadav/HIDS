"""SQLAlchemy setup + ORM models for Users, Predictions, and Security Logs."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from app.utils.config import settings

# SQLite needs this connect_arg when used with multiple threads (FastAPI's default).
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="analyst", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="user")
    logs = relationship("SecurityLog", back_populates="user")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction = Column(Integer, nullable=False)       # raw class index, e.g. 0/1
    label = Column(String, nullable=False)             # human label, e.g. "Normal"/"Attack"
    attack_type = Column(String, nullable=True)         # null if not supported by the model
    confidence = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    input_data = Column(Text, nullable=False)           # JSON-encoded input feature values
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False)   # e.g. LOGIN, PREDICTION, MODEL_ERROR
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)     # INFO, WARNING, ALERT, ERROR
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")


def init_db():
    import os

    os.makedirs(os.path.dirname(settings.resolve("database/hids.db")), exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()