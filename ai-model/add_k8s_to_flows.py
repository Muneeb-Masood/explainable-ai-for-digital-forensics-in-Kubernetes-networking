#!/usr/bin/env python3
"""
Add K8s metrics to flow data by using average metrics from collection period
Since flows don't have timestamps, we'll use the average K8s metrics
"""

import pandas as pd

# Load the data
print("Loading data...")
k8s = pd.read_csv('ai-model/k8s_metrics.csv')
flows = pd.read_csv('ai-model/mapped_features.csv')

print(f"✓ K8s metrics: {k8s.shape}")
print(f"✓ Flow features: {flows.shape}")

# K8s metric columns
k8s_cols = [
    'container_cpu_usage_seconds_rate',
    'container_memory_usage_bytes', 
    'container_memory_working_set_bytes',
    'container_network_receive_bytes_rate',
    'container_network_transmit_bytes_rate',
    'container_network_receive_packets_rate',
    'container_network_transmit_packets_rate'
]

# Calculate average K8s metrics during the attack period
k8s_avg = k8s[k8s_cols].mean()

print("\n📊 Average K8s metrics during attack:")
for col, val in k8s_avg.items():
    print(f"  {col}: {val:.6f}")

# Add K8s metrics to all flows
print("\nAdding K8s metrics to all flows...")
for col in k8s_cols:
    flows[col] = k8s_avg[col]

# Save the result
output_path = 'ai-model/mapped_features_with_k8s.csv'
flows.to_csv(output_path, index=False)

print(f"\n✅ Saved flows with K8s metrics to: {output_path}")
print(f"   Shape: {flows.shape}")
print(f"   Columns: {flows.columns.tolist()}")
