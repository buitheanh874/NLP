"""
FastAPI server for NLP review inference and dashboard UI.
"""

from __future__ import annotations

import csv
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from webapp.predictor import analyze_reviews, model_status
from src.issue_steps.common import ISSUE_LABELS as ISSUE_LABEL_COLUMNS


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
PROJECT_DIR = APP_DIR.parent
ITEMS_DIR = PROJECT_DIR / "items"
DOWNLOADS_DIR = Path.home() / "Downloads"
ITEM_NAME_PRESETS = [
    "Amazon Gift Card - Floral Sleeve",
    "Amazon Gift Card - Birthday Edition",
    "Amazon Gift Card - Thank You Theme",
    "Amazon Gift Card - Elegant Gold Pack",
    "Amazon Gift Card - Celebration Box",
    "Amazon Gift Card - Premium Envelope",
    "Amazon Gift Card - Holiday Special",
    "Amazon Gift Card - Minimalist Pack",
    "Amazon Gift Card - Family Gift Bundle",
]
ITEM_SUBTITLE_PRESETS = [
    "Fast delivery and ready-to-gift packaging.",
    "Top pick for birthdays and quick gifting.",
    "Professional style for business gifting.",
    "Premium print with envelope included.",
    "Popular seasonal design.",
    "Clean design and easy redemption.",
    "Great for teams and family events.",
    "Simple and modern card look.",
    "Great value bundle for repeat gifts.",
]

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
ITEMS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/items", StaticFiles(directory=ITEMS_DIR), name="items")


def _item_meta(file_name: str, index: int) -> dict:
    title = ITEM_NAME_PRESETS[index % len(ITEM_NAME_PRESETS)]
    subtitle = ITEM_SUBTITLE_PRESETS[index % len(ITEM_SUBTITLE_PRESETS)]
    price_vnd = 149000 + index * 25000
    rating = round(min(4.9, 4.3 + (index % 5) * 0.12), 1)
    badge = "Best Seller" if index in {0, 3, 6} else "Prime"
    return {
        "display_name": title,
        "subtitle": subtitle,
        "price_vnd": int(price_vnd),
        "rating": float(rating),
        "badge": badge,
        "file_name": file_name,
    }


def _candidate_review_paths() -> List[Path]:
    env_path = os.getenv("NLP_REVIEW_POOL_CSV", "").strip()
    candidates: List[Path] = []
    if env_path:
        candidates.append(Path(env_path))

    candidates.extend(
        [
            PROJECT_DIR / "data" / "tung_labeled.csv",
            PROJECT_DIR / "data" / "Tung_labeled.csv",
            PROJECT_DIR / "data" / "T\u00f9ng_labeled.csv",
        ]
    )

    if DOWNLOADS_DIR.exists():
        candidates.extend(
            [
                DOWNLOADS_DIR / "T\u00f9ng_labeled.csv",
                DOWNLOADS_DIR / "tung_labeled.csv",
                DOWNLOADS_DIR / "Tung_labeled.csv",
            ]
        )
        candidates.extend(
            sorted(DOWNLOADS_DIR.glob("*labeled*.csv"), key=lambda x: x.name.lower())
        )

    seen = set()
    ordered: List[Path] = []
    for path in candidates:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered


def _read_review_csv(path: Path, limit: int = 3000) -> List[dict]:
    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    for enc in encodings:
        try:
            with path.open("r", encoding=enc, errors="replace", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = [x.strip().lower() for x in (reader.fieldnames or [])]
                if "text" not in fieldnames or "rating" not in fieldnames:
                    return []

                rows: List[dict] = []
                for row in reader:
                    normalized = {str(k).strip().lower(): v for k, v in row.items()}
                    text = str(normalized.get("text", "")).strip()
                    if not text:
                        continue

                    try:
                        rating = int(float(str(normalized.get("rating", "")).strip()))
                    except (TypeError, ValueError):
                        continue
                    rating = max(1, min(5, rating))

                    issue_flags = {}
                    for key in ISSUE_LABEL_COLUMNS:
                        raw = normalized.get(key, 0)
                        try:
                            parsed = float(str(raw).strip())
                            issue_flags[key] = 1 if parsed >= 1 else 0
                        except (TypeError, ValueError):
                            issue_flags[key] = 0

                    rows.append(
                        {
                            "id": str(normalized.get("id", "")).strip(),
                            "rating": rating,
                            "text": text,
                            "issue_flags": issue_flags,
                        }
                    )
                    if len(rows) >= limit:
                        break

                return rows
        except OSError:
            return []

    return []


@lru_cache(maxsize=1)
def load_review_pool() -> dict:
    for path in _candidate_review_paths():
        if not path.exists() or not path.is_file():
            continue
        rows = _read_review_csv(path, limit=5000)
        if rows:
            return {
                "source": str(path),
                "rows": rows,
            }

    return {
        "source": "",
        "rows": [],
    }


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


@app.get("/api/catalog")
def catalog():
    allowed = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    files = [
        item
        for item in sorted(ITEMS_DIR.iterdir(), key=lambda x: x.name.lower())
        if item.is_file() and item.suffix.lower() in allowed
    ]
    items = []
    for idx, file in enumerate(files):
        meta = _item_meta(file.name, idx)
        items.append(
            {
                "name": file.name,
                "url": f"/items/{file.name}",
                **meta,
            }
        )
    return {"items": items}


@app.get("/api/review_pool")
def review_pool(limit: int = 1000):
    limit = max(1, min(3000, int(limit)))
    pool = load_review_pool()
    rows = pool.get("rows", [])
    normalized_rows = []
    for row in rows[:limit]:
        flags = row.get("issue_flags", {})
        normalized_flags = {}
        for key in ISSUE_LABEL_COLUMNS:
            try:
                normalized_flags[key] = 1 if float(flags.get(key, 0)) >= 1 else 0
            except (TypeError, ValueError):
                normalized_flags[key] = 0
        normalized_rows.append(
            {
                "id": row.get("id", ""),
                "rating": row.get("rating", 3),
                "text": row.get("text", ""),
                "issue_flags": normalized_flags,
            }
        )
    return {
        "source": pool.get("source", ""),
        "count": len(normalized_rows),
        "reviews": normalized_rows,
    }


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
