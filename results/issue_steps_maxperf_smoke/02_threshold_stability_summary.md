# Threshold Stability Summary

Metric stability is measured under threshold perturbations delta in {-0.10, -0.05, 0.00, 0.05, 0.10}.

| ('model_variant', '')   | ('split', '')   |   ('micro_f1', 'mean') |   ('micro_f1', 'std') |   ('macro_f1', 'mean') |   ('macro_f1', 'std') |
|:------------------------|:----------------|-----------------------:|----------------------:|-----------------------:|----------------------:|
| blend_lr_svm            | test            |               0.756114 |             0.0450821 |               0.373167 |             0.0191646 |
| blend_lr_svm            | val             |               0.751509 |             0.0516388 |               0.390396 |             0.0349931 |
| logreg_calibrated       | test            |               0.757669 |             0.0493955 |               0.372846 |             0.0106453 |
| logreg_calibrated       | val             |               0.75653  |             0.0535927 |               0.39207  |             0.0227777 |
| logreg_uncalibrated     | test            |               0.76739  |             0.0187016 |               0.400254 |             0.0110105 |
| logreg_uncalibrated     | val             |               0.761879 |             0.0208265 |               0.407434 |             0.0187795 |
