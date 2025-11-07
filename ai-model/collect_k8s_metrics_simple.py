"""
Collect Kubernetes metrics directly from kubectl top command.
Works with Minikube's metrics-server.
"""

import subprocess
import pandas as pd
import time
from datetime import datetime
import json
import argparse

def get_pod_metrics():
    """Get pod metrics using kubectl top"""
    try:
        result = subprocess.run(
            ['kubectl', 'top', 'pods', '--all-namespaces', '--no-headers'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return []
        
        metrics = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 4:
                metrics.append({
                    'namespace': parts[0],
                    'pod': parts[1],
                    'cpu': parts[2],
                    'memory': parts[3]
                })
        return metrics
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return []

def parse_cpu(cpu_str):
    """Convert CPU string (e.g., '1m', '500m', '1') to millicores"""
    if cpu_str.endswith('m'):
        return float(cpu_str[:-1])
    return float(cpu_str) * 1000

def parse_memory(mem_str):
    """Convert memory string (e.g., '100Mi', '1Gi') to bytes"""
    mem_str = mem_str.strip()
    if mem_str.endswith('Mi'):
        return float(mem_str[:-2]) * 1024 * 1024
    elif mem_str.endswith('Gi'):
        return float(mem_str[:-2]) * 1024 * 1024 * 1024
    elif mem_str.endswith('Ki'):
        return float(mem_str[:-2]) * 1024
    return float(mem_str)

def collect_metrics(duration_sec, interval_sec, output_file):
    """Collect metrics continuously"""
    print(f"🔄 Collecting Kubernetes metrics for {duration_sec} seconds...")
    print(f"   Interval: {interval_sec}s")
    print(f"   Output: {output_file}")
    
    all_data = []
    start_time = time.time()
    iteration = 0
    
    while time.time() - start_time < duration_sec:
        iteration += 1
        timestamp = datetime.now()
        
        print(f"\n[{iteration}] Collecting at {timestamp.strftime('%H:%M:%S')}...")
        
        metrics = get_pod_metrics()
        
        if not metrics:
            print("   ⚠️  No metrics available yet")
        else:
            print(f"   Collected metrics from {len(metrics)} pods")
            
            for m in metrics:
                try:
                    all_data.append({
                        'timestamp': timestamp,
                        'namespace': m['namespace'],
                        'pod': m['pod'],
                        'container_cpu_usage_seconds_rate': parse_cpu(m['cpu']) / 1000,  # Convert to cores
                        'container_memory_usage_bytes': parse_memory(m['memory']),
                        'container_memory_working_set_bytes': parse_memory(m['memory'])  # Approximate
                    })
                except Exception as e:
                    print(f"   Error parsing metrics: {e}")
        
        time.sleep(interval_sec)
    
    if not all_data:
        print("\n❌ No metrics collected!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Add zero values for network metrics (not available from kubectl top)
    df['container_network_receive_bytes_rate'] = 0
    df['container_network_transmit_bytes_rate'] = 0
    df['container_network_receive_packets_rate'] = 0
    df['container_network_transmit_packets_rate'] = 0
    
    # Aggregate by timestamp (average across all pods)
    metric_cols = [c for c in df.columns if c.startswith('container_')]
    df_agg = df.groupby('timestamp')[metric_cols].mean().reset_index()
    
    # Save
    df_agg.to_csv(output_file, index=False)
    
    print(f"\n✅ Saved {len(df_agg)} rows to {output_file}")
    print(f"   Columns: {list(df_agg.columns)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect K8s metrics from kubectl")
    parser.add_argument("--duration", type=int, default=60, help="Collection duration in seconds")
    parser.add_argument("--interval", type=int, default=5, help="Collection interval in seconds")
    parser.add_argument("--output", default="ai-model/k8s_metrics.csv", help="Output CSV file")
    
    args = parser.parse_args()
    collect_metrics(args.duration, args.interval, args.output)
