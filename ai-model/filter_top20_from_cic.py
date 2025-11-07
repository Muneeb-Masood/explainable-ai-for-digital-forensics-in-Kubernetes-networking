"""
Filter CICFlowMeter CSV to the top-20 features required by the DVWA model.

Usage:
    python filter_top20_from_cic.py --cic_csv cic_features_output.csv --output_csv top20_features_for_model.csv

Notes:
 - Missing columns will be created and filled with 0.
 - Extra columns in the input will be ignored.
"""

import argparse
import pandas as pd
from pathlib import Path


def load_feature_list(features_txt):
    with open(features_txt, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main(cic_csv, features_txt, output_csv):
    print(f"Reading CICFlowMeter CSV: {cic_csv}")
    df = pd.read_csv(cic_csv)
    print(f"Input shape: {df.shape}")
    print(f"Input columns: {list(df.columns)[:10]}...")  # Show first 10 columns

    wanted = load_feature_list(features_txt)
    print(f"\nLoaded {len(wanted)} target features from {features_txt}")
    print(f"Target features: {wanted[:5]}...")  # Show first 5

    # Ensure all wanted columns exist
    missing = []
    for col in wanted:
        if col not in df.columns:
            df[col] = 0
            missing.append(col)
    
    if missing:
        print(f"\nWarning: {len(missing)} features not found in input CSV (filled with 0):")
        print(f"  {missing[:5]}..." if len(missing) > 5 else f"  {missing}")

    # Reorder and keep only wanted
    out = df[wanted]
    print(f"\nOutput shape: {out.shape}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--cic_csv", required=True, type=Path, help="Path to CICFlowMeter CSV")
    p.add_argument(
        "--features_txt",
        required=False,
        type=Path,
        default=Path("ai-model/saved_models/features_35_with_k8s.txt"),
        help="Path to text file with one feature name per line",
    )
    p.add_argument(
        "--output_csv",
        required=False,
        type=Path,
        default=Path("ai-model/filtered_features.csv"),
        help="Path to save the filtered CSV",
    )
    args = p.parse_args()
    main(args.cic_csv, args.features_txt, args.output_csv)
