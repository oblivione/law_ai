# 🚀 Full-Stack LegalAI Deployment Guide

## 🔍 Current Issue Identified

The LegalAI application is a **full-stack app** requiring both:
- **Frontend**: React app (currently deployed to GitHub Pages)
- **Backend**: FastAPI Python server (`start.py`) - **NOT deployed**

**GitHub Pages limitation**: Only serves static files, cannot run Python servers.

## 🛠️ Full-Stack Deployment Options

### Option 1: Railway (Recommended) 🚂
**Free tier available, supports both frontend + backend**

1. **Connect Repository**:
   - Go to: https://railway.app
   - Connect your GitHub account
   - Select `oblivione/law_ai` repository

2. **Deploy Backend**:
   - Railway will auto-detect Python app
   - Set start command: `python backend/start.py`
   - Add environment variables (OpenRouter API key, etc.)

3. **Deploy Frontend**:
   - Add second service for React app
   - Build command: `cd frontend && npm run build`
   - Static files served automatically

### Option 2: Render 🎨
**Free tier, excellent for full-stack**

1. **Backend Service**:
   - Create new Web Service
   - Root directory: `backend`
   - Start command: `python start.py`

2. **Frontend Service**:
   - Create new Static Site
   - Root directory: `frontend`
   - Build command: `npm run build`

### Option 3: Heroku 📦
**Classic platform, reliable**

1. **Create Heroku App**
2. **Add Procfile**: `web: python backend/start.py`
3. **Configure buildpacks**: Python + Node.js
4. **Deploy via Git**

### Option 4: Docker + Cloud Run 🐳
**Use existing docker-compose.yml**

1. **Google Cloud Run** or **AWS Container Service**
2. **Deploy using**: `docker-compose.yml`
3. **Automatic scaling**

### Option 5: Local Development 💻
**For testing and development**

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python start.py

# Terminal 2: Frontend  
cd frontend
npm install
npm start
```

## 🔧 Environment Variables Needed

```env
# Required for backend
OPENROUTER_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./legal_ai.db
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Optional but recommended
REDIS_URL=redis://localhost:6379
MAX_FILE_SIZE_MB=50
```

## 🎯 Recommended Next Steps

1. **Choose Railway or Render** (easiest full-stack deployment)
2. **Set up environment variables**
3. **Deploy both backend and frontend**
4. **Update frontend API URLs** to point to deployed backend

## 🌐 Expected Result

After full-stack deployment:
- **Backend API**: `https://your-app.railway.app/api/docs`
- **Frontend**: `https://your-app.railway.app`
- **Full functionality**: Search, upload, AI analysis working

## 📝 Current GitHub Pages Status

- ✅ **React frontend deployed** to GitHub Pages
- ❌ **Backend not deployed** (GitHub Pages limitation)
- 🔄 **Need full-stack platform** for complete functionality

---

**The code is 100% ready - we just need the right deployment platform!** 🚀
