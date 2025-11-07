# Quick Kubernetes Attack Script - Simplified
param(
    [int]$Duration = 30,
    [int]$Connections = 100,
    [int]$Port = 8080
)

$ErrorActionPreference = "Continue"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "KUBERNETES ATTACK - QUICK RUN" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 1. Deploy
Write-Host "[1/5] Cleaning up old resources..." -ForegroundColor Yellow
kubectl delete -f kubernetes/demo-hpa/php-apache-hpa.yaml 2>$null
kubectl delete -f kubernetes/demo-hpa/php-apache-service.yaml 2>$null
kubectl delete -f kubernetes/demo-hpa/php-apache-deployment.yaml 2>$null
Start-Sleep -Seconds 3

Write-Host "[2/5] Deploying application..." -ForegroundColor Yellow
kubectl apply -f kubernetes/demo-hpa/php-apache-deployment.yaml
kubectl apply -f kubernetes/demo-hpa/php-apache-service.yaml
kubectl apply -f kubernetes/demo-hpa/php-apache-hpa.yaml
Start-Sleep -Seconds 8

Write-Host "[3/5] Starting port-forward in background..." -ForegroundColor Yellow
$portForwardJob = Start-Job -ScriptBlock {
    param($p)
    kubectl port-forward service/php-apache ${p}:80
} -ArgumentList $Port
Start-Sleep -Seconds 5

Write-Host "`nChecking service..." -ForegroundColor Yellow
kubectl get pods -l app=php-apache
kubectl get hpa php-apache

Write-Host "`n[4/5] Launching Slowloris attack..." -ForegroundColor Red
Write-Host "Target: localhost:$Port -> Kubernetes service" -ForegroundColor Cyan
Write-Host "Duration: $Duration seconds" -ForegroundColor Cyan
Write-Host "Connections: $Connections`n" -ForegroundColor Cyan

C:\Python312\python.exe attack-simulation/advanced_attacks.py `
    --mode slowloris `
    --host localhost `
    --port $Port `
    --duration $Duration `
    --connections $Connections

Write-Host "`n[5/5] Attack complete!" -ForegroundColor Green
Write-Host "`nCurrent status:" -ForegroundColor Yellow
kubectl get hpa php-apache
kubectl get pods -l app=php-apache

# Cleanup port-forward
if ($portForwardJob) {
    Stop-Job $portForwardJob
    Remove-Job $portForwardJob
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DONE! Watch scale-down: kubectl get hpa -w" -ForegroundColor Yellow
Write-Host "============================================================`n" -ForegroundColor Cyan
