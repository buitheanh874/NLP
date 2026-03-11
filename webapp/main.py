"""
FastAPI server for NLP review inference and dashboard UI.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from webapp.predictor import analyze_reviews, model_status


class PredictRequest(BaseModel):
    texts: List[str]
    include_transformer: bool = False


app = FastAPI(
    title="NLP Review API",
    version="1.0.0",
    description="Classic sentiment + issue extraction with optional transformer comparison.",
)

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/status")
def status(include_transformer: bool = False):
    try:
        return model_status(include_transformer=include_transformer)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/predict")
def predict(payload: PredictRequest):
    if len(payload.texts) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 input rows per request.")

    try:
        return analyze_reviews(
            raw_texts=payload.texts,
            include_transformer=payload.include_transformer,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc

