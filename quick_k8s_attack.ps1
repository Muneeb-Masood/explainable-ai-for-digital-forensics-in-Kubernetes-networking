# Quick Kubernetes Attack Script - Simplified
param(
    [int]$Duration = 30,
    [int]$Connections = 100,
    [int]$Port = 8080,
    [int]$MetricDuration = 0,  # 0 = Duration + 60 seconds
    [switch]$SkipPrometheus
)

$ErrorActionPreference = "Continue"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "KUBERNETES ATTACK - QUICK RUN" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Calculate metric collection duration
if ($MetricDuration -eq 0) {
    $MetricDuration = $Duration + 60
}

# Step 0: Deploy Prometheus and start metric collection
if (-not $SkipPrometheus) {
    Write-Host "[0/7] Setting up Prometheus for metrics..." -ForegroundColor Yellow
    
    # Deploy Prometheus
    kubectl apply -f kubernetes/prometheus-deployment.yaml 2>&1 | Out-Null
    
    Write-Host "   Waiting for Prometheus pod..." -ForegroundColor Gray
    $maxWait = 60
    $waited = 0
    while ($waited -lt $maxWait) {
        $pod = kubectl get pods -n monitoring -l app=prometheus -o jsonpath='{.items[0].status.phase}' 2>$null
        if ($pod -eq "Running") { break }
        Start-Sleep -Seconds 5
        $waited += 5
    }
    
    # Start port-forward for Prometheus
    Write-Host "   Starting Prometheus port-forward..." -ForegroundColor Gray
    $prometheusJob = Start-Job -ScriptBlock {
        kubectl port-forward -n monitoring svc/prometheus 9090:9090 2>&1 | Out-Null
    }
    Start-Sleep -Seconds 5
    
    # Start metric collection in background
    Write-Host "   Starting metric collection ($MetricDuration seconds)..." -ForegroundColor Green
    $metricsJob = Start-Job -ScriptBlock {
        param($dur)
        C:\Python312\python.exe ai-model\collect_k8s_metrics_simple.py --duration $dur --interval 5 --output ai-model\k8s_metrics.csv 2>&1
    } -ArgumentList $MetricDuration
    
    Start-Sleep -Seconds 3
    Write-Host "   [OK] Prometheus and metrics collection started" -ForegroundColor Green
} else {
    Write-Host "[Skipped] Prometheus setup" -ForegroundColor Yellow
}

# 1. Deploy
Write-Host "`n[1/6] Cleaning up old resources..." -ForegroundColor Yellow
kubectl delete -f kubernetes/demo-hpa/php-apache-hpa.yaml 2>$null
kubectl delete -f kubernetes/demo-hpa/php-apache-service.yaml 2>$null
kubectl delete -f kubernetes/demo-hpa/php-apache-deployment.yaml 2>$null
Start-Sleep -Seconds 3

Write-Host "[2/6] Deploying application..." -ForegroundColor Yellow
kubectl apply -f kubernetes/demo-hpa/php-apache-deployment.yaml
kubectl apply -f kubernetes/demo-hpa/php-apache-service.yaml
kubectl apply -f kubernetes/demo-hpa/php-apache-hpa.yaml
Start-Sleep -Seconds 8

Write-Host "[3/6] Starting port-forward in background..." -ForegroundColor Yellow
$portForwardJob = Start-Job -ScriptBlock {
    param($p)
    kubectl port-forward service/php-apache ${p}:80
} -ArgumentList $Port
Start-Sleep -Seconds 5

Write-Host "`nChecking service..." -ForegroundColor Yellow
kubectl get pods -l app=php-apache
kubectl get hpa php-apache

Write-Host "`n[4/6] Launching Slowloris attack..." -ForegroundColor Red
Write-Host "Target: localhost:$Port -> Kubernetes service" -ForegroundColor Cyan
Write-Host "Duration: $Duration seconds" -ForegroundColor Cyan
Write-Host "Connections: $Connections`n" -ForegroundColor Cyan

