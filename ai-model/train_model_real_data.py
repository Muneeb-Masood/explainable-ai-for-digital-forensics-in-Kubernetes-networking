"""
Train AI Model Using Real Attack Data from Prometheus

This version uses REAL metrics collected from Kubernetes during actual
attack simulations instead of synthetic data.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def load_real_data():
    """
    Load real metrics collected from Prometheus
    """
    data_path = 'data/real_attack_logs.csv'
    
    if not os.path.exists(data_path):
        print("❌ Real data not found!")
        print("\nYou need to:")
        print("  1. Deploy Kubernetes cluster with Prometheus")
        print("  2. Run attack simulation")
        print("  3. Collect metrics: python logging/export_metrics.py")
        print("\nFor now, using synthetic data for demonstration...")
        return None
    
    print(f"✅ Loading real data from: {data_path}")
    df = pd.read_csv(data_path)
    
    print(f"   Loaded {len(df)} samples")
    print(f"   Features: {list(df.columns)}")
    
    return df

def label_data(df):
    """
    Label the data based on patterns
    
    Labels:
    - 0: Normal traffic
    - 1: DDoS attack
    - 2: Port scanning
    """
    print("\nLabeling data based on attack patterns...")
    
    # Simple labeling logic based on metrics
    # You can adjust these thresholds based on your observations
    
    labels = []
    for idx, row in df.iterrows():
        # High network traffic + high CPU = DDoS
        if row.get('requests_per_second', 0) > 100 and row.get('cpu_avg', 0) > 0.5:
            labels.append(1)  # DDoS
        # Low network but many connections = Port scan
        elif row.get('network_receive_rate', 0) < 10000 and row.get('active_pods', 2) > 5:
            labels.append(2)  # Port scan (if pods scaled up)
        else:
            labels.append(0)  # Normal
    
    df['label'] = labels
    
    print(f"   Normal traffic: {len(df[df['label']==0])}")
    print(f"   DDoS attacks: {len(df[df['label']==1])}")
    print(f"   Port scans: {len(df[df['label']==2])}")
    
    return df

def generate_synthetic_data():
    """
    Generate synthetic data if real data is not available
    """
    print("Generating synthetic data for demonstration...")
    
    data = []
    
    # Normal traffic
    for _ in range(5000):
        data.append({
            'cpu_avg': np.random.normal(0.2, 0.05),
            'memory_avg': np.random.normal(0.5, 0.1),
            'network_receive_rate': np.random.normal(50000, 10000),
            'network_transmit_rate': np.random.normal(45000, 9000),
            'requests_per_second': np.random.normal(50, 15),
            'active_pods': 2,
            'label': 0
        })
    
    # DDoS attacks
    for _ in range(2500):
        data.append({
            'cpu_avg': np.random.normal(0.8, 0.1),
            'memory_avg': np.random.normal(0.7, 0.15),
            'network_receive_rate': np.random.normal(500000, 100000),
            'network_transmit_rate': np.random.normal(450000, 90000),
            'requests_per_second': np.random.normal(500, 100),
            'active_pods': np.random.randint(5, 10),
            'label': 1
        })
    
    # Port scanning
    for _ in range(2500):
        data.append({
            'cpu_avg': np.random.normal(0.3, 0.1),
            'memory_avg': np.random.normal(0.4, 0.1),
            'network_receive_rate': np.random.normal(20000, 5000),
            'network_transmit_rate': np.random.normal(18000, 4500),
            'requests_per_second': np.random.normal(100, 30),
            'active_pods': 3,
            'label': 2
        })
    
    return pd.DataFrame(data)

def train_model():
    """
    Train the attack detection model on real data
    """
    print("="*60)
    print("TRAINING AI MODEL ON REAL ATTACK DATA")
    print("="*60)
    
    # Load real data
    df = load_real_data()
    
    # If no real data, use synthetic
    if df is None:
        df = generate_synthetic_data()
    else:
        # Label the real data
        df = label_data(df)
    
    print(f"\nTotal samples: {len(df)}")
    
    # Prepare features
    feature_columns = ['cpu_avg', 'memory_avg', 'network_receive_rate', 
                      'network_transmit_rate', 'requests_per_second', 'active_pods']
    
    # Make sure all features exist
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    
    X = df[feature_columns]
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n📊 Model Performance:")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"   Training accuracy: {train_score:.4f}")
    print(f"   Test accuracy: {test_score:.4f}")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Classification report
    print("\n" + "="*60)
    print("Classification Report:")
    print("="*60)
    print(classification_report(
        y_test, y_pred,
        target_names=['Normal', 'DDoS Attack', 'Port Scan']
    ))
    
    # Confusion matrix
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    print("\n" + "="*60)
    print("Feature Importance (What the AI looks at):")
    print("="*60)
    for feature, importance in sorted(
        zip(feature_columns, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    ):
        bar = '█' * int(importance * 50)
        print(f"  {feature:25} {importance:.4f} {bar}")
    
    # Save model
    os.makedirs('ai-model/saved_models', exist_ok=True)
    model_path = 'ai-model/saved_models/attack_detector_real.pkl'
    joblib.dump(model, model_path)
    print(f"\n✅ Model saved to: {model_path}")
    
    # Save feature names
    feature_path = 'ai-model/saved_models/feature_names_real.pkl'
    joblib.dump(feature_columns, feature_path)
    print(f"✅ Feature names saved to: {feature_path}")
    
    print("\n" + "="*60)
    print("🎉 Training completed successfully!")
    print("="*60)
    print("\nThis model was trained on:")
    if os.path.exists('data/real_attack_logs.csv'):
        print("  ✅ REAL metrics from Kubernetes & Prometheus")
    else:
        print("  ⚠️  Synthetic data (run real attacks to get better results)")
    
    print("\nNext steps:")
    print("  1. python ai-model/test_model.py")
    print("  2. python explainable-ai/explain_predictions.py")

if __name__ == "__main__":
    train_model()
