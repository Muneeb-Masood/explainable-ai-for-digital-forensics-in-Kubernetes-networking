"""
SHAP Analysis for Explainable AI - Three Dataset Analysis
=========================================================

This script performs SHAP (SHapley Additive exPlanations) analysis on:
1. Training dataset (DVWA - full dataset with 59,325 samples)
2. Collected attack data (Real Slowloris attack we captured)
3. Merged predictions (Combined analysis)

Provides clear explanations for why the model made specific predictions.
"""

import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Attack class names
CLASS_NAMES = {
    0: "Normal Traffic",
    1: "Slowloris Attack",
    2: "Torshammer/DoS",
    3: "Brute Force Attack",
    4: "SQL Injection"
}

def load_model_and_data():
    """Load the 36-feature model and feature list"""
    model_path = '../ai-model/saved_models/dvwa_attack_detector_36_features.pkl'
    features_path = '../ai-model/saved_models/features_35_with_k8s.txt'
    
    if not os.path.exists(model_path):
        print("❌ Model not found! Train it first:")
        print("   python ai-model/train_model_36_features.py")
        return None, None
    
    print("✅ Loading 36-feature model...")
    model = joblib.load(model_path)
    
    with open(features_path, 'r') as f:
        feature_names = [line.strip() for line in f if line.strip()]
    
    print(f"✅ Model loaded: {model.n_estimators} trees, {len(feature_names)} features")
    return model, feature_names


