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
Write-Host "DONE!" -ForegroundColor Green
if (-not $SkipPrometheus) {
    Write-Host "Metrics saved to: ai-model\k8s_metrics.csv" -ForegroundColor Yellow
}
Write-Host "Watch scale-down: kubectl get hpa -w" -ForegroundColor Yellow
Write-Host "============================================================`n" -ForegroundColor Cyan
