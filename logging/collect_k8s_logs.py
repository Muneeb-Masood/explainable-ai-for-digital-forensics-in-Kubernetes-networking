"""
Collect Logs from Kubernetes Cluster

This script collects metrics and logs from Kubernetes pods during/after attacks.
It creates CSV files that can be used to train the AI model.
"""

import subprocess
import json
import csv
import time
from datetime import datetime
import os

def run_kubectl_command(command):
    """Run kubectl command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def get_pod_metrics():
    """Get CPU and memory metrics for pods"""
    print("📊 Collecting pod metrics...")
    
    output = run_kubectl_command("kubectl top pods --no-headers")
    if not output:
        print("  ⚠ No metrics available yet")
        print("  Wait a minute for metrics to populate, then try again")
        return []
    
    metrics = []
    for line in output.strip().split('\n'):
        if line:
            parts = line.split()
            if len(parts) >= 3:
                metrics.append({
                    'pod_name': parts[0],
                    'cpu': parts[1],
                    'memory': parts[2]
                })
    
    print(f"  ✓ Collected metrics for {len(metrics)} pods")
    return metrics

def get_pod_logs(pod_name, lines=100):
    """Get logs from a specific pod"""
    print(f"📝 Collecting logs from {pod_name}...")
    
    output = run_kubectl_command(f"kubectl logs {pod_name} --tail={lines}")
    return output if output else ""

def get_hpa_status():
    """Get Horizontal Pod Autoscaler status"""
    print("📈 Collecting HPA status...")
    
    output = run_kubectl_command("kubectl get hpa -o json")
    if not output:
        return None
    
    try:
        hpa_data = json.loads(output)
        if hpa_data.get('items'):
            hpa = hpa_data['items'][0]
            status = {
                'name': hpa['metadata']['name'],
                'current_replicas': hpa['status'].get('currentReplicas', 0),
                'desired_replicas': hpa['status'].get('desiredReplicas', 0),
                'current_cpu': hpa['status'].get('currentCPUUtilizationPercentage', 0),
                'target_cpu': hpa['spec']['metrics'][0]['resource']['target']['averageUtilization']
            }
            print(f"  ✓ Current replicas: {status['current_replicas']}")
            return status
    except Exception as e:
        print(f"  ⚠ Error parsing HPA data: {e}")
    
    return None

def get_pod_events():
    """Get recent events (scaling, errors, etc.)"""
    print("📋 Collecting events...")
    
    output = run_kubectl_command("kubectl get events --sort-by='.lastTimestamp' -o json")
    if not output:
        return []
    
    try:
        events_data = json.loads(output)
        events = []
        
        for event in events_data.get('items', [])[-50:]:  # Last 50 events
            events.append({
                'time': event.get('lastTimestamp', ''),
                'type': event.get('type', ''),
                'reason': event.get('reason', ''),
                'message': event.get('message', ''),
                'object': event.get('involvedObject', {}).get('name', '')
            })
        
        print(f"  ✓ Collected {len(events)} events")
        return events
    except Exception as e:
        print(f"  ⚠ Error parsing events: {e}")
    
    return []

def collect_all_data():
    """Collect all data and save to files"""
    print("="*70)
    print("COLLECTING KUBERNETES LOGS AND METRICS")
    print("="*70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('data/k8s_logs', exist_ok=True)
    
    # Collect pod metrics
    pod_metrics = get_pod_metrics()
    
    if pod_metrics:
        metrics_file = f'data/k8s_logs/pod_metrics_{timestamp}.csv'
        with open(metrics_file, 'w', newline='') as f:
            if pod_metrics:
                writer = csv.DictWriter(f, fieldnames=['pod_name', 'cpu', 'memory'])
                writer.writeheader()
                writer.writerows(pod_metrics)
        print(f"\n✓ Pod metrics saved to: {metrics_file}")
    
    # Collect HPA status
    hpa_status = get_hpa_status()
    if hpa_status:
        hpa_file = f'data/k8s_logs/hpa_status_{timestamp}.json'
        import json as json_module
        with open(hpa_file, 'w') as f:
            json_module.dump(hpa_status, f, indent=2)
        print(f"✓ HPA status saved to: {hpa_file}")
    
    # Collect events
    events = get_pod_events()
    if events:
        events_file = f'data/k8s_logs/events_{timestamp}.csv'
        with open(events_file, 'w', newline='', encoding='utf-8') as f:
            if events:
                writer = csv.DictWriter(f, fieldnames=['time', 'type', 'reason', 'message', 'object'])
                writer.writeheader()
                writer.writerows(events)
        print(f"✓ Events saved to: {events_file}")
    
    # Collect pod logs
    print("\n📝 Collecting pod logs...")
    output = run_kubectl_command("kubectl get pods --no-headers -o custom-columns=NAME:.metadata.name")
    if output:
        pods = [p.strip() for p in output.strip().split('\n') if p.strip()]
        
        logs_dir = f'data/k8s_logs/pod_logs_{timestamp}'
        os.makedirs(logs_dir, exist_ok=True)
        
        for pod in pods[:5]:  # First 5 pods
            logs = get_pod_logs(pod, lines=200)
            if logs:
                log_file = f'{logs_dir}/{pod}.log'
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(logs)
                print(f"  ✓ Saved logs for {pod}")
    
    # Create summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if hpa_status:
        print(f"\n📊 HPA Status:")
        print(f"   Current replicas: {hpa_status['current_replicas']}")
        print(f"   Desired replicas: {hpa_status['desired_replicas']}")
        print(f"   Current CPU: {hpa_status['current_cpu']}%")
        print(f"   Target CPU: {hpa_status['target_cpu']}%")
    
    if pod_metrics:
        print(f"\n💻 Pod Metrics:")
        for metric in pod_metrics[:5]:
            print(f"   {metric['pod_name']}: CPU={metric['cpu']}, Memory={metric['memory']}")
    
    print("\n" + "="*70)
    print("✅ LOG COLLECTION COMPLETED!")
    print("="*70)
    print(f"\n📁 All logs saved to: data/k8s_logs/")
    
    print("\n🎯 Next steps:")
    print("  1. View logs: dir data\\k8s_logs")
    print("  2. Train AI: python ai-model/train_from_k8s_logs.py")
    print("  3. Analyze with XAI: python explainable-ai/explain_predictions.py")
    
    return {
        'pod_metrics': pod_metrics,
        'hpa_status': hpa_status,
        'events': events
    }

if __name__ == "__main__":
    collect_all_data()
