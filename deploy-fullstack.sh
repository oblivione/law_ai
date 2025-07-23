#!/bin/bash

echo "🚀 LegalAI Full-Stack Deployment Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "backend/start.py" ]; then
    echo "❌ Error: backend/start.py not found. Run this script from the project root."
    exit 1
fi

echo "✅ Project structure verified"

# Option 1: Local Development Setup
setup_local() {
    echo "🔧 Setting up local development environment..."
    
    # Backend setup
    echo "📦 Setting up backend..."
    cd backend
    python -m venv venv
    source venv/bin/activate || ./venv/Scripts/activate
    pip install -r ../requirements.txt
    
    # Frontend setup  
    echo "📦 Setting up frontend..."
    cd ../frontend
    npm install
    
    echo "✅ Local setup complete!"
    echo "To run the app:"
    echo "1. Backend: cd backend && source venv/bin/activate && python start.py"
    echo "2. Frontend: cd frontend && npm start"
    echo "3. Visit: http://localhost:3000"
}

# Option 2: Docker setup
setup_docker() {
    echo "🐳 Setting up Docker deployment..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    echo "🔨 Building and starting containers..."
    docker-compose up -d --build
    
    echo "✅ Docker deployment complete!"
    echo "Visit: http://localhost:3000"
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1) Local development setup"
echo "2) Docker deployment"
echo "3) Show cloud deployment options"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        setup_local
        ;;
    2)
        setup_docker
        ;;
    3)
        echo "☁️ Cloud Deployment Options:"
        echo ""
        echo "🚂 Railway (Recommended):"
        echo "   1. Go to https://railway.app"
        echo "   2. Connect GitHub account"
        echo "   3. Deploy oblivione/law_ai repository"
        echo "   4. Set environment variables"
        echo ""
        echo "🎨 Render:"
        echo "   1. Go to https://render.com"
        echo "   2. Create Web Service (backend)"
        echo "   3. Create Static Site (frontend)"
        echo ""
        echo "📦 Heroku:"
        echo "   1. Create Heroku app"
        echo "   2. Push repository"
        echo "   3. Configure environment variables"
        echo ""
        echo "See FULLSTACK_DEPLOYMENT.md for detailed instructions."
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
