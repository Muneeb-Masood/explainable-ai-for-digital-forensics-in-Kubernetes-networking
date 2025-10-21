"""
Explainable AI for Attack Detection

This script uses SHAP (SHapley Additive exPlanations) to explain
why the AI model predicted certain network traffic as an attack.
This is crucial for digital forensics.
"""

import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os

def load_model():
    """
    Load the trained model
    """
    model_path = 'ai-model/saved_models/attack_detector.pkl'
    feature_path = 'ai-model/saved_models/feature_names.pkl'
    
    if not os.path.exists(model_path):
        print("❌ Model not found! Please train the model first:")
        print("   python ai-model/train_model.py")
        return None, None
    
    model = joblib.load(model_path)
    feature_names = joblib.load(feature_path)
    
    return model, feature_names

def generate_test_sample():
    """
    Generate a sample that looks like a DDoS attack
    """
    sample = pd.DataFrame([{
        'requests_per_second': 600,  # Very high
        'avg_response_time': 550,  # Slow response
        'error_rate': 18,  # High error rate
        'port_scan_count': 0,  # No port scanning
        'unique_ips': 250,  # Many different IPs
        'cpu_usage': 0.80,  # High CPU
        'memory_usage': 0.70,  # High memory
        'network_bytes': 280000  # High network traffic
    }])
    
    return sample

def explain_prediction(model, feature_names, sample):
    """
    Use SHAP to explain the model's prediction
    """
    print("="*60)
    print("EXPLAINABLE AI - ATTACK DETECTION FORENSICS")
    print("="*60)
    
    # Align sample columns to model feature names
    sample = sample[feature_names]

    # Make prediction
    prediction = model.predict(sample)[0]
    prediction_proba = model.predict_proba(sample)[0]
    
    labels = ['Normal', 'DDoS Attack', 'Port Scan']
    
    print("\n📊 PREDICTION RESULTS:")
    print(f"Predicted class: {labels[prediction]}")
    print("\nConfidence scores:")
    for i, label in enumerate(labels):
        print(f"  {label}: {prediction_proba[i]:.2%}")
    
    # Create SHAP explainer
    print("\n🔍 Generating SHAP explanations...")
    print("(This may take a moment...)")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)

    # Display feature contributions
    print("\n📋 FEATURE CONTRIBUTIONS (Why this was detected as an attack):")
    print("-" * 60)

    # Handle SHAP values format (can be array or list of arrays)
    if isinstance(shap_values, list):
        # Multi-class: get values for predicted class, shape: (n_features,)
        class_shap_values = shap_values[prediction][0]
        base_value = explainer.expected_value[prediction]
    else:
        # Binary/single output, shape: (n_features,)
        class_shap_values = shap_values[0]
        base_value = explainer.expected_value if not isinstance(explainer.expected_value, list) else explainer.expected_value[0]

    # For the predicted class
    feature_impacts = []
    for i, feature in enumerate(feature_names):
        impact_val = class_shap_values[i]
        try:
            impact = float(impact_val)
        except Exception:
            arr = np.array(impact_val, dtype=float).ravel()
            impact = float(arr[0] if arr.size > 0 else 0.0)
        feature_impacts.append((feature, impact, float(sample[feature].values[0])))
    
    # Sort by absolute impact
    feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for feature, impact, value in feature_impacts:
        direction = "increases" if impact > 0 else "decreases"
        print(f"\n  Feature: {feature}")
        print(f"    Value: {value:.2f}")
        print(f"    Impact: {impact:+.4f} ({direction} likelihood of {labels[prediction]})")
    
    print("\n" + "="*60)
    print("📝 FORENSIC INTERPRETATION:")
    print("="*60)
    
    if prediction == 1:  # DDoS
        print("""
This traffic was classified as a DDoS ATTACK because:
  
  1. EXTREMELY HIGH request rate - Far above normal baseline
  2. MANY UNIQUE IP addresses - Distributed attack pattern
  3. HIGH ERROR RATE - System struggling under load
  4. SLOW RESPONSE TIMES - Server overwhelmed
  5. SMALL PACKET SIZES - Typical of flood attacks
  
🔍 Forensic Recommendation:
  - Collect all IP addresses for further investigation
  - Check firewall logs for geographic distribution
  - Examine timestamps for attack patterns
  - Preserve logs as evidence
        """)
    
    # Save explanation plots
    print("\n📈 Generating visualization...")
    os.makedirs('explainable-ai/outputs', exist_ok=True)

    # Summary (bar) plot for single sample
    plt.figure(figsize=(10, 6))
    shap.summary_plot(np.array([class_shap_values]), np.array(sample), feature_names=feature_names, show=False, plot_type='bar')
    plt.title(f'SHAP Feature Impact - {labels[prediction]}')
    plt.tight_layout()
    plt.savefig('explainable-ai/outputs/shap_explanation.png', dpi=300, bbox_inches='tight')
    print("✅ Visualization saved to: explainable-ai/outputs/shap_explanation.png")

    # Waterfall plot disabled for multi-output SHAP instability in some setups.
    # Uncomment below if needed and SHAP shapes are correct for your environment.
    # plt.figure(figsize=(10, 6))
    # shap.waterfall_plot(shap.Explanation(
    #     values=np.array(class_shap_values).ravel(),
    #     base_values=float(np.array(base_value).reshape(-1)[0]),
    #     data=np.array(sample.values[0]).ravel(),
    #     feature_names=feature_names
    # ), show=False)
    # plt.tight_layout()
    # plt.savefig('explainable-ai/outputs/shap_waterfall.png', dpi=300, bbox_inches='tight')
    # print("✅ Waterfall plot saved to: explainable-ai/outputs/shap_waterfall.png")
    
    print("\n" + "="*60)
    print("Explanation completed successfully!")
    print("="*60)

def main():
    # Load model
    model, feature_names = load_model()
    if model is None:
        return
    
    print("\n✅ Model loaded successfully!\n")
    
    # Generate test sample
    print("Generating test sample (simulated attack traffic)...\n")
    sample = generate_test_sample()
    
    print("Sample features:")
    for col in sample.columns:
        print(f"  {col}: {sample[col].values[0]:.2f}")
    
    print()
    
    # Explain prediction
    explain_prediction(model, feature_names, sample)

if __name__ == "__main__":
    main()
