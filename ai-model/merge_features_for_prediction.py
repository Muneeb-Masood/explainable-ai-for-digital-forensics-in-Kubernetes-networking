"""
Merge Network and Container Metrics for Model Prediction

- Reads network features CSV and container metrics CSV
- Merges them into a single DataFrame with the exact columns as dvwa_features.txt
- Fills missing columns with 0
- Saves the merged CSV for model prediction

Usage:
    python ai-model/merge_features_for_prediction.py --network_csv path/to/network.csv --container_csv path/to/container.csv --output_csv path/to/merged.csv
"""

import pandas as pd
import argparse

FEATURES_PATH = 'ai-model/saved_models/dvwa_features.txt'

def load_feature_list():
    with open(FEATURES_PATH) as f:
        return [line.strip() for line in f if line.strip()]

def main(network_csv, container_csv, output_csv):
    features = load_feature_list()
    print(f"Loaded {len(features)} required features.")

    print(f"Reading network features from {network_csv}")
    net_df = pd.read_csv(network_csv)
    print(f"Reading container metrics from {container_csv}")
    cont_df = pd.read_csv(container_csv)

    # Merge on a common key if available, else concatenate rows
    if 'timestamp' in net_df.columns and 'timestamp' in cont_df.columns:
        merged = pd.merge(net_df, cont_df, on='timestamp', how='outer')
    else:
        merged = pd.concat([net_df, cont_df], axis=1)

    # Keep only required features, fill missing with 0
    merged = merged.reindex(columns=features, fill_value=0)
    print(f"Merged shape: {merged.shape}")

    merged.to_csv(output_csv, index=False)
    print(f"Merged features saved to {output_csv}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--network_csv', required=True, help='Path to network features CSV')
    parser.add_argument('--container_csv', required=True, help='Path to container metrics CSV')
    parser.add_argument('--output_csv', required=True, help='Path to save merged CSV')
    args = parser.parse_args()
    main(args.network_csv, args.container_csv, args.output_csv)
