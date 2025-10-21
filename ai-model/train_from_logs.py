"""
Train AI Model from Attack Simulation Logs

This script trains the AI model using logs generated from
the simple attack simulation.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def load_logs():
    """Load simulation logs"""
    log_path = 'data/attack_simulation_logs.csv'
    
    if not os.path.exists(log_path):
        print("❌ Logs not found!")
        print("   Please run: python attack-simulation/simple_attack_with_logs.py")
        return None
    
    print(f"✅ Loading logs from: {log_path}")
    df = pd.read_csv(log_path)
    print(f"   Loaded {len(df)} log entries")
    
    return df

def prepare_features(df):
    """Prepare features for ML"""
    
    # Map attack types to labels
    label_map = {
        'Normal': 0,
        'DDoS': 1,
        'PortScan': 2
    }
    
    df['label'] = df['attack_type'].map(label_map)
    
    # Select features
    feature_columns = [
        'requests_per_second',
        'avg_response_time',
        'error_rate',
        'port_scan_count',
        'unique_ips',
        'cpu_usage',
        'memory_usage',
        'network_bytes'
    ]
    
    X = df[feature_columns]
    y = df['label']
    
    return X, y, feature_columns

def train_model():
    """Train the attack detection model"""
    
    print("="*60)
    print("TRAINING AI MODEL FROM SIMULATION LOGS")
    print("="*60)
    
    # Load logs
    df = load_logs()
    if df is None:
        return
    
    # Show distribution
    print("\n📊 Data Distribution:")
    for attack_type, count in df['attack_type'].value_counts().items():
        print(f"   {attack_type:12} : {count} samples")
    
    # Prepare features
    print("\n🔧 Preparing features...")
    X, y, feature_columns = prepare_features(df)
    
    print(f"   Features: {feature_columns}")
    print(f"   Total samples: {len(X)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # Train model
    print("\n🤖 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n📊 MODEL PERFORMANCE:")
    print("="*60)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.4f} ({train_score*100:.2f}%)")
    print(f"Test accuracy: {test_score:.4f} ({test_score*100:.2f}%)")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Classification report
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT:")
    print("="*60)
    print(classification_report(
        y_test, y_pred,
        target_names=['Normal', 'DDoS', 'Port Scan']
    ))
    
    # Confusion matrix
    print("CONFUSION MATRIX:")
    print("-"*60)
    cm = confusion_matrix(y_test, y_pred)
    print("                Predicted")
    print("                Normal  DDoS  PortScan")
    labels = ['Normal    ', 'DDoS      ', 'PortScan  ']
    for i, label in enumerate(labels):
        print(f"Actual {label}", end="")
        for j in range(3):
            print(f"{cm[i][j]:7d}", end="")
        print()
    
    # Feature importance
    print("\n" + "="*60)
    print("FEATURE IMPORTANCE:")
    print("="*60)
    print("(Which features the AI considers most important)\n")
    
    importance_pairs = sorted(
        zip(feature_columns, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    
    for feature, importance in importance_pairs:
        bar = '█' * int(importance * 50)
        print(f"{feature:25} {importance:.4f} {bar}")
    
    # Save model
    os.makedirs('ai-model/saved_models', exist_ok=True)
    model_path = 'ai-model/saved_models/attack_detector.pkl'
    joblib.dump(model, model_path)
    
    feature_path = 'ai-model/saved_models/feature_names.pkl'
    joblib.dump(feature_columns, feature_path)
    
    print("\n" + "="*60)
    print("✅ MODEL SAVED SUCCESSFULLY!")
    print("="*60)
    print(f"Model: {model_path}")
    print(f"Features: {feature_path}")
    
    print("\n🎯 Next steps:")
    print("  1. Test model: python ai-model/test_model.py")
    print("  2. Explain predictions: python explainable-ai/explain_predictions.py")
    print("  3. View logs: notepad data\\attack_simulation_logs.csv")

if __name__ == "__main__":
    train_model()
