"""
Streamlit UI for NLP review understanding demo.

Run:
    streamlit run demo_app.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from demo import (
    load_issue_model,
    load_models,
    predict_sentiment as predict_classic_sentiment,
)


APP_TITLE = "NLP Review Demo"


@st.cache_resource(show_spinner=False)
def load_classic_bundle(base_dir: Path):
    vectorizer, selector, model, meta, model_info = load_models(base_dir, verbose=False)
    issue_bundle = load_issue_model(base_dir, verbose=False)
    return vectorizer, selector, model, meta, model_info, issue_bundle


@st.cache_resource(show_spinner=False)
def load_transformer_bundle(base_dir: Path):
    # Lazy import so the app can still run without torch/transformers.
    from demo_transformer import load_transformer_model

    tokenizer, model = load_transformer_model(base_dir, verbose=False)
    return tokenizer, model


def format_prob(value: Any) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if pd.isna(value):
        return "N/A"
    return f"{value:.3f}"


def summarize_issue_labels(result: Dict[str, Any]) -> str:
    issue_rows = result.get("issue_labels", [])
    if issue_rows:
        return ", ".join(f"{row['label']}:{row['confidence']:.2f}" for row in issue_rows)
    fallback = result.get("issue_tags", [])
    if fallback:
        return ", ".join(fallback)
    return "-"


def build_classic_row(text: str, result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "text": text,
        "classic_label": result.get("label", "N/A"),
        "classic_prob_pos": format_prob(result.get("probability")),
        "classic_confidence": result.get("confidence", "N/A"),
        "classic_reason": result.get("fallback_reason") or "-",
        "issue_tags_or_labels": summarize_issue_labels(result),
    }


def build_transformer_row(text: str, result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "text": text,
        "transformer_label": result.get("label", "N/A"),
        "transformer_prob_pos": format_prob(result.get("probability")),
        "transformer_confidence": result.get("confidence", "N/A"),
        "transformer_reason": result.get("fallback_reason") or "-",
    }


def parse_inputs(raw_text: str) -> List[str]:
    lines = [line.strip() for line in raw_text.splitlines()]
    return [line for line in lines if line]


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(
        "Classic sentiment + issue extraction, with optional transformer side-by-side."
    )

    base_dir = Path(__file__).resolve().parent

    with st.sidebar:
        st.header("Options")
        enable_transformer = st.checkbox("Compare with transformer", value=False)
        st.markdown("Model files are loaded from `models/`.")

    try:
        classic_bundle = load_classic_bundle(base_dir)
    except SystemExit:
        st.error("Classic model artifacts are missing. Train or restore `models/` first.")
        return

    vectorizer, selector, model, meta, model_info, issue_bundle = classic_bundle

    tokenizer = None
    transformer_model = None
    transformer_status = "disabled"

    if enable_transformer:
        try:
            tokenizer, transformer_model = load_transformer_bundle(base_dir)
            transformer_status = "ready"
        except Exception as exc:  # noqa: BLE001
            transformer_status = f"unavailable: {exc}"

    st.subheader("Input")
    raw_text = st.text_area(
        "One review per line",
        value="great product!\nterrible experience\nnot bad\ngood but late delivery",
        height=150,
    )

    col_run, col_info = st.columns([1, 2])
    run_clicked = col_run.button("Analyze", type="primary")
    col_info.write(
        f"Classic model: K*={model_info.get('k_features')} | "
        f"thresholds={model_info.get('thresholds')} | "
        f"transformer={transformer_status}"
    )

    if not run_clicked:
        st.info("Enter review lines and click Analyze.")
        return

    inputs = parse_inputs(raw_text)
    if not inputs:
        st.warning("No valid input lines found.")
        return

    classic_rows: List[Dict[str, Any]] = []
    classic_raw: List[Dict[str, Any]] = []

    for text in inputs:
        result = predict_classic_sentiment(
            text,
            vectorizer,
            selector,
            model,
            meta,
            issue_bundle=issue_bundle,
        )
        classic_rows.append(build_classic_row(text, result))
        classic_raw.append({"text": text, "classic": result})

    classic_df = pd.DataFrame(classic_rows)
    st.subheader("Classic Pipeline Output")
    st.dataframe(classic_df, use_container_width=True)

    if enable_transformer and tokenizer is not None and transformer_model is not None:
        from demo_transformer import predict_sentiment as predict_transformer_sentiment

        transformer_rows: List[Dict[str, Any]] = []
        merged_rows: List[Dict[str, Any]] = []

        for item in classic_raw:
            text = item["text"]
            t_result = predict_transformer_sentiment(text, tokenizer, transformer_model)
            transformer_rows.append(build_transformer_row(text, t_result))

            merged = build_classic_row(text, item["classic"])
            merged.update(
                {
                    "transformer_label": t_result.get("label", "N/A"),
                    "transformer_prob_pos": format_prob(t_result.get("probability")),
                    "transformer_reason": t_result.get("fallback_reason") or "-",
                }
            )
            merged_rows.append(merged)

        st.subheader("Classic vs Transformer")
        st.dataframe(pd.DataFrame(merged_rows), use_container_width=True)
    elif enable_transformer:
        st.warning("Transformer comparison requested but model/dependencies are unavailable.")

    with st.expander("Raw JSON outputs"):
        st.json(classic_raw)


if __name__ == "__main__":
    main()
