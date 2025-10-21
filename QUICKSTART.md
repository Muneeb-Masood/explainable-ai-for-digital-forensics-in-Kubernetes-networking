# Quick Start Guide

Welcome! Here's how to get your project running quickly. 🚀

## Step 1: Install Python Packages (5 minutes)

Open PowerShell in your project folder and run:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install all packages (this will take a few minutes)
pip install -r requirements.txt
```

## Step 2: Install Kubernetes (10 minutes)

1. Install **Docker Desktop** from: https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop
3. Install **Minikube** from: https://minikube.sigs.k8s.io/docs/start/
4. Open PowerShell and run:
   ```powershell
   minikube start --cpus=4 --memory=4096
   ```

## Step 3: Try the Project! (Quick Demo)

### Train the AI Model First:
```powershell
.\venv\Scripts\Activate.ps1
python ai-model/train_model.py
```

### Run Explainable AI:
```powershell
python explainable-ai/explain_predictions.py
```

This will show you how AI detects attacks and explains why!

## Step 4: Deploy to Kubernetes (Optional)

```powershell
# Deploy the web app
kubectl apply -f kubernetes/deployments/web-app-deployment.yaml
kubectl apply -f kubernetes/services/web-app-service.yaml
kubectl apply -f kubernetes/hpa/web-app-hpa.yaml

# Check if it's running
kubectl get pods
kubectl get svc
```

## Step 5: Simulate Attacks (Optional)

```powershell
# Get the service URL
minikube service web-app-service --url

# In the attack scripts, update TARGET_URL with the URL from above
# Then run:
python attack-simulation/ddos_attack.py
```

Watch your pods scale automatically with:
```powershell
kubectl get pods -w
```

## What Each Part Does:

1. **AI Model** (`ai-model/`) - Detects if traffic is normal or an attack
2. **Explainable AI** (`explainable-ai/`) - Explains WHY it's an attack (for forensics)
3. **Kubernetes** (`kubernetes/`) - Runs your app and auto-scales under attack
4. **Attack Simulation** (`attack-simulation/`) - Simulates DDoS and port scanning

## Need Help?

Just ask! I'm here to help you understand anything. 😊

Remember: Start with Steps 1 and 3 first to see the AI in action!
