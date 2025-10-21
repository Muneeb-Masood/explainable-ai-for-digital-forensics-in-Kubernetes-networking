# Complete Kubernetes Attack Simulation with Logging

Write-Host ("=" * 70)
Write-Host "KUBERNETES ATTACK SIMULATION WITH REAL LOGS" -ForegroundColor Green
Write-Host ("=" * 70)

# Step 1: Wait for pods to be ready
Write-Host "`n[Step 1] Waiting for pods to be ready..." -ForegroundColor Cyan
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    $pods = kubectl get pods --no-headers 2>$null
    
    if ($pods) {
        $runningCount = 0
        $totalCount = 0
        
        foreach ($line in ($pods -split "`n")) {
            if ($line.Trim()) {
                $totalCount++
                if ($line -match "Running") {
                    $runningCount++
                }
            }
        }
        
        Write-Host "  Attempt $attempt/$maxAttempts : $runningCount/$totalCount pods running"
        
        if ($runningCount -eq $totalCount -and $totalCount -gt 0) {
            Write-Host "  All pods are running!" -ForegroundColor Green
            break
        }
    }
    
    Start-Sleep -Seconds 2
}

# Step 2: Show deployment status
Write-Host "`n[Step 2] Deployment Status:" -ForegroundColor Cyan
kubectl get pods
kubectl get svc
kubectl get hpa

# Step 3: Get service URL
Write-Host "`n[Step 3] Getting service URL..." -ForegroundColor Cyan
$nodePort = kubectl get svc web-app-service -o jsonpath="{.spec.ports[0].nodePort}"
$minikubeIp = minikube ip

$targetUrl = "http://${minikubeIp}:${nodePort}"
Write-Host "  Service URL: $targetUrl" -ForegroundColor Yellow

# Step 4: Update attack script with correct URL
Write-Host "`n[Step 4] Updating attack script..." -ForegroundColor Cyan
$attackScript = "attack-simulation/ddos_attack.py"
$content = Get-Content $attackScript -Raw
$content = $content -replace 'TARGET_URL = ".*"', "TARGET_URL = `"$targetUrl`""
Set-Content -Path $attackScript -Value $content
Write-Host "  Attack script updated with URL: $targetUrl" -ForegroundColor Green

# Step 5: Test connectivity
Write-Host "`n[Step 5] Testing connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri $targetUrl -TimeoutSec 5 -UseBasicParsing
    Write-Host "  Service is accessible! Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  Service might not be ready yet, but continuing..." -ForegroundColor Yellow
}

# Step 6: Instructions for running attack
Write-Host "`n" -NoNewline
Write-Host ("=" * 70)
Write-Host "READY TO SIMULATE ATTACK!" -ForegroundColor Green
Write-Host ("=" * 70)

Write-Host "`nOpen 3 PowerShell terminals and run these commands:"
Write-Host "`n[Terminal 1] Watch Pods Scaling:" -ForegroundColor Cyan
Write-Host "  kubectl get pods -w" -ForegroundColor White

Write-Host "`n[Terminal 2] Watch HPA (Auto-scaler):" -ForegroundColor Cyan
Write-Host "  kubectl get hpa -w" -ForegroundColor White

Write-Host "`n[Terminal 3] Run Attack:" -ForegroundColor Cyan
Write-Host "  cd D:\NIS\explainable-ai-for-digital-forencics-in-kubernetes-networking" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python attack-simulation\ddos_attack.py" -ForegroundColor White

Write-Host "`nAfter attack, collect logs with:" -ForegroundColor Cyan
Write-Host "  python logging\collect_k8s_logs.py" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host ("=" * 70)
