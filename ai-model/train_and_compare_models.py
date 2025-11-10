"""
Train and compare two classifiers on the DVWA dataset (or any processed flow CSV).

Creates and saves two models (Random Forest and Gradient Boosting) as .pkl files
in `ai-model/saved_models/` and writes a brief metrics CSV to the same folder.

Usage (PowerShell):
    python ai-model/train_and_compare_models.py --data "<path-to-processed-csv>"

The script will look for feature list at `ai-model/saved_models/features_35_with_k8s.txt`.
If not found, it will use all columns except `label` as features.
"""

import argparse
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def load_features_list(features_path):
    if os.path.exists(features_path):
        with open(features_path, 'r') as f:
            features = [line.strip() for line in f if line.strip()]
        return features
    return None


def main():
    parser = argparse.ArgumentParser(description='Train and compare RF and GBM models')
    parser.add_argument('--data', required=False,
                        default=None,
                        help='Path to processed CSV with flows and label column')
    parser.add_argument('--features', required=False,
                        default='ai-model/saved_models/features_35_with_k8s.txt',
                        help='Path to file with feature names (one per line)')
    parser.add_argument('--outdir', required=False, default='ai-model/saved_models', help='Output directory')
    parser.add_argument('--test-size', type=float, default=0.2)
    parser.add_argument('--random-state', type=int, default=42)
    args = parser.parse_args()

    data_path = args.data
    features_path = args.features
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        print("Please provide the correct path to the processed DVWA CSV.")
        return

    print(f"📂 Loading data: {data_path}")
    df = pd.read_csv(data_path)

    # load features list if available
    features = load_features_list(features_path)
    if features:
        missing = [f for f in features if f not in df.columns]
        if missing:
            print(f"⚠️  Warning: {len(missing)} features from list not found in CSV. They will be filled with zeros.")
            for m in missing:
                df[m] = 0
        X = df[features]
    else:
        print("⚠️  No features file found; using all columns except 'label' as features.")
        X = df.drop(columns=['label']) if 'label' in df.columns else df.copy()

    if 'label' not in df.columns:
        print("❌ No 'label' column found in CSV. Ensure dataset has a 'label' column.")
        return

    y = df['label']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y if len(np.unique(y))>1 else None
    )

    print(f"🧪 Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Models to train
    models = {
        'random_forest': RandomForestClassifier(n_estimators=200, random_state=args.random_state, n_jobs=-1),
        'gradient_boosting': GradientBoostingClassifier(n_estimators=200, random_state=args.random_state)
    }

    results = []

    for name, model in models.items():
        print(f"\n🔧 Training {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, output_dict=True, zero_division=0)

        # Save model
        model_path = os.path.join(outdir, f"{name}.pkl")
        joblib.dump(model, model_path)
        print(f"✅ Saved model: {model_path}")

        # Save detailed metrics to CSV-friendly dict
        results.append({
            'model': name,
            'accuracy': acc,
            'n_train': len(X_train),
            'n_test': len(X_test)
        })

        # write classification report per model
        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv(os.path.join(outdir, f"{name}_classification_report.csv"))
        cm = confusion_matrix(y_test, preds)
        pd.DataFrame(cm).to_csv(os.path.join(outdir, f"{name}_confusion_matrix.csv"), index=False)

        print(f"📊 {name} accuracy: {acc:.4f}")

    # summary
    summary_df = pd.DataFrame(results)
    summary_df.to_csv(os.path.join(outdir, 'training_summary.csv'), index=False)
    print(f"\n📁 Training summary saved to: {os.path.join(outdir, 'training_summary.csv')}")


if __name__ == '__main__':
    main()
