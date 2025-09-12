# stop-rag.ps1
# RAG System Cleanup Script
Write-Host "Stopping RAG System..." -ForegroundColor Cyan

# 1. Kill any process using port 8000
$port = 8000
Write-Host "Checking port $port..." -ForegroundColor Yellow
try {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $pid = $connection.OwningProcess
        Write-Host "Killing process $pid on port $port..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
        Write-Host "Process killed" -ForegroundColor Green
    } else {
        Write-Host "No process using port $port" -ForegroundColor Green
    }
} catch {
    Write-Host "Port $port is free" -ForegroundColor Green
}

# 2. Kill all Python processes
Write-Host "Stopping all Python processes..." -ForegroundColor Yellow
try {
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $pythonProcesses | Stop-Process -Force
        Write-Host "Stopped $($pythonProcesses.Count) Python process(es)" -ForegroundColor Green
    } else {
        Write-Host "No Python processes running" -ForegroundColor Blue
    }
} catch {
    Write-Host "No Python processes to stop" -ForegroundColor Blue
}

# 3. Stop Ollama processes
Write-Host "Stopping Ollama..." -ForegroundColor Yellow
try {
    $ollamaProcesses = Get-Process ollama -ErrorAction SilentlyContinue
    if ($ollamaProcesses) {
        $ollamaProcesses | Stop-Process -Force
        Write-Host "Stopped $($ollamaProcesses.Count) Ollama process(es)" -ForegroundColor Green
    } else {
        Write-Host "No Ollama processes running" -ForegroundColor Blue
    }
} catch {
    Write-Host "No Ollama processes to stop" -ForegroundColor Blue
}

# 4. Verify cleanup
Write-Host "Verifying cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$portCheck = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
$pythonCheck = Get-Process python -ErrorAction SilentlyContinue
$ollamaCheck = Get-Process ollama -ErrorAction SilentlyContinue

if (-not $portCheck -and -not $pythonCheck -and -not $ollamaCheck) {
    Write-Host "All processes stopped successfully!" -ForegroundColor Green
    Write-Host "Port $port is free" -ForegroundColor Green
    Write-Host "No Python processes running" -ForegroundColor Green
    Write-Host "No Ollama processes running" -ForegroundColor Green
} else {
    Write-Host "Some processes may still be running:" -ForegroundColor Yellow
    if ($portCheck) { Write-Host "Port $port still in use" -ForegroundColor Red }
    if ($pythonCheck) { Write-Host "Python processes still running" -ForegroundColor Red }
    if ($ollamaCheck) { Write-Host "Ollama processes still running" -ForegroundColor Red }
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "RAG System stopped" -ForegroundColor Cyan