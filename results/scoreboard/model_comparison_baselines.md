# Updated Model vs Baseline Comparison

## Sentiment (test split)

| Model | recall_0 | precision_0 | f2_0 | Note |
|---|---:|---:|---:|---|
| logreg_best_variant | 0.9320 | 0.6777 | 0.8670 | Best current |
| decision_tree (w2) | 0.6317 | 0.6467 | 0.6346 | Best Decision Tree baseline |
| random_forest (none) | 0.4887 | 0.9042 | 0.5382 | Best Random Forest baseline |
| distilbert_finetune | 0.8327 | 0.8218 | 0.8305 | Transformer baseline |
| logreg_l2 (syllabus bench) | 0.9134 | 0.7030 | 0.8618 | Classic benchmark baseline |

### Delta vs baselines (f2_0)

- vs best Decision Tree: +0.2323
- vs best Random Forest: +0.3288
- vs Transformer (DistilBERT): +0.0364
- vs syllabus `logreg_l2`: +0.0052

## Issue Multi-label (test split)

| Model | micro_f1 | macro_f1 | subset_accuracy | hamming_loss |
|---|---:|---:|---:|---:|
| ovr_logreg | 0.7826 | 0.3888 | 0.6353 | 0.0578 |
| ovr_linearsvm | 0.7699 | 0.3923 | 0.6150 | 0.0628 |
| ovr_blend_lr_svm | 0.7697 | 0.3823 | 0.6176 | 0.0626 |
| transformer_multilabel | 0.6464 | 0.1878 | 0.5510 | 0.1013 |
| hybrid_route (classic + transformer) | 0.7300 | 0.3376 | 0.6150 | 0.0740 |

- Selected by current policy (max val micro_f1): **ovr_logreg**
- micro_f1 delta vs LinearSVM baseline: +0.0127
- micro_f1 delta vs Blend baseline: +0.0130
- micro_f1 delta vs Transformer multi-label: +0.1363
- micro_f1 delta vs Hybrid route: +0.0526

### Transformer Notes

- Sentiment transformer đã được so trực tiếp: `distilbert_finetune (f2_0=0.8305)` vs model hiện tại `0.8670`.
- Issue transformer cũng đã có kết quả, nhưng được train từ pipeline `src.nlp_ext issue_transformer_multilabel` nên có thể khác cấu hình split/sampling so với `src.issue_steps train`.
- Đối chiếu fair-split (classic vs transformer/hybrid cùng test split) xem thêm: `results/scoreboard/issue_fair_comparison.md`.

### Dummy Baseline Notes

- Code đã bổ sung dummy baselines cho:
  - Sentiment step08 (`dummy_most_frequent`, `dummy_stratified`)
  - Issue training (`dummy_labelset_majority`, `dummy_label_prior`)
- Để cập nhật số liệu dummy vào artifacts hiện hành, cần chạy lại:
  - `python -m src.dm2_steps 08 --data_path data/Gift_Cards.jsonl --output_dir results/dm2_steps`
  - `python -m src.issue_steps train --labels_path data/issue_labels.csv --data_path data/Gift_Cards.jsonl --output_dir results/issue_steps --model_dir models/issue_classifier --max_performance`
  - `python scripts/build_scoreboard.py`

_Updated from artifacts on 2026-03-12 01:25:00_
