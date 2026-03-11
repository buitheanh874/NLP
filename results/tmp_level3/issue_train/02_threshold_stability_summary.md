# Threshold Stability Summary

Metric stability is measured under threshold perturbations delta in {-0.10, -0.05, 0.00, 0.05, 0.10}.

| ('model_variant', '')   | ('split', '')   |   ('micro_f1', 'mean') |   ('micro_f1', 'std') |   ('macro_f1', 'mean') |   ('macro_f1', 'std') |
|:------------------------|:----------------|-----------------------:|----------------------:|-----------------------:|----------------------:|
| logreg_calibrated       | test            |               0.744474 |             0.0935082 |               0.259012 |             0.0403918 |
| logreg_calibrated       | val             |               0.724826 |             0.0589183 |               0.270794 |             0.0603334 |
| logreg_uncalibrated     | test            |               0.725402 |             0.0645321 |               0.224852 |             0.0119623 |
| logreg_uncalibrated     | val             |               0.717266 |             0.0498896 |               0.263757 |             0.0220762 |
