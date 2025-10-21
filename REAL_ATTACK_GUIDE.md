# Step-by-Step: Real Attack Simulation with Industry Logging

## Overview
We'll set up REAL logging tools used in industry, simulate attacks, collect logs, and train AI on that data.

## Industry Tools We'll Use:

1. **Prometheus** - Collects metrics (CPU, memory, requests)
2. **Grafana** - Visualizes the data
3. **Fluentd** - Collects logs from all pods
4. **Elasticsearch** - Stores logs
5. **Kibana** - Views logs

---

## Phase 1: Setup Kubernetes with Monitoring (30 minutes)

### Step 1: Start Minikube with enough resources
```powershell
# Stop if already running
minikube stop

# Start with more resources for monitoring tools
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable metrics
minikube addons enable metrics-server
```

### Step 2: Deploy our web application
```powershell
kubectl apply -f kubernetes/deployments/web-app-deployment.yaml
kubectl apply -f kubernetes/services/web-app-service.yaml
kubectl apply -f kubernetes/hpa/web-app-hpa.yaml

# Wait for pods to be ready
kubectl get pods -w
```

### Step 3: Install Prometheus & Grafana
```powershell
# Add Prometheus helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana stack
helm install prometheus prometheus-community/kube-prometheus-stack

# Wait for all pods to be ready (takes 2-3 minutes)
kubectl get pods -w
```

---

## Phase 2: Run Attack & Collect Logs (15 minutes)

### Step 1: Get the service URL
```powershell
minikube service web-app-service --url
# Copy this URL
```

### Step 2: Update attack script
Open `attack-simulation/ddos_attack.py` and change `TARGET_URL` to the URL from above.

### Step 3: Run attack in one terminal
```powershell
# Terminal 1
.\venv\Scripts\Activate.ps1
python attack-simulation/ddos_attack.py
```

### Step 4: Watch scaling in another terminal
```powershell
# Terminal 2
kubectl get pods -w
kubectl get hpa -w
```

### Step 5: Collect metrics during attack
```powershell
# Get Prometheus URL
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

# Open in browser: http://localhost:9090
# Run these queries:
# 1. container_cpu_usage_seconds_total
# 2. container_memory_usage_bytes
# 3. rate(container_network_receive_bytes_total[1m])
```

---

## Phase 3: Export Real Data for AI Training (10 minutes)

### Export metrics to CSV
We'll create a script that pulls real data from Prometheus and saves it for AI training!

See: `logging/export_metrics.py`

### Run the export
```powershell
.\venv\Scripts\Activate.ps1
python logging/export_metrics.py
```

This creates: `data/real_attack_logs.csv`

---

## Phase 4: Train AI on Real Data (5 minutes)

```powershell
# Train model using real logs
python ai-model/train_model_real_data.py

# Test it
python ai-model/test_model.py

# Explain with XAI
python explainable-ai/explain_predictions.py
```

---

## What Makes This "Industry Standard"?

✅ **Prometheus** - Used by Google, Amazon, Microsoft  
✅ **Grafana** - Standard monitoring dashboard  
✅ **Helm** - Kubernetes package manager (like pip for k8s)  
✅ **Metrics Server** - Real CPU/memory data  
✅ **HPA** - Real auto-scaling based on metrics  
✅ **Real attacks** - Actual HTTP flood, not fake data  

---

## Timeline:

1. **Setup** (30 min) - Install tools, deploy app
2. **Attack** (5 min) - Run DDoS simulation
3. **Collect** (5 min) - Export real metrics
4. **Train** (5 min) - Train AI on real data
5. **Analyze** (5 min) - XAI explanations

**Total: ~50 minutes for complete real-world demo!**

---

## Next Steps:

Let me create all the necessary files for you...