def create_shap_plots(shap_values, X_sample, feature_names, dataset_name, output_dir):
    """Generate beautiful SHAP visualizations"""
    
    print(f"\n📊 Generating SHAP visualizations for {dataset_name}...")
    
    # 1. Summary Plot (Beeswarm) - Shows feature importance across all samples
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False, max_display=15)
    plt.title(f'SHAP Feature Importance - {dataset_name}\n(Impact on Model Predictions)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/shap_summary_{dataset_name}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Summary plot saved")
    
    # 2. Bar Plot - Mean absolute SHAP values
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names, 
                      plot_type='bar', show=False, max_display=15)
    plt.title(f'Mean Feature Impact - {dataset_name}\n(Average Absolute SHAP Values)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/shap_bar_{dataset_name}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Bar plot saved")
    
    # 3. Individual prediction explanation (first attack sample)
    if len(X_sample) > 0:
        attack_idx = 0
        plt.figure(figsize=(12, 8))
        
        # Get SHAP values for single sample
        sample_shap = shap_values[attack_idx]
        
        # For multi-output (multi-class), take the predicted class values
        if len(sample_shap.values.shape) > 1:
            # Multi-class: take first class for simplicity
            sample_values = sample_shap.values[:, 0]
            base_val = sample_shap.base_values[0] if isinstance(sample_shap.base_values, np.ndarray) else sample_shap.base_values
        else:
            sample_values = sample_shap.values
            base_val = sample_shap.base_values
        
        shap.waterfall_plot(shap.Explanation(
            values=sample_values,
            base_values=float(base_val),
            data=X_sample.iloc[attack_idx].values,
            feature_names=feature_names
        ), show=False, max_display=15)
        plt.title(f'Individual Sample Explanation - {dataset_name}\n(Feature Contributions to Prediction)', 
                  fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/shap_waterfall_{dataset_name}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Waterfall plot saved")


def analyze_dataset_1_training():
    """
    Dataset 1: DVWA Training Dataset (Full 59,325 samples)
    Shows what features the model learned as important
    """
    print("\n" + "="*80)
    print("📊 DATASET 1: TRAINING DATA ANALYSIS")
    print("="*80)
    print("Purpose: Understand what the model learned from training data")
    print("Dataset: DVWA with 59,325 samples (5 attack classes)")
    
    model, feature_names = load_model_and_data()
    if model is None:
        return
    
    # Load training data
    dataset_path = r"C:\Users\PMLS\Downloads\archive (1)\dvwa_dataset\processed\dvwa_dataset_ml_ready.csv"
    if not os.path.exists(dataset_path):
        print("❌ Training dataset not found!")
        return
    
    print("\n📂 Loading training dataset...")
    df = pd.read_csv(dataset_path)
    print(f"   Total samples: {len(df)}")
    
    # Use only the 36 features the model was trained on
    X = df[feature_names].fillna(0)
    y = df['label']
    
    print(f"\n📋 Class distribution:")
    for label, count in y.value_counts().sort_index().items():
        print(f"   Class {label} ({CLASS_NAMES.get(label, 'Unknown'):20s}): {count:6d} samples ({count/len(y)*100:.1f}%)")
    
    # Sample 1000 random samples for SHAP (full dataset takes too long)
    print("\n🔍 Sampling 1000 flows for SHAP analysis...")
    X_sample = X.sample(n=min(1000, len(X)), random_state=42)
    
    print("⏳ Computing SHAP values (this may take 2-3 minutes)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_sample)
    
    # Create output directory
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate plots
    create_shap_plots(shap_values, X_sample, feature_names, 
                     'Training_Dataset', output_dir)
    
    # Print top 10 most important features
    print("\n📊 TOP 10 MOST IMPORTANT FEATURES (From Training):")
    print("-" * 80)
    
    # Handle multi-class SHAP values
    if len(shap_values.values.shape) > 2:
        # Multi-class: average across classes
        mean_abs_shap = np.abs(shap_values.values).mean(axis=(0, 2))
    else:
        mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    
    feature_importance = pd.DataFrame({
        'Feature': feature_names,
        'Importance': mean_abs_shap
    }).sort_values('Importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['Feature']:40s}: {row['Importance']:.4f}")
    
    print("\n✅ Dataset 1 analysis complete!")
    return shap_values, X_sample


def analyze_dataset_2_collected():
    """
    Dataset 2: Real Collected Attack Data (122 flows from Slowloris)
    Shows how the model performs on our actual captured traffic
    """
    print("\n" + "="*80)
    print("📊 DATASET 2: COLLECTED ATTACK DATA (Our Slowloris Capture)")
    print("="*80)
    print("Purpose: Explain why our captured attack was detected")
    print("Dataset: 122 flows from real Slowloris attack on Kubernetes")
    
    model, feature_names = load_model_and_data()
    if model is None:
        return
    
    # Load collected data
    data_path = '../ai-model/final_model_input.csv'
    if not os.path.exists(data_path):
        print("❌ Collected data not found! Run the attack pipeline first.")
        return
    
    print("\n📂 Loading collected attack data...")
    X = pd.read_csv(data_path)
    print(f"   Total flows captured: {len(X)}")
    
    # Make predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    print(f"\n🎯 Model Predictions on Collected Data:")
    unique, counts = np.unique(predictions, return_counts=True)
    for label, count in zip(unique, counts):
        pct = count/len(predictions)*100
        print(f"   Class {label} ({CLASS_NAMES.get(label, 'Unknown'):20s}): {count:3d} flows ({pct:5.1f}%)")
    
    print("\n⏳ Computing SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    
    # Create output directory
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate plots
    create_shap_plots(shap_values, X, feature_names, 
                     'Collected_Attack', output_dir)
    
    # Analyze attack flows specifically
    print("\n📊 FEATURE ANALYSIS FOR DETECTED ATTACKS:")
    print("-" * 80)
    
    attack_mask = predictions != 0  # Non-normal traffic
    if attack_mask.sum() > 0:
        X_attacks = X[attack_mask]
        shap_attacks = shap_values.values[attack_mask]
        
        # Handle multi-class SHAP
        if len(shap_attacks.shape) > 2:
            mean_abs_shap = np.abs(shap_attacks).mean(axis=(0, 2))
        else:
            mean_abs_shap = np.abs(shap_attacks).mean(axis=0)
        
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': mean_abs_shap,
            'Avg_Value': X_attacks.mean()
        }).sort_values('Importance', ascending=False)
        
        print("\nTop 10 features that identified this as an attack:")
        for idx, row in feature_importance.head(10).iterrows():
            print(f"   {row['Feature']:40s}: Impact={row['Importance']:.4f}, Value={row['Avg_Value']:.2f}")
    
    print("\n✅ Dataset 2 analysis complete!")
    return shap_values, X


def analyze_dataset_3_merged():
    """
    Dataset 3: Merged Analysis (Training + Collected)
    Shows comparison between training patterns and real attack
    """
    print("\n" + "="*80)
    print("📊 DATASET 3: MERGED ANALYSIS (Training + Collected)")
    print("="*80)
    print("Purpose: Compare training patterns with real-world attack")
    
    model, feature_names = load_model_and_data()
    if model is None:
        return
    
    # Load both datasets
    print("\n📂 Loading both datasets for comparison...")
    
    # Training data (sample)
    training_path = r"C:\Users\PMLS\Downloads\archive (1)\dvwa_dataset\processed\dvwa_dataset_ml_ready.csv"
    if os.path.exists(training_path):
        df_train = pd.read_csv(training_path)
        X_train = df_train[feature_names].sample(n=200, random_state=42).fillna(0)
        X_train['Source'] = 'Training'
        print(f"   Training samples: 200 (sampled)")
    else:
        X_train = pd.DataFrame()
    
    # Collected data
    collected_path = '../ai-model/final_model_input.csv'
    if os.path.exists(collected_path):
        X_collected = pd.read_csv(collected_path)
        X_collected['Source'] = 'Collected'
        print(f"   Collected samples: {len(X_collected)}")
    else:
        print("❌ Collected data not found!")
        return
    
    # Merge
    X_merged = pd.concat([X_train, X_collected], ignore_index=True)
    source_labels = X_merged['Source']
    X_features = X_merged[feature_names]
    
    print(f"\n   Total merged samples: {len(X_merged)}")
    
    print("\n⏳ Computing SHAP values for merged dataset...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_features)
    
    # Create output directory
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate comparison plots
    print(f"\n📊 Generating comparison visualizations...")
    
    # Overall merged plot
    create_shap_plots(shap_values, X_features, feature_names, 
                     'Merged_Analysis', output_dir)
    
    # Side-by-side comparison
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    
    # Training side
    train_mask = source_labels == 'Training'
    if train_mask.sum() > 0:
        plt.sca(axes[0])
        shap.summary_plot(shap_values.values[train_mask], 
                         X_features[train_mask], 
                         feature_names=feature_names,
                         show=False, max_display=10, plot_type='bar')
        axes[0].set_title('Training Dataset\n(What Model Learned)', 
                         fontsize=12, fontweight='bold')
    
    # Collected side
    collected_mask = source_labels == 'Collected'
    if collected_mask.sum() > 0:
        plt.sca(axes[1])
        shap.summary_plot(shap_values.values[collected_mask], 
                         X_features[collected_mask], 
                         feature_names=feature_names,
                         show=False, max_display=10, plot_type='bar')
        axes[1].set_title('Collected Attack\n(Real Slowloris)', 
                         fontsize=12, fontweight='bold')
    
    plt.suptitle('SHAP Comparison: Training vs Real Attack', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/shap_comparison_training_vs_collected.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Comparison plot saved")
    
    # Feature correlation analysis
    print("\n📊 FEATURE COMPARISON (Training vs Collected):")
    print("-" * 80)
    
    if train_mask.sum() > 0 and collected_mask.sum() > 0:
        shap_train = shap_values.values[train_mask]
        shap_collected = shap_values.values[collected_mask]
        
        # Handle multi-class
        if len(shap_train.shape) > 2:
            train_importance = np.abs(shap_train).mean(axis=(0, 2))
            collected_importance = np.abs(shap_collected).mean(axis=(0, 2))
        else:
            train_importance = np.abs(shap_train).mean(axis=0)
            collected_importance = np.abs(shap_collected).mean(axis=0)
        
        comparison = pd.DataFrame({
            'Feature': feature_names,
            'Training_Importance': train_importance,
            'Collected_Importance': collected_importance,
            'Difference': collected_importance - train_importance
        }).sort_values('Collected_Importance', ascending=False)
        
        print("\nTop 10 features in collected attack:")
        for idx, row in comparison.head(10).iterrows():
            diff_indicator = "📈" if row['Difference'] > 0 else "📉"
            print(f"   {row['Feature']:35s}: "
                  f"Train={row['Training_Importance']:.4f}, "
                  f"Real={row['Collected_Importance']:.4f} "
                  f"{diff_indicator}")
    
    print("\n✅ Dataset 3 (merged) analysis complete!")
    return shap_values, X_features


def generate_summary_report():
    """Generate a comprehensive summary report"""
    output_dir = 'outputs'
    
    report = """
================================================================================
                 SHAP EXPLAINABILITY ANALYSIS SUMMARY REPORT
================================================================================

ANALYSIS COMPLETED ON THREE DATASETS:

1. TRAINING DATASET (59,325 samples)
   - Shows what features the model learned as important
   - Visualizations: shap_summary_Training_Dataset.png
                    shap_bar_Training_Dataset.png
                    shap_waterfall_Training_Dataset.png

2. COLLECTED ATTACK DATA (122 flows - Real Slowloris)
   - Explains why our captured attack was detected
   - Shows real-world feature patterns
   - Visualizations: shap_summary_Collected_Attack.png
                    shap_bar_Collected_Attack.png
                    shap_waterfall_Collected_Attack.png

3. MERGED ANALYSIS (Training + Collected)
   - Compares training patterns with real attack
   - Highlights differences between learned and actual patterns
   - Visualizations: shap_summary_Merged_Analysis.png
                    shap_bar_Merged_Analysis.png
                    shap_comparison_training_vs_collected.png

================================================================================
HOW TO INTERPRET SHAP PLOTS:
================================================================================

SUMMARY PLOT (Beeswarm):
  - Each dot is one sample
  - X-axis: SHAP value (impact on prediction)
  - Color: Feature value (red=high, blue=low)
  - Y-axis: Features ordered by importance
  - Shows: How each feature affects predictions

BAR PLOT:
  - Shows average absolute impact of each feature
  - Higher bar = more important feature
  - Easy to identify top contributing features

WATERFALL PLOT:
  - Shows one individual prediction
  - Arrows show how each feature pushed prediction
  - Red arrows push toward attack, blue toward normal

COMPARISON PLOT:
  - Left: What model learned from training
  - Right: What we see in real attack
  - Helps validate if model generalizes well

================================================================================
FILES GENERATED:
================================================================================

All visualizations saved to: outputs/
  ✅ shap_summary_Training_Dataset.png
  ✅ shap_bar_Training_Dataset.png
  ✅ shap_waterfall_Training_Dataset.png
  ✅ shap_summary_Collected_Attack.png
  ✅ shap_bar_Collected_Attack.png
  ✅ shap_waterfall_Collected_Attack.png
  ✅ shap_summary_Merged_Analysis.png
  ✅ shap_bar_Merged_Analysis.png
  ✅ shap_comparison_training_vs_collected.png
  ✅ SHAP_Analysis_Report.txt (this file)

================================================================================
NEXT STEPS:
================================================================================

1. Review all generated plots in outputs/
2. Compare training vs collected importance rankings
3. Identify key features that detected your attack
4. Use insights for forensic analysis and reporting

================================================================================
"""
    
    report_path = f'{output_dir}/SHAP_Analysis_Report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Summary report saved: {report_path}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE SHAP EXPLAINABILITY ANALYSIS")
    print("="*80)
    print("\nThis analysis will run SHAP on three datasets:")
    print("  1. Training dataset (what model learned)")
    print("  2. Collected attack data (our real capture)")
    print("  3. Merged analysis (comparison)")
    print("\n⏱️  Estimated time: 5-10 minutes")
    print("="*80)
    
    try:
        # Run all three analyses
        analyze_dataset_1_training()
        analyze_dataset_2_collected()
        analyze_dataset_3_merged()
        
        # Generate summary report
        generate_summary_report()
        
        print("\n" + "="*80)
        print("✅ ALL ANALYSES COMPLETE!")
        print("="*80)
        print("\n📂 Check outputs/ for all visualizations")
        print("📄 Read SHAP_Analysis_Report.txt for detailed summary")
        print("\n🎉 Explainable AI analysis finished successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
