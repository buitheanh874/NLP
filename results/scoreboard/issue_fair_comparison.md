# Issue Fair Comparison (Classic vs Transformer)

This report separates:
- Fair-split comparison: models evaluated on the same split in `nlp_issue_hybrid_metrics.csv`.
- Reference classic split: metrics from `results/issue_steps/02_metrics_overall.csv`.

## A) Fair split comparison (same test split)

| model                  | split   |   micro_f1 |   macro_f1 |   subset_accuracy |   hamming_loss |
|:-----------------------|:--------|-----------:|-----------:|------------------:|---------------:|
| classic_issue_model    | test    |   0.792358 |   0.527595 |             0.656 |      0.0549444 |
| hybrid_route           | test    |   0.730036 |   0.337592 |             0.615 |      0.074     |
| transformer_multilabel | test    |   0.646363 |   0.187802 |             0.551 |      0.101278  |

- Best fair-split model: **classic_issue_model** (micro_f1=0.7924)
- micro_f1 delta vs transformer_multilabel: +0.1460
- micro_f1 delta vs hybrid_route: +0.0623
- micro_f1 delta vs classic_issue_model: +0.0000

## B) Reference classic split (issue_steps)

| model                   | split   |   micro_f1 |   macro_f1 |   subset_accuracy |   hamming_loss |
|:------------------------|:--------|-----------:|-----------:|------------------:|---------------:|
| dummy_labelset_majority | test    |   0.809324 |   0.10119  |          0.811053 |      0.0437719 |
| dummy_label_prior       | test    |   0.809324 |   0.10119  |          0.811053 |      0.0437719 |
| ovr_logreg              | test    |   0.780327 |   0.387145 |          0.633684 |      0.0585088 |
| ovr_linearsvm           | test    |   0.771327 |   0.405458 |          0.616842 |      0.0623099 |
| ovr_blend_lr_svm        | test    |   0.768171 |   0.39113  |          0.625526 |      0.0620175 |

- Note: section B may use a different split protocol than section A and is shown for reference only.
