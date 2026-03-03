# NLP Project: E-commerce Review Understanding

Repository da duoc don gon de chi giu cac thanh phan phuc vu mon NLP.

## Scope
- Task A: Sentiment classification (Negative/Positive/Uncertain) voi TF-IDF + chi-square + logistic regression.
- Task B: Multi-label issue extraction (classic ML, one-vs-rest).
- Task C: Transformer extension va syllabus-alignment benchmarks.

## Setup
```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
```

## Data
- Main corpus: `data/Gift_Cards.jsonl` (bat buoc co cot `text`, `rating`).
- Manual issue labels: `data/issue_labels.csv`.

## Core Commands
```bash
# Sentiment demo
python demo.py "great product!" "terrible experience"

# Run full classic NLP sentiment pipeline (steps 01-10)
python -m src.run_all --data_path data/Gift_Cards.jsonl

# Run a single sentiment step (module name dm2_steps la ten legacy)
python -m src.dm2_steps 06b --data_path data/Gift_Cards.jsonl --enable_negation_tagging --enable_char_ngrams

# Train/evaluate issue classifier
python -m src.issue_steps train --labels_path data/issue_labels.csv --data_path data/Gift_Cards.jsonl

# Issue inference
python -m src.issue_steps predict --text "good but slow delivery"
```

## Transformer Extension (Optional)
```bash
python -m src.nlp_ext transformer_finetune --data_path data/Gift_Cards.jsonl
python demo_transformer.py "not bad at all"
```

## Interactive Demo UI (Optional)
```bash
pip install -r requirements-optional.txt
streamlit run demo_app.py
```

## Report
- English report: `results/reports/NLP_project_report.tex` and `.pdf`
- Vietnamese report: `results/reports/NLP_project_report_vi.tex` and `.pdf`
- Rubric checklist and defense flow: `results/reports/NLP_max_score_checklist_vi.md`

## Main Artifacts
- `results/dm2_steps/`: classic sentiment experiment outputs.
- `results/issue_steps/`: issue extraction metrics and plots.
- `results/nlp_ext/`: transformer and syllabus-upgrade outputs.
- `models/`: trained artifacts for demo/inference.

## Notes
- Chi su dung text feature, khong dung metadata.
- Split: rating 1-2 -> negative, 4-5 -> positive, rating 3 giu cho uncertainty analysis.
