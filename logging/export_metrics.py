"""
Export Real Metrics from Prometheus

This script connects to Prometheus and exports real metrics collected
during attack simulations. These metrics will be used to train the AI model.
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import os

# Prometheus configuration
PROMETHEUS_URL = "http://localhost:9090"

def query_prometheus(query, start_time, end_time, step='15s'):
    """
    Query Prometheus for metrics in a time range
    """
    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    
    params = {
        'query': query,
        'start': start_time.timestamp(),
        'end': end_time.timestamp(),
        'step': step
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error querying Prometheus: {e}")
        return None

def collect_metrics(duration_minutes=10):
    """
    Collect metrics from Prometheus
    """
    print("="*60)
    print("COLLECTING REAL METRICS FROM PROMETHEUS")
    print("="*60)
    
    # Check if Prometheus is accessible
    try:
        response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=5)
        print("✅ Prometheus is accessible!")
    except Exception as e:
        print("❌ Cannot connect to Prometheus!")
        print(f"   Error: {e}")
        print("\nMake sure port-forwarding is active:")
        print("   kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090")
        return None
    
    # Time range for queries
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=duration_minutes)
    
    print(f"\nCollecting metrics from:")
    print(f"  Start: {start_time}")
    print(f"  End: {end_time}")
    
    # Queries for different metrics
    queries = {
        'cpu_usage': 'rate(container_cpu_usage_seconds_total{pod=~"web-app.*"}[1m])',
        'memory_usage': 'container_memory_usage_bytes{pod=~"web-app.*"}',
        'network_receive': 'rate(container_network_receive_bytes_total{pod=~"web-app.*"}[1m])',
        'network_transmit': 'rate(container_network_transmit_bytes_total{pod=~"web-app.*"}[1m])',
        'pod_count': 'count(kube_pod_info{pod=~"web-app.*"})',
    }
    
    print("\nQuerying Prometheus...")
    all_data = []
    
    for metric_name, query in queries.items():
        print(f"  📊 {metric_name}...", end=" ")
        result = query_prometheus(query, start_time, end_time)
        
        if result and result.get('status') == 'success':
            data = result.get('data', {}).get('result', [])
            print(f"✅ ({len(data)} series)")
            
            # Process each time series
            for series in data:
                values = series.get('values', [])
                for timestamp, value in values:
                    all_data.append({
                        'timestamp': datetime.fromtimestamp(timestamp),
                        'metric': metric_name,
                        'value': float(value),
                        'pod': series.get('metric', {}).get('pod', 'unknown')
                    })
        else:
            print("❌ No data")
    
    if not all_data:
        print("\n❌ No metrics collected!")
        print("   Make sure:")
        print("   1. The web app is running (kubectl get pods)")
        print("   2. You ran the attack simulation")
        print("   3. Prometheus is scraping metrics")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    print(f"\n✅ Collected {len(df)} data points!")
    
    return df

def process_for_ml(df):
    """
    Process raw metrics into features for ML model
    """
    print("\nProcessing data for ML training...")
    
    # Group by time windows (30 seconds)
    df['time_window'] = df['timestamp'].dt.floor('30S')
    
    # Pivot to get features
    features = df.pivot_table(
        index='time_window',
        columns='metric',
        values='value',
        aggfunc='mean'
    ).reset_index()
    
    # Calculate additional features
    if 'cpu_usage' in features.columns:
        features['cpu_avg'] = features['cpu_usage']
    if 'memory_usage' in features.columns:
        features['memory_avg'] = features['memory_usage'] / (1024**3)  # Convert to GB
    if 'network_receive' in features.columns:
        features['network_receive_rate'] = features['network_receive']
    if 'network_transmit' in features.columns:
        features['network_transmit_rate'] = features['network_transmit']
    if 'pod_count' in features.columns:
        features['active_pods'] = features['pod_count']
    
    # Calculate requests per second (approximation from network traffic)
    if 'network_receive' in features.columns:
        features['requests_per_second'] = features['network_receive'] / 1024  # Rough estimate
    
    # Drop NaN values
    features = features.fillna(0)
    
    print(f"✅ Created {len(features)} feature rows")
    print(f"   Features: {list(features.columns)}")
    
    return features

def save_data(df):
    """
    Save collected data
    """
    os.makedirs('data', exist_ok=True)
    
    # Save raw data
    raw_path = 'data/raw_metrics.csv'
    df.to_csv(raw_path, index=False)
    print(f"\n✅ Raw data saved to: {raw_path}")
    
    # Process and save ML features
    features = process_for_ml(df)
    ml_path = 'data/real_attack_logs.csv'
    features.to_csv(ml_path, index=False)
    print(f"✅ ML features saved to: {ml_path}")
    
    # Show sample
    print("\n📊 Sample of collected data:")
    print(features.head())
    
    print("\n" + "="*60)
    print("Data collection completed!")
    print("="*60)
    print("\nNext steps:")
    print("  1. python ai-model/train_model_real_data.py")
    print("  2. python explainable-ai/explain_predictions.py")

def main():
    print("\n⚠️  IMPORTANT: Make sure Prometheus port-forwarding is active!")
    print("   Run in another terminal:")
    print("   kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090\n")
    
    input("Press Enter when Prometheus is accessible...")
    
    # Collect metrics
    df = collect_metrics(duration_minutes=10)
    
    if df is not None:
        # Save data
        save_data(df)

if __name__ == "__main__":
    main()
