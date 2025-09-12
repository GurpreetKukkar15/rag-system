# start-rag.ps1
# RAG System Startup Script
Write-Host "Starting RAG System..." -ForegroundColor Cyan

# 1. Kill any process using port 8000 (optional cleanup)
$port = 8000
Write-Host "Checking port $port..." -ForegroundColor Yellow
try {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $pid = $connection.OwningProcess
        Write-Host "Port $port is busy, killing process $pid..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Port $port is free" -ForegroundColor Green
    }
} catch {
    Write-Host "Port $port is free" -ForegroundColor Green
}

# 2. Kill any existing Python processes (cleanup)
Write-Host "Cleaning up existing Python processes..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Python processes cleaned up" -ForegroundColor Green
} catch {
    Write-Host "No Python processes to clean up" -ForegroundColor Blue
}

# 3. Start Ollama if available
Write-Host "Starting Ollama..." -ForegroundColor Green

# Check if Ollama is already running
try {
    $ollamaCheck = Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($ollamaCheck.StatusCode -eq 200) {
        Write-Host "[OK] Ollama is already running" -ForegroundColor Green
        $models = ($ollamaCheck.Content | ConvertFrom-Json).models
        if ($models.Count -gt 0) {
            Write-Host "   Available models: $($models.name -join ', ')" -ForegroundColor Cyan
        }
    } else {
        throw "Ollama not responding"
    }
} catch {
    # Ollama not running, try to start it
    Write-Host "Ollama not running, starting new instance..." -ForegroundColor Yellow
    
    # Try multiple possible Ollama paths
    $ollamaPaths = @(
        "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe",
        "C:\Program Files\Ollama\ollama.exe"
    )

    $ollamaPath = $null
    foreach ($path in $ollamaPaths) {
        if (Test-Path $path) {
            $ollamaPath = $path
            break
        }
    }

    if ($ollamaPath) {
        Write-Host "Found Ollama at $ollamaPath" -ForegroundColor Green
        
        # Create logs directory
        if (-not (Test-Path "logs")) {
            New-Item -ItemType Directory -Path "logs" | Out-Null
        }
        
        # Start Ollama with logging
        Start-Process -FilePath $ollamaPath -ArgumentList "serve" -RedirectStandardOutput "logs\ollama.log" -RedirectStandardError "logs\ollama.err" -WindowStyle Hidden
        Start-Sleep -Seconds 5
        
        try {
            $response = Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "[OK] Ollama started successfully" -ForegroundColor Green
                $models = ($response.Content | ConvertFrom-Json).models
                if ($models.Count -gt 0) {
                    Write-Host "   Available models: $($models.name -join ', ')" -ForegroundColor Cyan
                }
            } else {
                Write-Host "[WARNING] Ollama responded with status code $($response.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[ERROR] Ollama did not respond in time" -ForegroundColor Red
            Write-Host "   Check logs\ollama.log for details" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[ERROR] Ollama not found in any expected location" -ForegroundColor Red
        Write-Host "   Searched: $($ollamaPaths -join ', ')" -ForegroundColor Yellow
        Write-Host "   Download it from: https://ollama.com/download" -ForegroundColor Yellow
    }
}

# 4. Activate your virtual environment
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment" -ForegroundColor Green
    & $venvPath
} else {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "python -m venv venv" -ForegroundColor Yellow
    Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# 5. Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import uvicorn, fastapi, sqlalchemy" 2>$null
    Write-Host "Required packages are installed" -ForegroundColor Green
} catch {
    Write-Host "Missing required packages. Installing..." -ForegroundColor Red
    pip install -r requirements.txt
}

# 6. Run your FastAPI app
Write-Host "Starting FastAPI on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "API logs will be saved to: logs\api.log" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Start FastAPI with logging (without -Wait so it runs in background)
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "src.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" -RedirectStandardOutput "logs\api.log" -RedirectStandardError "logs\api.err" -NoNewWindow -PassThru

# Wait a moment for API to start
Write-Host "Waiting for API to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Health check with polling
Write-Host "Checking API health..." -ForegroundColor Yellow
$maxRetries = 10
$ok = $false
$healthStatus = "unknown"

for ($i=0; $i -lt $maxRetries; $i++) {
    Start-Sleep -Seconds 2
    try {
        $resp = Invoke-WebRequest http://127.0.0.1:8000/api/health -UseBasicParsing -TimeoutSec 3
        $json = $resp.Content | ConvertFrom-Json
        $healthStatus = $json.status
        
        if ($json.status -eq "ok" -or $json.status -eq "degraded" -or $json.status -eq "healthy") {
            Write-Host "[OK] FastAPI is running! Health status: $($json.status)" -ForegroundColor Green
            
            # Show detailed status
            Write-Host "   Database: $($json.database)" -ForegroundColor $(if($json.database) {"Green"} else {"Red"})
            Write-Host "   FAISS: $($json.faiss) ($($json.faiss_documents) documents)" -ForegroundColor $(if($json.faiss) {"Green"} else {"Red"})
            Write-Host "   LLM: $($json.llm) ($($json.llm_type))" -ForegroundColor $(if($json.llm) {"Green"} else {"Red"})
            Write-Host "   Ollama: $($json.ollama) ($($json.ollama_models -join ', '))" -ForegroundColor $(if($json.ollama) {"Green"} else {"Red"})
            
            Write-Host "===============================================" -ForegroundColor Cyan
            Write-Host "Open your browser to: http://127.0.0.1:8000" -ForegroundColor Cyan
            Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
            Write-Host "===============================================" -ForegroundColor Cyan
            
            $ok = $true
            break
        } else {
            Write-Host "   Attempt $($i+1)/$maxRetries - Status = $($json.status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Attempt $($i+1)/$maxRetries - Connection failed" -ForegroundColor Yellow
    }
}

if (-not $ok) {
    Write-Host "[ERROR] API did not become healthy in time. Final status: $healthStatus" -ForegroundColor Red
    Write-Host "Check logs\api.log for details:" -ForegroundColor Yellow
    Write-Host "   Get-Content logs\api.log -Tail 20" -ForegroundColor Gray
    Write-Host "   Get-Content logs\api.err -Tail 20" -ForegroundColor Gray
} else {
    # Keep the script running and wait for user to stop
    Write-Host "API is running. Press any key to stop..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    # Stop the API process
    Stop-Process -Id $apiProcess.Id -Force
    Write-Host "API stopped." -ForegroundColor Yellow
}