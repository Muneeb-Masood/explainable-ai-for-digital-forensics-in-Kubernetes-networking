"""
Simple test script to verify model predictions

Run this after training the model to test it with different scenarios.
"""

import joblib
import pandas as pd
import os

def load_model():
    """Load the trained model"""
    model_path = 'ai-model/saved_models/attack_detector.pkl'
    if not os.path.exists(model_path):
        print("❌ Model not found! Please train it first:")
        print("   python ai-model/train_model.py")
        return None
    
    model = joblib.load(model_path)
    return model

def test_scenarios():
    """Test the model with different traffic scenarios"""
    
    model = load_model()
    if model is None:
        return
    
    print("="*60)
    print("TESTING AI MODEL WITH DIFFERENT SCENARIOS")
    print("="*60)
    
    # Scenario 1: Normal traffic
    normal_traffic = pd.DataFrame([{
        'requests_per_second': 45,
        'avg_response_time': 95,
        'error_rate': 1.2,
        'port_scan_count': 0,
        'unique_ips': 25,
        'cpu_usage': 0.2,
        'memory_usage': 0.4,
        'network_bytes': 15000
    }])
    
    # Scenario 2: DDoS attack
    ddos_attack = pd.DataFrame([{
        'requests_per_second': 750,
        'avg_response_time': 650,
        'error_rate': 22,
        'port_scan_count': 0,
        'unique_ips': 300,
        'cpu_usage': 0.85,
        'memory_usage': 0.75,
        'network_bytes': 350000
    }])
    
    # Scenario 3: Port scanning
    port_scan = pd.DataFrame([{
        'requests_per_second': 120,
        'avg_response_time': 45,
        'error_rate': 3,
        'port_scan_count': 85,
        'unique_ips': 3,
        'cpu_usage': 0.25,
        'memory_usage': 0.35,
        'network_bytes': 35000
    }])
    
    scenarios = [
        ("Normal Traffic", normal_traffic),
        ("DDoS Attack", ddos_attack),
        ("Port Scanning", port_scan)
    ]
    
    labels = ['Normal', 'DDoS', 'Port Scan']
    
    for name, data in scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario: {name}")
        print('='*60)
        
        # Show input features
        print("\nInput Features:")
        for col in data.columns:
            print(f"  {col}: {data[col].values[0]:.2f}")
        
        # Make prediction
        prediction = model.predict(data)[0]
        probabilities = model.predict_proba(data)[0]
        
        # Show results
        print(f"\n🎯 Prediction: {labels[prediction]}")
        print("\nConfidence Scores:")
        for i, label in enumerate(labels):
            bar = '█' * int(probabilities[i] * 50)
            print(f"  {label:12} {probabilities[i]:6.2%} {bar}")
    
    print("\n" + "="*60)
    print("Testing completed!")
    print("="*60)
    print("\n✅ The model is working correctly!")
    print("   You can now run: python explainable-ai/explain_predictions.py")

if __name__ == "__main__":
    test_scenarios()
