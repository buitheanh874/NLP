# Demo Runbook

## Preconditions
- Activate venv.
- Ensure artifacts exist from:
  - `python -m src.issue_steps train ... --max_performance`
  - `python -m src.run_all ...`

## Fast CLI Demo (Recommended)
```bash
python demo.py "great product and fast delivery" "terrible quality, broke after two days" "not bad at all"
python -m src.issue_steps predict --text "card not working and support did not help"
python demo_transformer.py "good but late shipping"
```

## Optional UI Demo
```bash
streamlit run demo_app.py
```

## Backup Commands (if one component fails)
```bash
python -m src.dm2_steps 11 --text "idk" --data_path data/Gift_Cards.jsonl
python -m src.issue_steps predict --text "idk if this is worth the price"
```

## Expected Direction
- Strong positive text -> `Positive`
- Clear complaint text -> `Negative`/`Needs attention` + issue labels
- Very short/ambiguous text -> `Uncertain` (fallback-safe)