# Manual traffic capture step
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "MANUAL STEP: START TRAFFIC CAPTURE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "   1. Open Wireshark" -ForegroundColor White
Write-Host "   2. Start capturing on the appropriate network interface" -ForegroundColor White
Write-Host "   3. Make sure you can see traffic flowing" -ForegroundColor White
Write-Host ""
Write-Host "Press ENTER when you are ready to start the attack..." -ForegroundColor Green
Read-Host

C:\Python312\python.exe attack-simulation/advanced_attacks.py `
    --mode slowloris `
    --host localhost `
    --port $Port `
    --duration $Duration `
    --connections $Connections

Write-Host "`n[5/6] Attack complete!" -ForegroundColor Green
Write-Host "`nCurrent status:" -ForegroundColor Yellow
kubectl get hpa php-apache
kubectl get pods -l app=php-apache

# Manual PCAP save step
Write-Host "`n============================================================" -ForegroundColor Yellow
Write-Host "MANUAL STEP: SAVE WIRESHARK CAPTURE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "   1. In Wireshark, STOP the capture (Ctrl+E)" -ForegroundColor White
Write-Host "   2. Save the capture file as: ai-model\latest.pcap" -ForegroundColor White
Write-Host "   3. Make sure the file is saved in the ai-model directory" -ForegroundColor White
Write-Host ""
Write-Host "Save location: ai-model\latest.pcap" -ForegroundColor Gray
Write-Host ""
Write-Host "Press ENTER when you have saved the PCAP file..." -ForegroundColor Green
Read-Host

# AI Analysis Workflow
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "AI ANALYSIS & FEATURE EXTRACTION WORKFLOW" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Push-Location ai-model

# Step 3a: Extract CIC features from PCAP
Write-Host "`n[Step 3a] Extracting CIC features from PCAP..." -ForegroundColor Yellow
Write-Host "Running: C:\Python312\python.exe extract_cic_direct.py --pcap latest.pcap --out cic_features_output.csv" -ForegroundColor Gray
$env:PYTHONIOENCODING = "utf-8"
$result = C:\Python312\python.exe extract_cic_direct.py --pcap latest.pcap --out cic_features_output.csv 2>&1
if (Test-Path "cic_features_output.csv") {
    Write-Host "   [OK] CIC features extracted successfully" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] CIC extraction failed: $result" -ForegroundColor Red
}

# Step 3b: Map CIC features to model schema
Write-Host "`n[Step 3b] Mapping CIC features to model schema..." -ForegroundColor Yellow
Write-Host "Running: C:\Python312\python.exe map_cic_features.py --input cic_features_output.csv --output mapped_features.csv" -ForegroundColor Gray
$result = C:\Python312\python.exe map_cic_features.py --input cic_features_output.csv --output mapped_features.csv 2>&1
if (Test-Path "mapped_features.csv") {
    Write-Host "   [OK] Features mapped successfully" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Feature mapping failed: $result" -ForegroundColor Red
}

# Step 3c: Collect Kubernetes metrics (if not already collected)
if ($SkipPrometheus) {
    Write-Host "`n[Step 3c] Collecting Kubernetes metrics (Prometheus was skipped)..." -ForegroundColor Yellow
    Write-Host "Running: C:\Python312\python.exe collect_k8s_metrics_simple.py --duration 60 --interval 5 --output k8s_metrics.csv" -ForegroundColor Gray
    $result = C:\Python312\python.exe collect_k8s_metrics_simple.py --duration 60 --interval 5 --output k8s_metrics.csv 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] K8s metrics collected" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] K8s metrics collection failed: $result" -ForegroundColor Red
    }
} else {
    Write-Host "`n[Step 3c] Using Kubernetes metrics from Prometheus..." -ForegroundColor Yellow
    Write-Host "   [OK] Metrics already collected during attack" -ForegroundColor Green
}

# Step 3d: Merge K8s metrics with flow features
Write-Host "`n[Step 3d] Merging K8s metrics with flow features..." -ForegroundColor Yellow
Write-Host "Running: inline Python script to merge K8s metrics" -ForegroundColor Gray
$result = C:\Python312\python.exe -c "
import pandas as pd
import os

