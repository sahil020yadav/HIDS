from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

import pandas as pd

from app.models.database import Prediction, User, get_db
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("")
def analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Aggregated analytics derived from real stored predictions (confidence
    distribution buckets + risk-vs-label breakdown), for the Analytics page
    charts."""
    rows = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()

    buckets = {"0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0}
    for r in rows:
        pct = r.confidence * 100
        if pct < 25:
            buckets["0-25%"] += 1
        elif pct < 50:
            buckets["25-50%"] += 1
        elif pct < 75:
            buckets["50-75%"] += 1
        else:
            buckets["75-100%"] += 1

    risk_by_label: dict[str, dict[str, int]] = {}
    for r in rows:
        risk_by_label.setdefault(r.label, {}).setdefault(r.risk_level, 0)
        risk_by_label[r.label][r.risk_level] += 1

    return {"confidence_distribution": buckets, "risk_by_label": risk_by_label, "total_analyzed": len(rows)}


@router.post("/dataset-summary")
async def dataset_summary(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Accepts a CSV upload and returns column-level statistics without ever
    holding the whole file as a single in-memory DataFrame at once - it's
    streamed in chunks, so this scales to large IoT datasets rather than
    loading millions of rows in one go."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    CHUNK_SIZE = 50_000
    row_count = 0
    column_names: list[str] = []
    numeric_sums: dict[str, float] = {}
    numeric_counts: dict[str, int] = {}

    try:
        for chunk in pd.read_csv(file.file, chunksize=CHUNK_SIZE, low_memory=False):
            if not column_names:
                column_names = list(chunk.columns)
            row_count += len(chunk)
            numeric_chunk = chunk.select_dtypes(include="number")
            for col in numeric_chunk.columns:
                numeric_sums[col] = numeric_sums.get(col, 0.0) + float(numeric_chunk[col].sum())
                numeric_counts[col] = numeric_counts.get(col, 0) + int(numeric_chunk[col].count())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    numeric_means = {
        col: round(numeric_sums[col] / numeric_counts[col], 4)
        for col in numeric_sums
        if numeric_counts.get(col, 0) > 0
    }

    return {
        "filename": file.filename,
        "row_count": row_count,
        "column_count": len(column_names),
        "columns": column_names,
        "numeric_column_means": numeric_means,
    }