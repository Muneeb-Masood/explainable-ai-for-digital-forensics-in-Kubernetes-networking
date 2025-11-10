"""
Inspect trained models and produce a concise comparison report.

Outputs saved to: ai-model/saved_models/model_comparison.txt
"""
import joblib
import json
import os
from pathlib import Path


def load_model(path):
    return joblib.load(path)


def main():
    outdir = Path('ai-model/saved_models')
    rf_path = outdir / 'random_forest.pkl'
    gb_path = outdir / 'gradient_boosting.pkl'
    features_path = outdir / 'features_35_with_k8s.txt'

    report_lines = []

    if not rf_path.exists() or not gb_path.exists():
        print('Model files not found in ai-model/saved_models/. Run training first.')
        return

    rf = load_model(str(rf_path))
    gb = load_model(str(gb_path))

    report_lines.append('Model parameter comparison')
    report_lines.append('--- Random Forest params ---')
    rf_params = rf.get_params()
    for k in sorted(rf_params.keys()):
        report_lines.append(f'{k}: {rf_params[k]}')

    report_lines.append('\n--- Gradient Boosting params ---')
    gb_params = gb.get_params()
    for k in sorted(gb_params.keys()):
        report_lines.append(f'{k}: {gb_params[k]}')

    # Feature importances (if available)
    if hasattr(rf, 'feature_importances_'):
        report_lines.append('\nTop features (Random Forest)')
        fi = rf.feature_importances_
        try:
            features = [x.strip() for x in open(features_path).read().splitlines() if x.strip()]
        except Exception:
            features = [f'feat_{i}' for i in range(len(fi))]

        pairs = sorted(list(zip(features, fi)), key=lambda x: x[1], reverse=True)[:15]
        for name, val in pairs:
            report_lines.append(f'{name}: {val:.6f}')

    if hasattr(gb, 'feature_importances_'):
        report_lines.append('\nTop features (Gradient Boosting)')
        fi = gb.feature_importances_
        try:
            features = [x.strip() for x in open(features_path).read().splitlines() if x.strip()]
        except Exception:
            features = [f'feat_{i}' for i in range(len(fi))]

        pairs = sorted(list(zip(features, fi)), key=lambda x: x[1], reverse=True)[:15]
        for name, val in pairs:
            report_lines.append(f'{name}: {val:.6f}')

    out_file = outdir / 'model_comparison.txt'
    with open(out_file, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f'Comparison written to: {out_file}')


if __name__ == '__main__':
    main()
