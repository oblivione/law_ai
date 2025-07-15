#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    log_info "Starting LegalAI setup..."
    
    # Check prerequisites
    check_prerequisites
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    # Setup environment
    setup_environment
    
    # Create database
    setup_database
    
    # Start services
    start_services
    
    log_success "Setup completed successfully!"
    log_info "Access the application at: http://localhost:3000"
    log_info "API documentation at: http://localhost:8000/docs"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
        log_error "Python 3.9+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python 3 found: $(python3 --version)"
    
    # Check Node.js
    if ! command_exists node; then
        log_error "Node.js is required but not installed."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $NODE_VERSION -lt 16 ]]; then
        log_error "Node.js 16+ is required. Found: $(node --version)"
        exit 1
    fi
    log_success "Node.js found: $(node --version)"
    
    # Check npm
    if ! command_exists npm; then
        log_error "npm is required but not installed."
        exit 1
    fi
    log_success "npm found: $(npm --version)"
    
    # Check Git
    if ! command_exists git; then
        log_warning "Git not found. Some features may not work."
    else
        log_success "Git found: $(git --version)"
    fi
}

setup_backend() {
    log_info "Setting up backend..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    log_success "Backend setup completed"
}

setup_frontend() {
    log_info "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Build for production (optional)
    if [ "$1" = "--production" ]; then
        log_info "Building frontend for production..."
        npm run build
    fi
    
    cd ..
    log_success "Frontend setup completed"
}

setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        log_info "Creating environment file from template..."
        cp env.example .env
        
        log_warning "Please edit .env file with your configuration:"
        log_warning "- Add your OpenRouter API key"
        log_warning "- Configure database settings"
        log_warning "- Adjust other settings as needed"
        
        read -p "Press Enter to continue after configuring .env..."
    else
        log_info "Environment file already exists"
    fi
}

setup_database() {
    log_info "Setting up database..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if PostgreSQL is available
    if command_exists psql && [ "$DATABASE_TYPE" = "postgresql" ]; then
        log_info "Setting up PostgreSQL database..."
        
        # Create database if it doesn't exist
        createdb legal_ai 2>/dev/null || log_info "Database already exists"
        
        # Run migrations
        cd backend
        python -m alembic upgrade head
        cd ..
        
        log_success "PostgreSQL database setup completed"
    else
        log_info "Using SQLite database for development..."
        
        # Initialize SQLite database
        cd backend
        python -c "
from app.core.database import engine
from app.models import document
document.Base.metadata.create_all(bind=engine)
print('SQLite database initialized')
"
        cd ..
        
        log_success "SQLite database setup completed"
    fi
}

start_services() {
    log_info "Starting services..."
    
    # Create startup script
    cat > start_dev.sh << 'EOF'
#!/bin/bash

# Start backend in background
echo "Starting backend server..."
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend in background  
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    
    chmod +x start_dev.sh
    
    log_success "Created start_dev.sh script"
    log_info "Run './start_dev.sh' to start both servers"
}

# Create production setup
setup_production() {
    log_info "Setting up for production..."
    
    # Install production dependencies
    pip install gunicorn
    
    # Build frontend
    cd frontend
    npm run build
    cd ..
    
    # Create production startup script
    cat > start_prod.sh << 'EOF'
#!/bin/bash

source venv/bin/activate

# Start backend with gunicorn
cd backend
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - &
BACKEND_PID=$!

# Serve frontend with a simple Python server
cd ../frontend/build
python3 -m http.server 3000 &
FRONTEND_PID=$!

echo "Production services started!"
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    
    chmod +x start_prod.sh
    log_success "Production setup completed"
}

# Check command line arguments
case "$1" in
    --production)
        main
        setup_production
        ;;
    --dev|"")
        main
        ;;
    --help)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  --dev         Setup for development (default)"
        echo "  --production  Setup for production"
        echo "  --help        Show this help message"
        echo ""
        echo "Prerequisites:"
        echo "  - Python 3.9+"
        echo "  - Node.js 16+"
        echo "  - npm"
        echo "  - Git (optional)"
        echo ""
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 