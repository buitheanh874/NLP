# Threshold Stability Summary

Metric stability is measured under threshold perturbations delta in {-0.10, -0.05, 0.00, 0.05, 0.10}.

| ('model_variant', '')   | ('split', '')   |   ('micro_f1', 'mean') |   ('micro_f1', 'std') |   ('macro_f1', 'mean') |   ('macro_f1', 'std') |
|:------------------------|:----------------|-----------------------:|----------------------:|-----------------------:|----------------------:|
| blend_lr_svm            | test            |               0.739496 |             0.0645354 |               0.369942 |            0.0230827  |
| blend_lr_svm            | val             |               0.735035 |             0.0701146 |               0.383977 |            0.0335274  |
| logreg_calibrated       | test            |               0.756534 |             0.0492031 |               0.373888 |            0.0115948  |
| logreg_calibrated       | val             |               0.754713 |             0.0535863 |               0.385686 |            0.032702   |
| logreg_uncalibrated     | test            |               0.767733 |             0.0177409 |               0.403252 |            0.00463814 |
| logreg_uncalibrated     | val             |               0.761734 |             0.0198564 |               0.407329 |            0.0184505  |
