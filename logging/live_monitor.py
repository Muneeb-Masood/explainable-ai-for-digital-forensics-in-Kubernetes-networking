"""
Live Attack Monitor - Watch attacks in real-time

This script monitors Prometheus metrics in real-time and detects
attacks as they happen using the trained AI model.
"""

import requests
import time
import joblib
import pandas as pd
import os
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
CHECK_INTERVAL = 5  # Check every 5 seconds

def load_model():
    """Load the trained model"""
    model_path = 'ai-model/saved_models/attack_detector_real.pkl'
    feature_path = 'ai-model/saved_models/feature_names_real.pkl'
    
    if not os.path.exists(model_path):
        print("❌ Model not found! Train it first:")
        print("   python ai-model/train_model_real_data.py")
        return None, None
    
    model = joblib.load(model_path)
    features = joblib.load(feature_path)
    return model, features

def query_current_metrics():
    """Query current metrics from Prometheus"""
    
    queries = {
        'cpu_avg': 'rate(container_cpu_usage_seconds_total{pod=~"web-app.*"}[1m])',
        'memory_avg': 'container_memory_usage_bytes{pod=~"web-app.*"} / (1024*1024*1024)',
        'network_receive_rate': 'rate(container_network_receive_bytes_total{pod=~"web-app.*"}[1m])',
        'network_transmit_rate': 'rate(container_network_transmit_bytes_total{pod=~"web-app.*"}[1m])',
        'active_pods': 'count(kube_pod_info{pod=~"web-app.*"})',
    }
    
    metrics = {}
    
    for metric_name, query in queries.items():
        try:
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={'query': query},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {}).get('result', [])
                
                if data:
                    # Average across all pods
                    values = [float(d['value'][1]) for d in data]
                    metrics[metric_name] = sum(values) / len(values)
                else:
                    metrics[metric_name] = 0
            else:
                metrics[metric_name] = 0
                
        except Exception as e:
            metrics[metric_name] = 0
    
    # Estimate requests per second from network traffic
    metrics['requests_per_second'] = metrics.get('network_receive_rate', 0) / 1024
    
    return metrics

def monitor_live():
    """Monitor metrics in real-time and detect attacks"""
    
    print("="*60)
    print("LIVE ATTACK DETECTION MONITOR")
    print("="*60)
    
    # Load model
    model, feature_names = load_model()
    if model is None:
        return
    
    print("\n✅ Model loaded!")
    print(f"   Features: {feature_names}")
    
    # Check Prometheus connection
    try:
        response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=5)
        print("✅ Prometheus connected!")
    except Exception as e:
        print("❌ Cannot connect to Prometheus!")
        print("   Run: kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090")
        return
    
    print(f"\n🔍 Monitoring every {CHECK_INTERVAL} seconds...")
    print("   Press Ctrl+C to stop\n")
    print("-"*60)
    
    labels = ['✅ Normal', '🚨 DDoS ATTACK', '⚠️  Port Scan']
    
    try:
        while True:
            # Get current metrics
            metrics = query_current_metrics()
            
            # Prepare for prediction
            features_df = pd.DataFrame([metrics])[feature_names]
            
            # Predict
            prediction = model.predict(features_df)[0]
            probabilities = model.predict_proba(features_df)[0]
            
            # Display
            timestamp = datetime.now().strftime('%H:%M:%S')
            status = labels[prediction]
            confidence = probabilities[prediction]
            
            print(f"[{timestamp}] {status} (confidence: {confidence:.2%})")
            
            if prediction != 0:  # Attack detected!
                print(f"  📊 Metrics:")
                print(f"     CPU: {metrics['cpu_avg']:.2f}")
                print(f"     Requests/s: {metrics['requests_per_second']:.0f}")
                print(f"     Active Pods: {metrics['active_pods']:.0f}")
                print(f"     Network In: {metrics['network_receive_rate']:.0f} bytes/s")
                print()
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped!")

if __name__ == "__main__":
    monitor_live()
