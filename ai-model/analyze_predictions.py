import pandas as pd
import numpy as np

# Load predictions
df = pd.read_csv('predictions_output.csv')

print("=" * 60)
print("PREDICTION ANALYSIS FOR SQLi ATTACK CAPTURE")
print("=" * 60)

print(f"\nTotal flows analyzed: {len(df)}")

print("\n" + "=" * 60)
print("CLASS DISTRIBUTION")
print("=" * 60)
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
    print(f"Class {cls} ({class_names[cls]:15s}): {count:5d} flows ({percentage:5.2f}%)")

print("\n" + "=" * 60)
print("AVERAGE CONFIDENCE PER PREDICTED CLASS")
print("=" * 60)
for cls in sorted(df['prediction'].unique()):
    prob_col = f'prob_class_{cls}'
    subset = df[df['prediction'] == cls]
    avg_conf = subset[prob_col].mean()
    print(f"Class {cls} ({class_names[cls]:15s}): {avg_conf:.4f} ({avg_conf*100:.2f}%)")

print("\n" + "=" * 60)
print("CLASS 4 (SQLi) PROBABILITY ANALYSIS")
print("=" * 60)
print(f"Average Class 4 probability across ALL flows: {df['prob_class_4'].mean():.4f}")
print(f"Maximum Class 4 probability observed: {df['prob_class_4'].max():.4f}")
print(f"Flows with Class 4 probability > 0.3: {(df['prob_class_4'] > 0.3).sum()}")
print(f"Flows with Class 4 probability > 0.4: {(df['prob_class_4'] > 0.4).sum()}")

print("\n" + "=" * 60)
print("TOP 10 FLOWS WITH HIGHEST CLASS 4 (SQLi) PROBABILITY")
print("=" * 60)
top10_class4 = df.nlargest(10, 'prob_class_4')[['prediction', 'prob_class_0', 'prob_class_1', 'prob_class_2', 'prob_class_3', 'prob_class_4']]
for idx, row in top10_class4.iterrows():
    pred = int(row['prediction'])
    print(f"\nFlow {idx}: Predicted as Class {pred} ({class_names[pred]})")
    print(f"  Probabilities: C0={row['prob_class_0']:.3f}, C1={row['prob_class_1']:.3f}, C2={row['prob_class_2']:.3f}, C3={row['prob_class_3']:.3f}, C4={row['prob_class_4']:.3f}")

print("\n" + "=" * 60)
print("PROBABILITY DISTRIBUTION ACROSS ALL CLASSES")
print("=" * 60)
for i in range(5):
    col = f'prob_class_{i}'
    print(f"Class {i} ({class_names[i]:15s}): mean={df[col].mean():.4f}, std={df[col].std():.4f}, max={df[col].max():.4f}")

print("\n" + "=" * 60)
print("INTERPRETATION")
print("=" * 60)
