#!/bin/bash

# ===============================
# Git Bash-Friendly RAG System Launcher
# Avoids [200~ bracketed paste issues
# ===============================

echo "Starting RAG System (Git Bash version)..."

# Step 1: Kill old processes
echo "Step 1: Cleaning up old processes..."
powershell.exe -Command "Get-Process python,ollama -ErrorAction SilentlyContinue | Stop-Process -Force; Write-Host '[OK] Old processes killed'"

# Step 2: Activate virtual environment
echo "Step 2: Activating virtual environment..."
powershell.exe -Command "& '.\venv\Scripts\Activate.ps1'; Write-Host '[OK] Virtual environment activated'"

# Step 3: Start Ollama if not running
echo "Step 3: Starting Ollama..."
powershell.exe -Command "if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) { Start-Process 'C:\Users\gurpr\AppData\Local\Programs\Ollama\ollama.exe'; Write-Host '[OK] Ollama started'; Start-Sleep -Seconds 5 } else { Write-Host '[OK] Ollama already running' }"

# Step 4: Start FastAPI
echo "Step 4: Starting FastAPI..."
echo "==============================================="
echo "RAG System will be available at: http://127.0.0.1:8000"
echo "API Documentation: http://127.0.0.1:8000/docs"
echo "Press Ctrl+C to stop the server"
echo "==============================================="

powershell.exe -Command "Write-Host '[INFO] Starting FastAPI...'; python .\src\main.py"
