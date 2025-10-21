"""
AI Model for Network Attack Detection

This script trains a machine learning model to detect network attacks
based on network traffic features.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def generate_sample_data(n_samples=10000):
    """
    Generate synthetic network traffic data for demonstration
    
    Features:
    - requests_per_second: Number of requests per second
    - unique_ips: Number of unique IP addresses
    - avg_response_time: Average response time
    - error_rate: Percentage of errors
    - port_scan_count: Number of port scan attempts
    - packet_size_avg: Average packet size
    
    Labels:
    - 0: Normal traffic
    - 1: DDoS attack
    - 2: Port scanning attack
    """
    
    print("Generating synthetic training data...")
    
    data = []
    
    # Normal traffic (50%)
    for _ in range(n_samples // 2):
        data.append({
            'requests_per_second': np.random.normal(50, 15),
            'unique_ips': np.random.normal(30, 10),
            'avg_response_time': np.random.normal(100, 20),
            'error_rate': np.random.normal(1, 0.5),
            'port_scan_count': np.random.normal(0, 1),
            'packet_size_avg': np.random.normal(500, 100),
            'label': 0  # Normal
        })
    
    # DDoS attack (25%)
    for _ in range(n_samples // 4):
        data.append({
            'requests_per_second': np.random.normal(500, 100),  # High
            'unique_ips': np.random.normal(200, 50),  # Many IPs
            'avg_response_time': np.random.normal(500, 100),  # Slow
            'error_rate': np.random.normal(15, 5),  # High errors
            'port_scan_count': np.random.normal(0, 1),
            'packet_size_avg': np.random.normal(300, 50),  # Small packets
            'label': 1  # DDoS
        })
    
    # Port scanning (25%)
    for _ in range(n_samples // 4):
        data.append({
            'requests_per_second': np.random.normal(100, 30),
            'unique_ips': np.random.normal(5, 2),  # Few IPs
            'avg_response_time': np.random.normal(50, 10),  # Fast
            'error_rate': np.random.normal(5, 2),
            'port_scan_count': np.random.normal(50, 15),  # High scan count
            'packet_size_avg': np.random.normal(100, 20),  # Very small
            'label': 2  # Port scan
        })
    
    df = pd.DataFrame(data)
    return df

def train_model():
    """
    Train the attack detection model
    """
    print("="*60)
    print("TRAINING AI MODEL FOR ATTACK DETECTION")
    print("="*60)
    
    # Generate data
    df = generate_sample_data(10000)
    print(f"\nDataset size: {len(df)}")
    print(f"Normal traffic: {len(df[df['label']==0])}")
    print(f"DDoS attacks: {len(df[df['label']==1])}")
    print(f"Port scans: {len(df[df['label']==2])}")
    
    # Prepare features and labels
    X = df.drop('label', axis=1)
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train Random Forest model
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=['Normal', 'DDoS', 'Port Scan']
    ))
    
    # Confusion matrix
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    print("\nFeature Importance:")
    for feature, importance in zip(X.columns, model.feature_importances_):
        print(f"  {feature}: {importance:.4f}")
    
    # Save model
    os.makedirs('ai-model/saved_models', exist_ok=True)
    model_path = 'ai-model/saved_models/attack_detector.pkl'
    joblib.dump(model, model_path)
    print(f"\n✅ Model saved to: {model_path}")
    
    # Save feature names
    feature_path = 'ai-model/saved_models/feature_names.pkl'
    joblib.dump(list(X.columns), feature_path)
    print(f"✅ Feature names saved to: {feature_path}")
    
    print("\n" + "="*60)
    print("Training completed successfully!")
    print("="*60)

if __name__ == "__main__":
    train_model()
