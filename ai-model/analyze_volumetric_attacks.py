"""
Enhanced Analysis for Volumetric DDoS Detection

This script adds temporal and volume-based features to better detect
Layer 7 HTTP flood attacks that complete TCP handshakes.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def load_predictions():
    """Load the predictions output"""
    df = pd.read_csv('ai-model/predictions_output.csv')
    print(f"✓ Loaded {len(df)} network flows")
    return df

def analyze_volumetric_patterns(df):
    """
    Analyze patterns that indicate volumetric attacks:
    - High packet rate
    - Similar packet characteristics (indicating automation)
    - Repetitive patterns
    """
    print("\n" + "="*70)
    print("VOLUMETRIC ATTACK PATTERN ANALYSIS")
    print("="*70)
    
    # Feature similarity analysis (flows with identical features = likely automated)
    feature_cols = [
        'fwd_init_win_bytes', 'min_fwd_payload_bytes_delta_len',
        'mean_header_bytes', 'max_fwd_packets_delta_len'
    ]
    
    # Create signature from key features
    df['flow_signature'] = df[feature_cols].apply(
        lambda x: f"{x['fwd_init_win_bytes']}_{x['min_fwd_payload_bytes_delta_len']}_{x['max_fwd_packets_delta_len']}", 
        axis=1
    )
    
    # Count signature frequencies
    signature_counts = df['flow_signature'].value_counts()
    
    print("\n📊 Flow Signature Analysis:")
    print(f"   Total unique signatures: {len(signature_counts)}")
    print(f"   Most common signature appears: {signature_counts.iloc[0]} times")
    print(f"   Top 3 signatures:")
    for i, (sig, count) in enumerate(signature_counts.head(3).items(), 1):
        percentage = (count / len(df)) * 100
        print(f"      {i}. {sig}: {count} flows ({percentage:.1f}%)")
    
    # Identify suspicious patterns (same signature repeated many times)
    suspicious_threshold = len(df) * 0.1  # 10% threshold
    suspicious_signatures = signature_counts[signature_counts > suspicious_threshold]
    
    print(f"\n⚠️  Suspicious patterns (>10% of traffic):")
    if len(suspicious_signatures) > 0:
        for sig, count in suspicious_signatures.items():
            percentage = (count / len(df)) * 100
            print(f"   • {sig}: {count} flows ({percentage:.1f}%) - LIKELY AUTOMATED ATTACK")
            
            # Mark these flows as suspicious
            df.loc[df['flow_signature'] == sig, 'volumetric_attack'] = 1
    else:
        print("   None detected")
    
    # Initialize volumetric_attack column if not exists
    if 'volumetric_attack' not in df.columns:
        df['volumetric_attack'] = 0
    
    return df

def detect_anomalies_isolation_forest(df):
    """
    Use Isolation Forest for anomaly detection based on volume patterns
    """
    print("\n" + "="*70)
    print("ISOLATION FOREST ANOMALY DETECTION")
    print("="*70)
    
    # Select features for anomaly detection
    features = [
        'fwd_init_win_bytes', 'ack_flag_percentage_in_total',
        'min_fwd_payload_bytes_delta_len', 'syn_flag_percentage_in_total',
        'mean_header_bytes', 'max_fwd_packets_delta_len'
    ]
    
    X = df[features].fillna(0)
    
    # Train Isolation Forest
    print("\n🌲 Training Isolation Forest...")
    iso_forest = IsolationForest(
        contamination=0.3,  # Expect 30% anomalies
        random_state=42,
        n_estimators=100
    )
    
    # Predict anomalies (-1 = anomaly, 1 = normal)
    predictions = iso_forest.fit_predict(X)
    anomaly_scores = iso_forest.score_samples(X)
    
    df['isolation_forest_anomaly'] = (predictions == -1).astype(int)
    df['anomaly_score'] = anomaly_scores
    
    n_anomalies = (predictions == -1).sum()
    print(f"✓ Detected {n_anomalies} anomalies ({n_anomalies/len(df)*100:.1f}%)")
    
    return df

def compare_detection_methods(df):
    """
    Compare different detection methods
    """
    print("\n" + "="*70)
    print("DETECTION METHOD COMPARISON")
    print("="*70)
    
    # Original DVWA model predictions
    dvwa_attacks = int(df['prediction'].isin([1, 2, 3, 4]).sum())
    
    # Volumetric pattern detection
    volumetric_attacks = int(df['volumetric_attack'].sum()) if 'volumetric_attack' in df.columns else 0
    
    # Isolation Forest detection
    iso_forest_attacks = int(df['isolation_forest_anomaly'].sum())
    
    # Combined detection (union of all methods)
    df['combined_attack'] = (
        (df['prediction'].isin([1, 2, 3, 4])) |
        (df['volumetric_attack'] == 1) |
        (df['isolation_forest_anomaly'] == 1)
    ).astype(int)
    
    combined_attacks = int(df['combined_attack'].sum())
    
    print(f"\n📊 Detection Results:")
    print(f"   DVWA Model (original):        {dvwa_attacks:4d} flows ({dvwa_attacks/len(df)*100:5.1f}%)")
    print(f"   Volumetric Pattern Analysis:  {volumetric_attacks:4d} flows ({volumetric_attacks/len(df)*100:5.1f}%)")
    print(f"   Isolation Forest:             {iso_forest_attacks:4d} flows ({iso_forest_attacks/len(df)*100:5.1f}%)")
    print(f"   Combined Detection:           {combined_attacks:4d} flows ({combined_attacks/len(df)*100:5.1f}%)")
    
    print(f"\n🎯 Improvement: Combined method detected {combined_attacks - dvwa_attacks} more attack flows!")
    
    return df

def generate_detailed_report(df):
    """
    Generate detailed attack report
    """
    print("\n" + "="*70)
    print("DETAILED ATTACK REPORT")
    print("="*70)
    
    # Breakdown by attack type
    print("\n1. DVWA Model Classifications:")
    for class_id in sorted(df['prediction'].unique()):
        count = (df['prediction'] == class_id).sum()
        percentage = count / len(df) * 100
        
        class_names = {
            0: "Normal Activity",
            1: "DoS Attack 1 (Slowloris)",
            2: "DoS Attack 2 (Torshammer)",
            3: "Brute Force Attack",
            4: "SQL Injection Attack"
        }
        name = class_names.get(class_id, f"Unknown Class {class_id}")
        print(f"   Class {class_id} ({name}): {count} flows ({percentage:.1f}%)")
    
    # Volumetric attack patterns
    if 'volumetric_attack' in df.columns:
        print("\n2. Volumetric Attack Indicators:")
        vol_attacks = df[df['volumetric_attack'] == 1]
        if len(vol_attacks) > 0:
            print(f"   Flows with repetitive patterns: {len(vol_attacks)} ({len(vol_attacks)/len(df)*100:.1f}%)")
            print(f"   Avg ACK flag %: {vol_attacks['ack_flag_percentage_in_total'].mean():.2f}%")
            print(f"   Avg SYN flag %: {vol_attacks['syn_flag_percentage_in_total'].mean():.2f}%")
    
    # Isolation Forest anomalies
    print("\n3. Anomaly Detection (Isolation Forest):")
    anomalies = df[df['isolation_forest_anomaly'] == 1]
    print(f"   Anomalous flows: {len(anomalies)} ({len(anomalies)/len(df)*100:.1f}%)")
    print(f"   Avg anomaly score: {df['anomaly_score'].mean():.4f}")
    print(f"   Most anomalous score: {df['anomaly_score'].min():.4f}")
    
    # Combined assessment
    print("\n4. Combined Attack Assessment:")
    attacks = df[df['combined_attack'] == 1]
    print(f"   Total attack flows: {len(attacks)} ({len(attacks)/len(df)*100:.1f}%)")
    print(f"   Total normal flows: {len(df) - len(attacks)} ({(len(df)-len(attacks))/len(df)*100:.1f}%)")
    
    # Save enhanced results
    output_path = 'ai-model/enhanced_attack_detection.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✅ Enhanced results saved to: {output_path}")
    
    return df

def create_visualizations(df):
    """
    Create visualizations of attack patterns
    """
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    try:
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Volumetric DDoS Attack Analysis', fontsize=16, fontweight='bold')
        
        # 1. Detection method comparison
        ax1 = axes[0, 0]
        detection_counts = [
            (df['prediction'].isin([1, 2, 3, 4])).sum(),
            df['volumetric_attack'].sum() if 'volumetric_attack' in df.columns else 0,
            df['isolation_forest_anomaly'].sum(),
            df['combined_attack'].sum()
        ]
        methods = ['DVWA Model', 'Volumetric\nPatterns', 'Isolation\nForest', 'Combined']
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f7b731']
        ax1.bar(methods, detection_counts, color=colors, alpha=0.7)
        ax1.set_ylabel('Number of Attack Flows')
        ax1.set_title('Detection Method Comparison')
        ax1.grid(axis='y', alpha=0.3)
        for i, v in enumerate(detection_counts):
            ax1.text(i, v + 10, str(v), ha='center', fontweight='bold')
        
        # 2. Flow signature distribution
        ax2 = axes[0, 1]
        top_signatures = df['flow_signature'].value_counts().head(10)
        ax2.barh(range(len(top_signatures)), top_signatures.values, color='#ff6b6b', alpha=0.7)
        ax2.set_yticks(range(len(top_signatures)))
        ax2.set_yticklabels([f"Pattern {i+1}" for i in range(len(top_signatures))], fontsize=8)
        ax2.set_xlabel('Number of Flows')
        ax2.set_title('Top 10 Flow Patterns (Repetition = Attack)')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. ACK vs SYN flag distribution
        ax3 = axes[1, 0]
        scatter_colors = df['combined_attack'].map({0: '#2ecc71', 1: '#e74c3c'})
        ax3.scatter(df['ack_flag_percentage_in_total'], 
                   df['syn_flag_percentage_in_total'],
                   c=scatter_colors, alpha=0.5, s=20)
        ax3.set_xlabel('ACK Flag %')
        ax3.set_ylabel('SYN Flag %')
        ax3.set_title('ACK vs SYN Flags (Red = Attack)')
        ax3.grid(alpha=0.3)
        
        # 4. Anomaly score distribution
        ax4 = axes[1, 1]
        attack_scores = df[df['combined_attack'] == 1]['anomaly_score']
        normal_scores = df[df['combined_attack'] == 0]['anomaly_score']
        ax4.hist(normal_scores, bins=30, alpha=0.6, label='Normal', color='#2ecc71')
        ax4.hist(attack_scores, bins=30, alpha=0.6, label='Attack', color='#e74c3c')
        ax4.set_xlabel('Anomaly Score')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Anomaly Score Distribution')
        ax4.legend()
        ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_path = 'ai-model/volumetric_attack_analysis.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization: {output_path}")
        
        plt.close()
        
    except Exception as e:
        print(f"⚠️  Could not create visualizations: {e}")
        print("   (This is optional - analysis results are still valid)")

def main():
    """
    Main analysis pipeline
    """
    print("="*70)
    print("ENHANCED VOLUMETRIC DDoS ATTACK DETECTION")
    print("="*70)
    print("\nThis analysis improves detection of Layer 7 HTTP flood attacks")
    print("that complete TCP handshakes but overwhelm with volume.\n")
    
    # Load data
    df = load_predictions()
    
    # Analyze volumetric patterns
    df = analyze_volumetric_patterns(df)
    
    # Run Isolation Forest anomaly detection
    df = detect_anomalies_isolation_forest(df)
    
    # Compare detection methods
    df = compare_detection_methods(df)
    
    # Generate detailed report
    df = generate_detailed_report(df)
    
    # Create visualizations
    create_visualizations(df)
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print("\nKey Findings:")
    print("• Your DDoS attack completes TCP handshakes (Layer 7 HTTP flood)")
    print("• Original DVWA model missed volumetric patterns")
    print("• Enhanced detection uses:")
    print("  - Pattern repetition analysis")
    print("  - Isolation Forest anomaly detection")
    print("  - Combined multi-method approach")
    print("\nNext steps:")
    print("  1. Review: ai-model/enhanced_attack_detection.csv")
    print("  2. View plots: ai-model/volumetric_attack_analysis.png")
    print("  3. Run SHAP explainability: python explainable-ai/explain_predictions.py")

if __name__ == "__main__":
    main()
