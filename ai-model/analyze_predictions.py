import pandas as pd
import numpy as np
import os
import sys

# Load predictions
prediction_file = 'ai-model/predictions_output.csv'
if not os.path.exists(prediction_file):
    prediction_file = 'predictions_output.csv'  # Fallback for direct script execution

if not os.path.exists(prediction_file):
    print(f"❌ Error: Could not find predictions file!")
    print(f"   Tried: ai-model/predictions_output.csv and predictions_output.csv")
    print(f"   Please run test_model.py first to generate predictions.")
    sys.exit(1)

df = pd.read_csv(prediction_file)

print("=" * 70)
print("PREDICTION ANALYSIS - 36 FEATURES (FLOW + K8S METRICS)")
print("=" * 70)

print(f"\nTotal flows analyzed: {len(df)}")

print("\n" + "=" * 70)
print("CLASS DISTRIBUTION")
print("=" * 70)
class_names = {
    0: "Normal",
    1: "Slowloris",
    2: "Torshammer/DoS",
    3: "Brute Force",
    4: "SQL Injection"
}

for cls in sorted(df['prediction'].unique()):
    count = (df['prediction'] == cls).sum()
    percentage = (count / len(df)) * 100
    bar = '█' * int(percentage / 2)
    print(f"Class {cls} ({class_names.get(cls, 'Unknown'):15s}): {count:5d} flows ({percentage:5.2f}%) {bar}")

print("\n" + "=" * 70)
print("AVERAGE CONFIDENCE PER PREDICTED CLASS")
print("=" * 70)
for cls in sorted(df['prediction'].unique()):
    prob_col = f'prob_class_{cls}'
    if prob_col in df.columns:
        subset = df[df['prediction'] == cls]
        avg_conf = subset[prob_col].mean()
        print(f"Class {cls} ({class_names.get(cls, 'Unknown'):15s}): {avg_conf:.4f} ({avg_conf*100:.2f}%)")

print("\n" + "=" * 70)
print("DETAILED PROBABILITY ANALYSIS FOR EACH CLASS")
print("=" * 70)
for i in range(5):
    prob_col = f'prob_class_{i}'
    if prob_col in df.columns:
        print(f"\nClass {i} ({class_names.get(i, 'Unknown'):15s}):")
        print(f"  Average probability across ALL flows: {df[prob_col].mean():.4f}")
        print(f"  Maximum probability observed:         {df[prob_col].max():.4f}")
        print(f"  Flows with probability > 0.3:         {(df[prob_col] > 0.3).sum()}")
        print(f"  Flows with probability > 0.5:         {(df[prob_col] > 0.5).sum()}")

print("\n" + "=" * 70)
print("TOP 10 FLOWS WITH HIGHEST PREDICTION CONFIDENCE")
print("=" * 70)

# Find the top 10 flows with highest confidence (max probability)
df['max_confidence'] = df[[col for col in df.columns if col.startswith('prob_class_')]].max(axis=1)
top10 = df.nlargest(10, 'max_confidence')

prob_cols = [col for col in df.columns if col.startswith('prob_class_')]
for idx, row in top10.iterrows():
    pred = int(row['prediction'])
    print(f"\nFlow {idx}: Predicted as Class {pred} ({class_names.get(pred, 'Unknown')}) - Confidence: {row['max_confidence']:.3f}")
    probs = ", ".join([f"C{i}={row[f'prob_class_{i}']:.3f}" for i in range(5) if f'prob_class_{i}' in row])
    print(f"  Probabilities: {probs}")

print("\n" + "=" * 70)
print("PROBABILITY DISTRIBUTION ACROSS ALL CLASSES")
print("=" * 70)
for i in range(5):
    col = f'prob_class_{i}'
    if col in df.columns:
        print(f"Class {i} ({class_names.get(i, 'Unknown'):15s}): mean={df[col].mean():.4f}, std={df[col].std():.4f}, max={df[col].max():.4f}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

# Check if K8s metrics are present
k8s_cols = [c for c in df.columns if c.startswith('container_')]
if k8s_cols:
    print("\n" + "=" * 70)
    print("KUBERNETES METRICS ANALYSIS")
    print("=" * 70)
    
    # Show K8s metrics for each predicted class
    for cls in sorted(df['prediction'].unique()):
        subset = df[df['prediction'] == cls]
        print(f"\n📊 Class {cls} ({class_names.get(cls, 'Unknown'):15s}) - {len(subset)} flows:")
        
        # CPU usage
        if 'container_cpu_usage_seconds_rate' in df.columns:
            cpu = subset['container_cpu_usage_seconds_rate'].mean()
            print(f"   CPU usage (avg):    {cpu:.6f}")
        
        # Memory usage
        if 'container_memory_usage_bytes' in df.columns:
            mem = subset['container_memory_usage_bytes'].mean()
            print(f"   Memory usage (avg): {mem/1024/1024:.2f} MB")
        
        # Memory working set
        if 'container_memory_working_set_bytes' in df.columns:
            mem_ws = subset['container_memory_working_set_bytes'].mean()
            print(f"   Memory working set: {mem_ws/1024/1024:.2f} MB")
    
    print(f"\n💡 Note: K8s metrics show container behavior during the attack.")
    print(f"   Network metrics are 0 (not available from kubectl top).")
else:
    print("\n⚠️  No Kubernetes metrics found in predictions.")
    print("   This might be an old prediction with only flow features.")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✅ Analyzed {len(df)} flows")
print(f"✅ Found {len(df['prediction'].unique())} different attack classes")
if k8s_cols:
    print(f"✅ Kubernetes metrics included in analysis")
print("\n")
