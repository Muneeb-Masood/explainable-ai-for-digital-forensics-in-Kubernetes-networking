# Setup Guide - Step by Step

This guide will help you set up the entire project from scratch. Don't worry, we'll go slowly! 😊

## Prerequisites

### 1. Install Required Software
- **Python 3.8+**: [Download here](https://www.python.org/downloads/)
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
- **Minikube** (for local Kubernetes): [Download here](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl** (Kubernetes CLI): [Download here](https://kubernetes.io/docs/tasks/tools/)

### 2. Verify Installation
Open PowerShell and run:
```powershell
python --version
docker --version
minikube version
kubectl version --client
```

## Step 1: Set Up Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

## Step 2: Start Kubernetes Cluster

```powershell
# Start Minikube
minikube start --cpus=4 --memory=4096

# Verify cluster is running
kubectl get nodes
```

## Step 3: Deploy Sample Application

```powershell
# Deploy the app
kubectl apply -f kubernetes/deployments/

# Check pods are running
kubectl get pods
```

## Step 4: Set Up Logging

```powershell
# Deploy ELK stack (or use Fluentd)
kubectl apply -f logging/

# Access Kibana (after it's ready)
minikube service kibana
```

## Step 5: Run Attack Simulation

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run DDoS simulation
python attack-simulation/ddos_attack.py

# Run Port Scan simulation
python attack-simulation/port_scan.py
```

## Step 6: Train AI Model

```powershell
# Collect logs and train model
python ai-model/train_model.py

# Test the model
python ai-model/test_model.py
```

## Step 7: Run Explainable AI Analysis

```powershell
# Generate explanations
python explainable-ai/explain_predictions.py

# View results in Jupyter
jupyter notebook notebooks/forensics_analysis.ipynb
```

## Troubleshooting

### Minikube won't start?
- Make sure Docker Desktop is running
- Try: `minikube delete` then `minikube start` again

### Python packages won't install?
- Upgrade pip: `python -m pip install --upgrade pip`
- Try installing packages one by one

### Need help?
Don't hesitate to ask questions! We'll figure it out together. 😊
