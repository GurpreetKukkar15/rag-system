# Memory Optimization Guide

This guide helps you optimize your RAG system for systems with limited RAM.

## Current Issue

Your system is experiencing memory issues with the Mistral model:
- **Required**: 2.3 GiB
- **Available**: 2.1-2.2 GiB
- **Result**: Model fails to load

## Solutions

### 1. Install Smaller Models

Run the model installation script:

```bash
python install_models.py
```

This will install memory-efficient models in order of preference:
- **TinyLlama** (1.1B parameters, ~637 MB) - Fastest, smallest
- **Phi-3 Mini** (3.8B parameters, ~2.3 GB) - Good balance
- **Mistral 7B** (7B parameters, ~4.1 GB) - Highest quality

### 2. Manual Model Installation

If you prefer to install models manually:

```bash
# Start Ollama (if not running)
ollama serve

# Install TinyLlama (recommended for low memory)
ollama pull tinyllama

# Install Phi-3 Mini (good balance)
ollama pull phi

# Install Mistral 7B (if you have enough RAM)
ollama pull mistral:7b
```

### 3. System Memory Optimization

#### Windows Memory Management
```powershell
# Check available memory
Get-ComputerInfo | Select-Object TotalPhysicalMemory, AvailablePhysicalMemory

# Close unnecessary applications
# - Close browser tabs
# - Close other Python processes
# - Close unused applications
```

#### Ollama Memory Settings
You can limit Ollama's memory usage by setting environment variables:

```bash
# Set Ollama to use less memory
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_MAX_QUEUE=1
```

### 4. Model Configuration

The system now automatically tries models in this order:
1. `tinyllama` - Smallest, fastest
2. `phi` - Good balance
3. `mistral:7b` - Higher quality
4. `mistral:latest` - Full model

### 5. Fallback System

If all models fail due to memory issues, the system will:
1. Use a fallback LLM that provides basic responses
2. Still process your documents and provide context
3. Give you the raw document content when possible

## Testing Your Setup

1. **Start the system**:
   ```bash
   source venv/Scripts/activate
   python src/main.py
   ```

2. **Check the logs** for model selection:
   ```
   [DEBUG] Trying model: tinyllama
   [OK] LLM initialized (using Ollama: tinyllama)
   ```

3. **Test with a query** to see if memory issues are resolved

## Recommended Configuration

For systems with **2-4 GB RAM**:
- Use **TinyLlama** or **Phi-3 Mini**
- Close other applications
- Set `OLLAMA_NUM_PARALLEL=1`

For systems with **4+ GB RAM**:
- Use **Mistral 7B** or **Phi-3 Mini**
- Can run other applications
- Default Ollama settings should work

## Troubleshooting

### Model Still Fails
1. Check available memory: `Get-ComputerInfo | Select-Object AvailablePhysicalMemory`
2. Close other applications
3. Try the smallest model: `ollama pull tinyllama`
4. Restart Ollama: `ollama serve`

### System Becomes Unresponsive
1. Stop the RAG system (Ctrl+C)
2. Stop Ollama
3. Restart with smaller model
4. Check system resources

### Fallback Responses
If you see fallback responses, it means:
- The LLM couldn't load due to memory issues
- The system is still processing your documents
- You're getting basic responses instead of AI-generated ones

## Performance Tips

1. **Use TinyLlama** for fastest responses
2. **Limit context length** (already optimized in the code)
3. **Process fewer documents** at once
4. **Close unnecessary applications**
5. **Restart the system** periodically to free memory

## Next Steps

1. Run `python install_models.py`
2. Restart your RAG system
3. Test with a simple query
4. Check the logs for successful model loading

The system will now automatically handle memory issues and provide the best possible experience with your available resources.