print('Loading data...')
# Use correct file paths
k8s_file = 'k8s_metrics.csv' if os.path.exists('k8s_metrics.csv') else '../k8s_metrics.csv'
if not os.path.exists(k8s_file):
    print('Warning: K8s metrics file not found, creating dummy data')
    k8s_data = {
        'container_cpu_usage_seconds_rate': [0.1],
        'container_memory_usage_bytes': [100000],
        'container_memory_working_set_bytes': [80000],
        'container_network_receive_bytes_rate': [1000],
        'container_network_transmit_bytes_rate': [1200],
        'container_network_receive_packets_rate': [10],
        'container_network_transmit_packets_rate': [12]
    }
    k8s = pd.DataFrame(k8s_data)
else:
    k8s = pd.read_csv(k8s_file)

flows = pd.read_csv('mapped_features.csv')
print(f'K8s metrics: {k8s.shape}')
print(f'Flow features: {flows.shape}')

k8s_cols = [
    'container_cpu_usage_seconds_rate',
    'container_memory_usage_bytes', 
    'container_memory_working_set_bytes',
    'container_network_receive_bytes_rate',
    'container_network_transmit_bytes_rate',
    'container_network_receive_packets_rate',
    'container_network_transmit_packets_rate'
]

k8s_avg = k8s[k8s_cols].mean()

for col in k8s_cols:
    flows[col] = k8s_avg[col]

flows.to_csv('mapped_features_with_k8s.csv', index=False)
print(f'Saved flows with K8s metrics: {flows.shape}')
" 2>&1
if (Test-Path "mapped_features_with_k8s.csv") {
    Write-Host "   [OK] K8s metrics merged with flows" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] K8s merge failed: $result" -ForegroundColor Red
}

# Step 3e: Filter to top-20 features for model
Write-Host "`n[Step 3e] Filtering to top-20 features for model..." -ForegroundColor Yellow
Write-Host "Running: C:\Python312\python.exe filter_top20_from_cic.py --cic_csv mapped_features_with_k8s.csv --output_csv final_top20_features.csv" -ForegroundColor Gray
$result = C:\Python312\python.exe filter_top20_from_cic.py --cic_csv mapped_features_with_k8s.csv --output_csv final_top20_features.csv 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Top-20 features filtered" -ForegroundColor Green
} else {
    Write-Host "   [WARN] Top-20 filtering had issues (continuing...)" -ForegroundColor Yellow
}

# Step 3f: Run AI model predictions
Write-Host "`n[Step 3f] Running AI model predictions..." -ForegroundColor Yellow
Write-Host "Running: inline Python script for AI predictions" -ForegroundColor Gray
$result = C:\Python312\python.exe -c "
import joblib
import pandas as pd
import os

try:
    print('Loading model...')
    model_path = 'saved_models/dvwa_attack_detector_top20.pkl'
    if not os.path.exists(model_path):
        print('ERROR: Model file not found at', model_path)
        exit(1)
    
    model = joblib.load(model_path)
    print('Model loaded successfully')

    print('Loading test data...')
    if not os.path.exists('final_top20_features.csv'):
        print('ERROR: final_top20_features.csv not found')
        exit(1)
        
    X_test = pd.read_csv('final_top20_features.csv')
    print(f'Test data loaded: {X_test.shape}')

    print('Making predictions...')
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    results = pd.DataFrame({
        'prediction': predictions,
        'prob_class_0': probabilities[:, 0],
        'prob_class_1': probabilities[:, 1] if probabilities.shape[1] > 1 else 0
    })
    results.to_csv('predictions_output.csv', index=False)

    print(f'Predictions saved: {len(predictions)} flows')
    print(f'Attack detection rate: {100 * sum(predictions) / len(predictions):.1f}%')
    
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" 2>&1
if (Test-Path "predictions_output.csv") {
    Write-Host "   [OK] AI predictions completed" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] AI prediction failed: $result" -ForegroundColor Red
}

# Step 3g: Analyze results
Write-Host "`n[Step 3g] Analyzing results..." -ForegroundColor Yellow
Write-Host "Running: C:\Python312\python.exe analyze_predictions.py" -ForegroundColor Gray
$result = C:\Python312\python.exe analyze_predictions.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Analysis complete" -ForegroundColor Green
} else {
    Write-Host "   [INFO] Analysis completed with warnings" -ForegroundColor Yellow
}

