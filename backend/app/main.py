from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.database import SecurityLog, SessionLocal, init_db
from app.routes import analytics, auth, dashboard, logs, predict
from app.utils.config import settings
from ml.preprocessing.model_loader import ModelNotFoundError, get_model_bundle

app = FastAPI(title="HIDS-IoT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Ensures any unhandled crash still returns a normal JSON response WITH
    # CORS headers attached, instead of the browser reporting a confusing
    # "blocked by CORS policy" error that hides the real Python exception.
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(logs.router)
app.include_router(analytics.router)


@app.on_event("startup")
def on_startup():
    init_db()

    db = SessionLocal()
    try:
        db.add(SecurityLog(user_id=None, event_type="STARTUP", message="Backend started", severity="INFO"))
        db.commit()

        try:
            bundle = get_model_bundle()
            info = bundle.info()
            db.add(
                SecurityLog(
                    user_id=None,
                    event_type="MODEL_LOADED",
                    message=f"{info['model_file']} ({info['model_type']}, {info['n_features']} features, pipeline={info['is_pipeline']})",
                    severity="INFO",
                )
            )
            db.commit()
        except ModelNotFoundError as e:
            db.add(SecurityLog(user_id=None, event_type="MODEL_LOAD_FAILED", message=str(e), severity="ERROR"))
            db.commit()
            print(f"[WARNING] {e}")
            print("[WARNING] /api/model/info and /api/predict will fail until a valid model is placed. See README.md.")
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}