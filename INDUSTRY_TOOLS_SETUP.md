# Industry-Standard Tools Installation Guide

## What We're Installing:

All these tools are used by companies like Google, Netflix, Uber, etc.

---

## 1. Prerequisites

### Install Helm (Kubernetes Package Manager)
```powershell
# Download Helm installer
Invoke-WebRequest -Uri https://get.helm.sh/helm-v3.12.0-windows-amd64.zip -OutFile helm.zip

# Extract it
Expand-Archive helm.zip -DestinationPath C:\helm

# Add to PATH (run as Administrator)
$env:Path += ";C:\helm\windows-amd64"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)

# Verify
helm version
```

---

## 2. Start Kubernetes Cluster

```powershell
# Stop existing cluster if any
minikube stop
minikube delete

# Start with enough resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable metrics server (for CPU/memory monitoring)
minikube addons enable metrics-server

# Verify
kubectl get nodes
kubectl top nodes
```

---

## 3. Deploy Your Web Application

```powershell
# Deploy everything
kubectl apply -f kubernetes/deployments/web-app-deployment.yaml
kubectl apply -f kubernetes/services/web-app-service.yaml
kubectl apply -f kubernetes/hpa/web-app-hpa.yaml

# Check status
kubectl get pods
kubectl get svc
kubectl get hpa

# Wait until all pods are "Running"
```

---

## 4. Install Prometheus Stack (Monitoring & Metrics)

```powershell
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (includes Prometheus + Grafana + Alertmanager)
helm install monitoring prometheus-community/kube-prometheus-stack

# This installs:
# - Prometheus: Metrics collection
# - Grafana: Visualization dashboards
# - Alertmanager: Alert management
# - Node Exporter: Hardware metrics
# - Kube State Metrics: Kubernetes metrics

# Wait for all pods (takes 2-3 minutes)
kubectl get pods -w
# Press Ctrl+C when all are "Running"
```

---

## 5. Access Prometheus (Metrics Database)

```powershell
# Port-forward Prometheus to your machine
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090

# Open in browser: http://localhost:9090
# Try queries like:
# - container_cpu_usage_seconds_total
# - container_memory_usage_bytes
# - rate(container_network_receive_bytes_total[1m])
```

---

## 6. Access Grafana (Dashboards)

```powershell
# Port-forward Grafana
kubectl port-forward svc/monitoring-grafana 3000:80

# Open in browser: http://localhost:3000
# Default login:
#   Username: admin
#   Password: prom-operator

# Pre-installed dashboards to check:
# - Kubernetes / Compute Resources / Pod
# - Kubernetes / Compute Resources / Namespace (Pods)
```

---

## 7. Test the Setup

```powershell
# Terminal 1: Watch pod metrics
kubectl top pods -w

# Terminal 2: Watch HPA (auto-scaling)
kubectl get hpa -w

# Terminal 3: Run a small test
# Get service URL
minikube service web-app-service --url
# Visit this URL in your browser
```

---

## 8. Optional: Install ELK Stack (Logging)

For complete logging (if you want to collect logs too):

```powershell
# Add Elastic Helm repo
helm repo add elastic https://helm.elastic.co
helm repo update

# Install Elasticsearch
helm install elasticsearch elastic/elasticsearch --set replicas=1

# Install Kibana
helm install kibana elastic/kibana

# Install Filebeat (log shipper)
helm install filebeat elastic/filebeat
```

---

## What Each Tool Does:

### Prometheus
- **What**: Metrics collection & storage
- **Collects**: CPU, memory, network, disk I/O
- **Industry use**: Google, SoundCloud, Digital Ocean
- **Why**: Time-series database optimized for monitoring

### Grafana  
- **What**: Visualization & dashboards
- **Shows**: Beautiful graphs, alerts, trends
- **Industry use**: Uber, Bloomberg, eBay
- **Why**: Best-in-class visualization tool

### Helm
- **What**: Package manager for Kubernetes
- **Does**: Installs complex apps with one command
- **Industry use**: Every company using Kubernetes
- **Why**: Like "pip" for Kubernetes

### Metrics Server
- **What**: Collects resource metrics from kubelet
- **Provides**: Data for `kubectl top` and HPA
- **Why**: Built-in Kubernetes component

### HPA (Horizontal Pod Autoscaler)
- **What**: Auto-scales pods based on metrics
- **Monitors**: CPU, memory, custom metrics
- **Why**: Core Kubernetes feature for reliability

---

## Troubleshooting:

### Prometheus pods not starting?
```powershell
# Check status
kubectl get pods | grep monitoring

# Check logs
kubectl logs <pod-name>

# If memory issues, restart Minikube with more RAM
minikube stop
minikube start --cpus=4 --memory=10240
```

### Can't access Prometheus/Grafana?
```powershell
# Make sure port-forwarding is running
# Check if process is blocked by firewall
# Try different port: kubectl port-forward ... 9091:9090
```

### Metrics not showing?
```powershell
# Wait 2-3 minutes for metrics to populate
# Check if metrics-server is running
kubectl get deployment metrics-server -n kube-system
```

---

## Quick Verification Checklist:

✅ Minikube running: `minikube status`  
✅ Pods running: `kubectl get pods`  
✅ HPA active: `kubectl get hpa`  
✅ Metrics server: `kubectl top nodes`  
✅ Prometheus accessible: http://localhost:9090  
✅ Grafana accessible: http://localhost:3000  

---

## Next Steps:

Once everything is running:
1. ✅ Run attack simulation
2. ✅ Watch metrics in Prometheus/Grafana
3. ✅ See pods auto-scale
4. ✅ Export metrics for AI training
5. ✅ Train AI model on real data

See: `REAL_ATTACK_GUIDE.md`
