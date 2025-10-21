# Explainable AI for Digital Forensics in Kubernetes Networking

## Project Overview
This project demonstrates how to detect and explain network attacks in a Kubernetes environment using AI and Explainable AI (XAI) techniques for digital forensics.

## Features
- Kubernetes cluster setup with sample applications
- Simulation of network attacks (DDoS, Port Scanning)
- Auto-scaling of pods under attack
- Centralized logging with ELK Stack (Elasticsearch, Logstash, Kibana)
- AI-based attack detection
- Explainable AI for forensic analysis

## Project Structure
```
├── kubernetes/              # Kubernetes manifests
│   ├── deployments/        # App deployments
│   ├── services/           # Services
│   └── hpa/                # Horizontal Pod Autoscaler configs
├── logging/                # Logging setup (ELK/Fluentd)
├── attack-simulation/      # Scripts to simulate attacks
├── ai-model/               # AI model for attack detection
├── explainable-ai/         # XAI implementation (SHAP/LIME)
├── data/                   # Sample network logs
└── notebooks/              # Jupyter notebooks for analysis

## Technologies Used
- **Kubernetes**: Container orchestration
- **Minikube/Kind**: Local Kubernetes cluster
- **Python**: Main programming language
- **ELK Stack**: Logging (Elasticsearch, Logstash, Kibana)
- **Fluentd**: Log collection
- **Scikit-learn/TensorFlow**: AI models
- **SHAP/LIME**: Explainable AI
- **Locust/hping3**: Attack simulation

## Setup Instructions
Coming soon...

## Attack Scenarios
1. **DDoS Attack**: Flood the service with requests
2. **Port Scanning**: Scan for open ports and vulnerabilities

## Digital Forensics
The XAI component explains:
- Which features led to attack detection
- Confidence scores for predictions
- Visual explanations for investigators
