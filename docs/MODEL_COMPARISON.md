# Model Comparison Report

This file summarizes the comparison between the two trained models in this project: Random Forest and Gradient Boosting. All artifacts referenced are saved under `ai-model/saved_models/`.

## Quick summary
- Both models were trained on the DVWA processed dataset and evaluated on the same test split (n_test = 11,865). Test accuracy for both models is 0.999410 (see `training_summary.csv`).
- Because raw accuracy is essentially identical, we compare per-class metrics, feature importances, and model characteristics to pick the more suitable model for forensic use.

## Training statistics
- Training samples: 47,460
- Test samples: 11,865
- Saved artifacts (folder): `ai-model/saved_models/`
  - `random_forest.pkl`
  - `gradient_boosting.pkl`
  - `random_forest_classification_report.csv`
  - `gradient_boosting_classification_report.csv`
  - `random_forest_confusion_matrix.csv`
  - `gradient_boosting_confusion_matrix.csv`
  - `training_summary.csv`
  - `model_comparison.txt`

## Per-model performance (selected metrics)

### Overall accuracy
| Model | Test accuracy |
|---|---:|
| Random Forest | 0.999410 |
| Gradient Boosting | 0.999410 |

### Per-class precision / recall / f1 (test set)

Random Forest

| Class | Precision | Recall | F1-score | Support |
|---:|---:|---:|---:|---:|
| 0 | 0.999547 | 0.998867 | 0.999207 | 4414 |
| 1 | 1.000000 | 1.000000 | 1.000000 | 1687 |
| 2 | 0.994179 | 0.997664 | 0.995918 | 856 |
| 3 | 1.000000 | 1.000000 | 1.000000 | 2972 |
| 4 | 1.000000 | 1.000000 | 1.000000 | 1936 |
| **accuracy** | **0.999410** | | |

Gradient Boosting

| Class | Precision | Recall | F1-score | Support |
|---:|---:|---:|---:|---:|
| 0 | 0.999773 | 0.998641 | 0.999207 | 4414 |
| 1 | 1.000000 | 1.000000 | 1.000000 | 1687 |
| 2 | 0.993031 | 0.998832 | 0.995923 | 856 |
| 3 | 1.000000 | 1.000000 | 1.000000 | 2972 |
| 4 | 1.000000 | 1.000000 | 1.000000 | 1936 |
| **accuracy** | **0.999410** | | |

Notes: differences are very small; class 2 shows a slight trade-off (RF higher precision, GB slightly higher recall).

### Observed small numeric differences (explicit)
To make the small differences clearer, below are the per-class tiny deltas (GradientBoosting minus RandomForest):

| Class | Precision Δ (GB - RF) | Recall Δ (GB - RF) |
|---:|---:|---:|
| 0 | +0.000226 | -0.000226 |
| 1 | 0.000000 | 0.000000 |
| 2 | -0.001148 | +0.001168 |
| 3 | 0.000000 | 0.000000 |
| 4 | 0.000000 | 0.000000 |

Interpretation: the largest observed differences are on class 2 (about 0.1 percentage points in precision/recall). These deltas are intentionally small — they confirm both models perform almost identically, with GB trading a tiny increase in recall for a tiny decrease in precision on that class. Use these deltas in the paper to show measurable (but minor) differences between the models.

## Confusion matrices
- See `ai-model/saved_models/random_forest_confusion_matrix.csv` and `ai-model/saved_models/gradient_boosting_confusion_matrix.csv` for the full confusion matrices (CSV). These files show counts per true/predicted class used to compute the metrics above.

## Top features (feature importance)
Top features from the trained models (extracted and saved in `model_comparison.txt`):

Random Forest (top 10)
1. packet_IAT_total
2. fwd_init_win_bytes
3. bwd_segment_size_cov
4. variance_bwd_header_bytes_delta_len
5. ack_flag_percentage_in_total
6. packet_IAT_max
7. fwd_segment_size_cov
8. fwd_segment_size_max
9. std_bwd_header_bytes_delta_len
10. min_fwd_payload_bytes_delta_len

Gradient Boosting (top 10)
1. fwd_init_win_bytes
2. bwd_segment_size_cov
3. fwd_segment_size_variance
4. fwd_packets_IAT_mean
5. variance_bwd_header_bytes_delta_len
6. ack_flag_percentage_in_total
7. std_bwd_header_bytes_delta_len
8. container_network_receive_bytes_rate
9. container_network_transmit_packets_rate
10. fwd_segment_size_max

Interpretation: both models agree on several key features (`fwd_init_win_bytes`, `bwd_segment_size_cov`, header-bytes variance measures, ack_flag percentage). GB concentrates more weight on `fwd_init_win_bytes` while RF spreads importance more evenly across features.

## Model parameter highlights

Random Forest key parameters (from trained model):
- n_estimators: 200
- max_features: sqrt
- bootstrap: True
- random_state: 42

Gradient Boosting key parameters:
- n_estimators: 200
- learning_rate: 0.1
- max_depth: 3
- random_state: 42

## Recommendation and notes for the paper
- Both models achieve essentially the same test accuracy. For the paper we recommend Random Forest for the following reasons:
  1. Robustness to noisy features and missing data (useful for Wireshark captures)
  2. Stable, distributed feature importances that are easier to explain to investigators
  3. Lower tuning burden and faster parallel training (n_jobs)

- Use the saved artifacts when writing the Methods section:
  - Models: `ai-model/saved_models/random_forest.pkl`, `ai-model/saved_models/gradient_boosting.pkl`
  - Metrics and reports: see the CSV files in `ai-model/saved_models/`
  - Feature importance and parameter listing: `ai-model/saved_models/model_comparison.txt`

## Appendix — file locations
- Training summary: `ai-model/saved_models/training_summary.csv`
- Per-model reports: `ai-model/saved_models/random_forest_classification_report.csv`, `ai-model/saved_models/gradient_boosting_classification_report.csv`
- Confusion matrices: `ai-model/saved_models/random_forest_confusion_matrix.csv`, `ai-model/saved_models/gradient_boosting_confusion_matrix.csv`
- Models (.pkl): `ai-model/saved_models/random_forest.pkl`, `ai-model/saved_models/gradient_boosting.pkl`
- SHAP outputs: `explainable-ai/outputs/`

---

If you want, I can also:
- Produce a CSV that directly diffs per-class precision/recall/f1 between the two models.
- Re-run SHAP explainability for both saved models and save side-by-side plots to visually compare explanation stability on the collected capture.
- Run a small hyperparameter sweep for Gradient Boosting (learning_rate / max_depth) and re-evaluate.
