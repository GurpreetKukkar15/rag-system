#!/usr/bin/env python3
"""
Script to install memory-efficient Ollama models for the RAG system.
This helps with systems that have limited RAM.
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and return success status"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            return True
        else:
            print(f"[ERROR] {description} failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"[ERROR] {description} failed with exception: {e}")
        return False

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        result = subprocess.run("ollama list", shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def install_models():
    """Install memory-efficient models in order of preference"""
    
    print("=== Ollama Model Installation Script ===")
    print("This script will install memory-efficient models for your RAG system.")
    print()
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("[ERROR] Ollama is not running. Please start Ollama first:")
        print("  ollama serve")
        print()
        print("Then run this script again.")
        return False
    
    print("[OK] Ollama is running")
    print()
    
    # Models to install (in order of preference - smallest first)
    models = [
        {
            "name": "tinyllama",
            "description": "TinyLlama (1.1B parameters) - Very small, fast model",
            "size": "~637 MB"
        },
        {
            "name": "phi",
            "description": "Phi-3 Mini (3.8B parameters) - Microsoft's efficient model",
            "size": "~2.3 GB"
        },
        {
            "name": "mistral:7b",
            "description": "Mistral 7B - Good balance of quality and size",
            "size": "~4.1 GB"
        }
    ]
    
    print("Available models to install:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model['name']} - {model['description']} ({model['size']})")
    print()
    
    # Ask user which models to install
    print("Which models would you like to install?")
    print("1. Install all models (recommended)")
    print("2. Install only TinyLlama (fastest, smallest)")
    print("3. Install only Phi-3 (good balance)")
    print("4. Install only Mistral 7B (highest quality)")
    print("5. Custom selection")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    models_to_install = []
    
    if choice == "1":
        models_to_install = models
    elif choice == "2":
        models_to_install = [models[0]]
    elif choice == "3":
        models_to_install = [models[1]]
    elif choice == "4":
        models_to_install = [models[2]]
    elif choice == "5":
        print("\nSelect models to install (enter numbers separated by commas):")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model['name']}")
        selections = input("Enter numbers (e.g., 1,3): ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in selections.split(",")]
            models_to_install = [models[i] for i in indices if 0 <= i < len(models)]
        except ValueError:
            print("[ERROR] Invalid selection")
            return False
    else:
        print("[ERROR] Invalid choice")
        return False
    
    if not models_to_install:
        print("[ERROR] No models selected")
        return False
    
    print(f"\n[INFO] Will install {len(models_to_install)} model(s)")
    print()
    
    # Install selected models
    success_count = 0
    for model in models_to_install:
        print(f"[INFO] Installing {model['name']}...")
        print(f"  Description: {model['description']}")
        print(f"  Size: {model['size']}")
        print("  This may take several minutes...")
        print()
        
        if run_command(f"ollama pull {model['name']}", f"Installing {model['name']}"):
            success_count += 1
            print(f"[OK] {model['name']} installed successfully")
        else:
            print(f"[ERROR] Failed to install {model['name']}")
        
        print()
    
    print("=== Installation Summary ===")
    print(f"Successfully installed: {success_count}/{len(models_to_install)} models")
    
    if success_count > 0:
        print("\n[OK] Model installation completed!")
        print("\nYour RAG system will now try to use these models in order of preference:")
        for model in models_to_install:
            print(f"  - {model['name']}")
        print("\nThe system will automatically select the first model that works with your available memory.")
    else:
        print("\n[ERROR] No models were installed successfully.")
        print("Please check your internet connection and Ollama installation.")
    
    return success_count > 0

if __name__ == "__main__":
    try:
        install_models()
    except KeyboardInterrupt:
        print("\n[INFO] Installation cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
