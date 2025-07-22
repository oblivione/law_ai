# LegalAI - Deployment Guide

## 🌐 Live Demo

- **Frontend (GitHub Pages)**: [https://oblivione.github.io/law_ai](https://oblivione.github.io/law_ai) 🚀 **DEPLOYING**
- **Repository**: [https://github.com/oblivione/law_ai](https://github.com/oblivione/law_ai) ✅ **PUBLIC & LIVE**

## 🚀 Quick Deploy Options

### 1. GitHub Pages (Frontend Only)
The React frontend is automatically deployed to GitHub Pages via GitHub Actions.

### 2. Full Stack Deployment

#### Option A: Docker Compose (Recommended)
```bash
git clone https://github.com/oblivione/law_ai.git
cd law_ai
cp env.example .env
# Edit .env with your API keys
docker-compose up -d
```

#### Option B: Railway/Render/Heroku
1. Fork the repository
2. Connect to your cloud platform
3. Set environment variables
4. Deploy backend and frontend separately

#### Option C: Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm start
```

## �� Configuration

### Required Environment Variables
```env
OPENROUTER_API_KEY=your_api_key
DATABASE_URL=postgresql://user:pass@host/db
CHROMA_HOST=localhost
CHROMA_PORT=8001
```

## 📊 Features Demo

This AI-powered legal platform includes:

- 🔍 **Semantic Search**: AI-powered document search
- 📄 **Document Processing**: PDF, DOCX, TXT support
- 🧠 **Legal Analysis**: AI reasoning and precedent analysis
- 📊 **Analytics**: Document insights and statistics
- 🔒 **Secure**: Enterprise-grade security

## 🛠️ Tech Stack

- **Backend**: FastAPI, PostgreSQL, ChromaDB
- **Frontend**: React, TypeScript, Tailwind CSS
- **AI**: OpenRouter, Claude, Embedding Models
- **Deployment**: Docker, GitHub Actions

## 📞 Support

For issues or questions:
1. Check the [main README](README.md)
2. Open an issue on GitHub
3. Contact the development team

---
Built with ❤️ for the legal community
