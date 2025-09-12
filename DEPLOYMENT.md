# RAG System Deployment Guide

## 🚀 Deploy to Vercel (Free Tier)

### Prerequisites
1. **GitHub Account** - Create one at [github.com](https://github.com)
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
3. **Git** - Already installed on your system

### Step 1: Initialize Git Repository
```bash
# In your project directory
git init
git add .
git commit -m "Initial commit: RAG System ready for deployment"
```

### Step 2: Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it: `rag-system`
4. Make it **Public** (required for free Vercel)
5. Don't initialize with README (you already have files)
6. Click "Create repository"

### Step 3: Push to GitHub
```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/rag-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository: `rag-system`
4. Vercel will auto-detect Python
5. **Important Settings:**
   - **Framework Preset**: Other
   - **Root Directory**: Leave empty (uses root)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`
6. Click "Deploy"

### Step 5: Environment Variables (Optional)
In Vercel dashboard, go to your project → Settings → Environment Variables:
- `PYTHONPATH`: `/var/task`
- `OLLAMA_URL`: `https://your-ollama-instance.com` (if using external Ollama)

### Step 6: Test Your Deployment
1. Vercel will give you a URL like: `https://rag-system-abc123.vercel.app`
2. Visit the URL to test your RAG system
3. Upload documents and test queries

## 🔧 Important Notes for Vercel

### Limitations
- **No persistent storage** - Files uploaded will be lost on restart
- **No Ollama support** - Vercel doesn't support Ollama
- **10-second timeout** - For free tier

### Solutions
1. **For file storage**: Use external storage (AWS S3, Google Cloud Storage)
2. **For Ollama**: Use external Ollama service or switch to OpenAI API
3. **For database**: Use external database (PlanetScale, Supabase, etc.)

### Alternative: Railway Deployment
For better Python support with persistent storage:

1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy with these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

## 📁 Project Structure for Deployment
```
rag-system/
├── .gitignore
├── requirements.txt
├── vercel.json
├── main.py
├── DEPLOYMENT.md
└── src/
    ├── api.py
    ├── database.py
    └── init_db.py
```

## 🐛 Troubleshooting

### Common Issues
1. **Import errors**: Check `PYTHONPATH` in vercel.json
2. **Module not found**: Ensure all dependencies in requirements.txt
3. **File uploads fail**: Vercel has no persistent storage
4. **Ollama not working**: Use external Ollama service

### Debug Commands
```bash
# Test locally
python main.py

# Check dependencies
pip list

# Test API
curl http://localhost:8000/api/health
```

## 🎉 Success!
Once deployed, your RAG system will be available at:
- **Vercel URL**: `https://your-project.vercel.app`
- **API Docs**: `https://your-project.vercel.app/docs`
- **Health Check**: `https://your-project.vercel.app/api/health`