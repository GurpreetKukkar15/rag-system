#!/bin/bash

# ===============================
# Complete RAG System Launcher
# Kills old processes, starts Ollama, activates venv, starts FastAPI
# ===============================

echo "🚀 Starting Complete RAG System..."

# Step 1: Kill any existing Python processes
echo "Step 1: Cleaning up old processes..."
powershell.exe -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force; Write-Host '[OK] Old processes killed'"

# Step 2: Check if Ollama is running, start if needed
echo "Step 2: Starting Ollama..."
powershell.exe -Command "if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) { Start-Process 'C:\Users\gurpr\AppData\Local\Programs\Ollama\ollama.exe'; Write-Host '[OK] Ollama started'; Start-Sleep -Seconds 5 } else { Write-Host '[OK] Ollama already running' }"

# Step 3: Activate virtual environment
echo "Step 3: Activating virtual environment..."
source venv/Scripts/activate

# Step 4: Install dependencies if needed
echo "Step 4: Checking dependencies..."
python -c "from langchain_community.document_loaders import PyPDFLoader; print('[OK] Dependencies verified')" 2>/dev/null || {
    echo "Installing missing dependencies..."
    pip install langchain langchain_community langchain-huggingface langchain-ollama faiss-cpu pypdf sentence-transformers
}

# Step 5: Start FastAPI
echo "Step 5: Starting FastAPI..."
echo "==============================================="
echo "RAG System will be available at: http://127.0.0.1:8000"
echo "API Documentation: http://127.0.0.1:8000/docs"
echo "Health Check: http://127.0.0.1:8000/api/health"
echo "Press Ctrl+C to stop the server"
echo "==============================================="

python src/main.py