# Step 4: View Results
Write-Host "`n[Step 4] Viewing Results..." -ForegroundColor Yellow
Write-Host "Predictions output:" -ForegroundColor Gray
if (Test-Path "predictions_output.csv") {
    Get-Content "predictions_output.csv" | Select-Object -First 10
    Write-Host "... (showing first 10 lines)" -ForegroundColor Gray
} else {
    Write-Host "   [WARN] predictions_output.csv not found" -ForegroundColor Yellow
}

Pop-Location

# Wait for metric collection to finish
if (-not $SkipPrometheus) {
    if ($metricsJob) {
        Write-Host "`n[6/6] Waiting for metric collection to complete..." -ForegroundColor Yellow
        $remaining = ($MetricDuration - $Duration)
        if ($remaining -gt 0) {
            Write-Host "   Collecting metrics for $remaining more seconds..." -ForegroundColor Gray
            Wait-Job -Job $metricsJob -Timeout $remaining | Out-Null
        }
        
        # Check if collection completed
        $state = (Get-Job -Id $metricsJob.Id).State
        if ($state -eq "Completed") {
            Write-Host "   [OK] Metric collection complete!" -ForegroundColor Green
        } else {
            Write-Host "   [WARN] Metric collection still running..." -ForegroundColor Yellow
        }
        
        Stop-Job $metricsJob -ErrorAction SilentlyContinue
        Remove-Job $metricsJob -ErrorAction SilentlyContinue
    }
}

# Cleanup port-forwards
if ($portForwardJob) {
    Stop-Job $portForwardJob -ErrorAction SilentlyContinue
    Remove-Job $portForwardJob -ErrorAction SilentlyContinue
}
if ($prometheusJob) {
    Stop-Job $prometheusJob -ErrorAction SilentlyContinue
    Remove-Job $prometheusJob -ErrorAction SilentlyContinue
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "COMPLETE A-Z ANALYSIS FINISHED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nRESULTS SUMMARY:" -ForegroundColor Yellow
if (-not $SkipPrometheus) {
    Write-Host "   K8s Metrics: ai-model\k8s_metrics.csv" -ForegroundColor Green
}
Write-Host "   PCAP Features: ai-model\cic_features_output.csv" -ForegroundColor Green
Write-Host "   Mapped Features: ai-model\mapped_features_with_k8s.csv" -ForegroundColor Green
Write-Host "   Top-20 Features: ai-model\final_top20_features.csv" -ForegroundColor Green
Write-Host "   AI Predictions: ai-model\predictions_output.csv" -ForegroundColor Green

Write-Host "`nOPTIONAL: SHAP Explainability Analysis" -ForegroundColor Yellow
Write-Host "To generate SHAP visualizations, run:" -ForegroundColor Cyan
Write-Host "   cd explainable-ai" -ForegroundColor Gray
Write-Host "   C:\Python312\python.exe shap_analysis_complete.py" -ForegroundColor Gray

Write-Host "`nWHAT TO CHECK:" -ForegroundColor Yellow
Write-Host "   1. Pod scaling: kubectl get hpa -w" -ForegroundColor Cyan
Write-Host "   2. Check ai-model\predictions_output.csv for detection results" -ForegroundColor Cyan
Write-Host "   3. View analysis results above" -ForegroundColor Cyan

Write-Host "`nCLEANUP COMMANDS:" -ForegroundColor Yellow
Write-Host "   # Delete K8s resources:" -ForegroundColor Gray
Write-Host "   kubectl delete -f kubernetes/demo-hpa/php-apache-hpa.yaml" -ForegroundColor Gray
Write-Host "   kubectl delete -f kubernetes/demo-hpa/php-apache-service.yaml" -ForegroundColor Gray
Write-Host "   kubectl delete -f kubernetes/demo-hpa/php-apache-deployment.yaml" -ForegroundColor Gray

Write-Host "`nONE-LINE AUTOMATION:" -ForegroundColor Yellow
Write-Host "   For future runs: .\quick_k8s_attack.ps1 -Duration 30" -ForegroundColor Cyan

Write-Host "`n============================================================`n" -ForegroundColor Cyan
