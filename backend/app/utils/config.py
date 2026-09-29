"""Centralized configuration, loaded once from environment variables / .env.
Every other module imports `settings` from here instead of reading
os.environ directly, so there's a single source of truth for config."""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    SECRET_KEY: str = "dev-only-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    DATABASE_URL: str = "sqlite:///./database/hids.db"

    MODEL_PATH: str = "ml/model/hids_model.pkl"
    SCALER_PATH: str = "ml/model/scaler.pkl"
    ENCODER_PATH: str = "ml/model/encoder.pkl"
    FEATURE_SELECTOR_PATH: str = "ml/model/feature_selector.pkl"
    SELECTED_FEATURES_PATH: str = "ml/model/selected_features.pkl"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def resolve(self, relative_path: str) -> str:
        """Resolve a config path relative to the backend/ directory, so the
        app works the same whether uvicorn is launched from backend/ or
        from the repo root."""
        p = Path(relative_path)
        if p.is_absolute():
            return str(p)
        return str(BACKEND_DIR / p)


settings = Settings()