## Methodology — how we did the experiments (practical)

This section describes the actual, hands-on steps used in the project: data sources, feature extraction, model training, evaluation, and explainability. It focuses on what we ran and why, so you can reproduce or re-run the experiments quickly.

### Data collection and preprocessing
- Collected traffic: real attack captures were recorded using Wireshark and exported as PCAP. These captures (Slowloris example) were processed into flow records using CICFlowMeter.
- Training dataset: the DVWA dataset (pre-processed CSV) was used for model training and contains ~59,325 labelled flows.
- Final input: processed flows for the model are available as `ai-model/final_model_input.csv` (used for collected/real data analysis).

### Features
- The model uses a 36-feature flow representation (IAT statistics, segment size statistics, header/payload bytes, flag percentages, packet counts and selected Kubernetes metrics). Feature names are kept in `ai-model/saved_models/features_35_with_k8s.txt`.

### Model training (what we used and why)
- Algorithm: Random Forest (tree-ensemble) trained with scikit-learn and saved as a joblib `.pkl` file (examples: `dvwa_attack_detector_36_features.pkl`). The code expects a tree-based model (the SHAP TreeExplainer is efficient and appropriate for this).
- Why Random Forest: robust to noisy flow features, handles mixed numeric ranges without heavy scaling, fast to train, and well-supported by SHAP's TreeExplainer for reliable explanations.
- Alternative / comparison: the repository keeps variants (e.g., a top-20 feature model). We compare the full 36-feature model against a reduced-feature model to check whether removing less-informative features affects detection performance and explanation stability.

### Training and evaluation procedure (steps you can run)
1. Preprocess flows and ensure `ai-model/final_model_input.csv` (collected) and DVWA CSV (training) are present.
2. Train the model (36 features):

```powershell
# Train (if training script is available)
python ai-model/train_model_36_features.py
```

3. Test the model on real flows and save predictions:

```powershell
python ai-model/test_model.py
```

4. Run SHAP explainability analysis (generates plots in `explainable-ai/outputs/`):

```powershell
python explainable-ai/shap_analysis_complete.py
```

The training script (if present) will save the model under `ai-model/saved_models/`. `test_model.py` will load the appropriate saved model and write `ai-model/predictions_output.csv`.

### Comparison experiments we run
- Full vs reduced feature set: train/evaluate the 36-feature model and a top-20 model; compare overall accuracy, per-class counts and prediction confidence. This shows whether a smaller feature set is enough.
- Training vs collected data: we run SHAP on a sample of training flows and on the collected capture (122 flows) to compare feature importance patterns between what the model learned and what the real attack exhibits.

### Evaluation metrics
- Primary checks: class distribution, prediction counts, and average confidence (from `predict_proba`).
- Standard ML metrics (compute as needed): accuracy, precision/recall per class, confusion matrix, and AUC where relevant.

### Explainability (how we explain predictions)
- We use SHAP (TreeExplainer) to get per-feature contributions.
- Practical settings used in the code:
	- Sample ~1,000 flows for summary plots to keep runtime reasonable.
	- `max_display=15` to keep plots readable (bar and summary plots show top features).
	- For multi-class models we compute mean(|SHAP|) across classes for overall importance and also show per-class stacked bars in bar plots.
- Visual outputs saved by the scripts include: beeswarm (summary), bar charts (mean abs SHAP), waterfall (single-sample breakdown), and training-vs-collected comparison plots.

### Model selection and comparison

- We experimentally trained and compared two tree-based classifiers: Random Forest and Gradient Boosting. Both reached very high test accuracy on the DVWA dataset, but we preferred Random Forest for the final system for practical reasons:
	- Robustness: Random Forest aggregates many independent trees so it is less sensitive to a single noisy or missing feature (useful for real captures from Wireshark).
	- Stability of explanations: Random Forest works seamlessly with SHAP's TreeExplainer and produces stable, distributed feature importances that are easier to interpret in forensic reports.
	- Low tuning burden and faster iteration: defaults work well and training can be parallelized (n_jobs) which is helpful during iterative analysis.

- Reproducible scripts and artifacts:
	- To train and compare both models run:

```powershell
python ai-model/train_and_compare_models.py --data "C:\Users\PMLS\Downloads\archive (1)\dvwa_dataset\processed\dvwa_dataset_ml_ready.csv"
```

	- This saves `random_forest.pkl` and `gradient_boosting.pkl` in `ai-model/saved_models/` and writes per-model reports and `training_summary.csv`.
	- To inspect parameters and top features for each trained model run:

```powershell
python ai-model/compare_models_inspect.py
```

	- The human-readable comparison is saved at `ai-model/saved_models/model_comparison.txt`.

Use these artifacts when writing the paper: they provide the exact models, parameter lists, per-class metrics, and top-features used to justify selecting Random Forest in the Methods section.

### Re-running and seeing results in real time
- You can retrain and immediately inspect results by running the three commands above: training, testing, and SHAP analysis. The scripts save models and images so you can open the outputs directory and review the updated SHAP plots.

### Practical notes and limitations
- The collected real attack capture is small (122 flows); use caution when generalizing results.
- Random Forest hyperparameters can be tuned in the training script; for rapid iteration keep default settings and re-run SHAP to compare explanations.

If you want, I can run the training and SHAP analysis here (if you want me to execute commands), or I can help tune hyperparameters and set up a quick retrain-and-evaluate loop.
