#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main deployment function
main() {
    log_header "Legal AI Local Deployment"
    
    log_info "Starting comprehensive local deployment..."
    log_info "This script will set up the complete Legal AI system with PDF processing"
    echo ""
    
    # Pre-flight checks
    preflight_checks
    
    # Environment setup
    setup_environment_variables
    
    # Backend setup
    setup_backend_environment
    
    # Frontend setup (if exists)
    setup_frontend_environment
    
    # Database initialization
    initialize_database
    
    # Process PDFs
    process_legal_documents
    
    # Create management scripts
    create_management_scripts
    
    # Final setup
    final_setup_steps
    
    log_success "Local deployment completed successfully!"
    show_next_steps
}

preflight_checks() {
    log_step "Running pre-flight checks..."
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ] || [ ! -d "backend" ]; then
        log_error "This doesn't appear to be the Legal AI project root directory."
        log_error "Please run this script from the project root."
        exit 1
    fi
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed."
        log_error "Please install Python 3.9+ and try again."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]] 2>/dev/null; then
        log_error "Python 3.9+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python 3 found: $(python3 --version)"
    
    # Check Node.js (optional for backend-only deployment)
    if [ -d "frontend" ]; then
        if ! command_exists node; then
            log_warning "Node.js not found. Frontend will be skipped."
            SKIP_FRONTEND=true
        else
            NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
            if [[ $NODE_VERSION -lt 16 ]]; then
                log_warning "Node.js 16+ recommended. Found: $(node --version). Frontend may not work properly."
            else
                log_success "Node.js found: $(node --version)"
            fi
        fi
    fi
    
    # Check for PDF files
    if [ -d "pdf" ]; then
        PDF_COUNT=$(find pdf -name "*.pdf" 2>/dev/null | wc -l)
        if [ $PDF_COUNT -gt 0 ]; then
            log_success "Found $PDF_COUNT PDF files for processing"
        else
            log_warning "No PDF files found in /pdf directory"
        fi
    else
        log_warning "PDF directory not found. Creating it..."
        mkdir -p pdf
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ $AVAILABLE_SPACE -lt 1000000 ]; then  # Less than 1GB
        log_warning "Available disk space is low. Consider freeing up space."
    fi
    
    log_success "Pre-flight checks completed"
}

setup_environment_variables() {
    log_step "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp env.example .env
        
        # Generate a secure secret key
        if command_exists openssl; then
            SECRET_KEY=$(openssl rand -hex 32)
            sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
            log_info "Generated secure secret key"
        fi
        
        log_warning "⚠️  IMPORTANT: Please configure your .env file with:"
        echo "   - OpenRouter API key (required for AI features)"
        echo "   - Database settings (if using PostgreSQL)"
        echo "   - Other API keys as needed"
        echo ""
        
        read -p "Do you want to edit the .env file now? (y/n): " edit_env
        if [[ $edit_env =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        else
            log_warning "Remember to edit .env before using AI features!"
        fi
    else
        log_info "Environment file already exists"
        
        # Check if OpenRouter API key is set
        if grep -q "your-openrouter-api-key" .env; then
            log_warning "⚠️  OpenRouter API key not configured. AI features will be limited."
        fi
    fi
    
    log_success "Environment setup completed"
}

setup_backend_environment() {
    log_step "Setting up backend environment..."
    
    # Create and activate virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install requirements
    log_info "Installing Python dependencies (this may take a few minutes)..."
    pip install -r requirements.txt
    
    # Create necessary directories
    log_info "Creating necessary directories..."
    mkdir -p backend/uploads
    mkdir -p backend/logs
    mkdir -p backend/static
    mkdir -p logs
    
    # Install additional dependencies for better PDF processing
    log_info "Installing additional system dependencies..."
    if command_exists apt-get; then
        sudo apt-get update > /dev/null 2>&1 || true
        sudo apt-get install -y tesseract-ocr poppler-utils > /dev/null 2>&1 || log_warning "Could not install system dependencies. Some PDF features may not work."
    elif command_exists brew; then
        brew install tesseract poppler > /dev/null 2>&1 || log_warning "Could not install system dependencies. Some PDF features may not work."
    fi
    
    log_success "Backend environment setup completed"
}

setup_frontend_environment() {
    if [ "$SKIP_FRONTEND" = true ] || [ ! -d "frontend" ]; then
        log_warning "Skipping frontend setup"
        return
    fi
    
    log_step "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Create environment file for frontend if needed
    if [ ! -f ".env.local" ] && [ -f ".env.example" ]; then
        cp .env.example .env.local
        log_info "Created frontend environment file"
    fi
    
    cd ..
    log_success "Frontend environment setup completed"
}

initialize_database() {
    log_step "Initializing database..."
    
    source venv/bin/activate
    
    # Check database configuration
    if grep -q "postgresql://" .env; then
        log_info "PostgreSQL configuration detected..."
        
        # Try to connect to PostgreSQL
        if command_exists psql; then
            log_info "Setting up PostgreSQL database..."
            
            # Extract database details from .env
            DB_URL=$(grep DATABASE_URL .env | cut -d'=' -f2- | tr -d '"')
            DB_NAME=$(echo $DB_URL | sed 's/.*\/\([^?]*\).*/\1/')
            
            # Create database if it doesn't exist
            createdb "$DB_NAME" 2>/dev/null || log_info "Database '$DB_NAME' already exists"
            
            # Run migrations if alembic is available
            if [ -f "backend/alembic.ini" ]; then
                cd backend
                python -m alembic upgrade head
                cd ..
                log_success "Database migrations completed"
            fi
        else
            log_warning "PostgreSQL client not found. Please ensure PostgreSQL is installed and configured."
        fi
    else
        log_info "Using SQLite database for development..."
        
        # Initialize SQLite database
        cd backend
        python -c "
try:
    from app.core.database import engine
    from app.models import document
    document.Base.metadata.create_all(bind=engine)
    print('✅ SQLite database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"
        cd ..
    fi
    
    log_success "Database initialization completed"
}

process_legal_documents() {
    log_step "Processing legal documents..."
    
    # Check if there are PDFs to process
    if [ ! -d "pdf" ] || [ -z "$(ls -A pdf/*.pdf 2>/dev/null)" ]; then
        log_warning "No PDF files found in /pdf directory"
        log_info "You can add PDF files later and run: python scripts/process_existing_pdfs.py"
        return
    fi
    
    source venv/bin/activate
    
    log_info "Processing PDF files in /pdf directory..."
    log_info "This may take several minutes depending on the number and size of PDFs..."
    
    cd scripts
    python process_existing_pdfs.py
    cd ..
    
    log_success "Legal document processing completed"
}

create_management_scripts() {
    log_step "Creating management scripts..."
    
    # Create comprehensive start script
    cat > start_legal_ai.sh << 'EOF'
#!/bin/bash

# Legal AI Startup Script
echo "🚀 Starting Legal AI System"
echo "=========================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run ./deploy_local.sh first.${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    fi
    return 0
}

# Check ports
if ! check_port 8000; then
    echo "Please stop the service using port 8000 or use a different port"
    exit 1
fi

if [ -d "frontend" ] && ! check_port 3000; then
    echo "Please stop the service using port 3000 or use a different port"
    exit 1
fi

# Start backend
echo -e "${BLUE}📡 Starting backend server...${NC}"
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend if available
if [ -d "frontend" ] && [ ! "$SKIP_FRONTEND" = true ]; then
    echo -e "${BLUE}🎨 Starting frontend server...${NC}"
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
else
    FRONTEND_PID=""
fi

# Display status
echo ""
echo -e "${GREEN}✅ Legal AI System Started!${NC}"
echo "================================"
echo -e "📊 Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "📚 API Documentation: ${BLUE}http://localhost:8000/docs${NC}"
if [ -n "$FRONTEND_PID" ]; then
    echo -e "🎨 Frontend: ${BLUE}http://localhost:3000${NC}"
fi
echo ""
echo -e "${YELLOW}📝 Logs are available in backend/logs/${NC}"
echo -e "${YELLOW}🛑 Press Ctrl+C to stop all services${NC}"
echo ""

# Create cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping Legal AI System...${NC}"
    
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Legal AI System stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Wait for processes
if [ -n "$FRONTEND_PID" ]; then
    wait $BACKEND_PID $FRONTEND_PID
else
    wait $BACKEND_PID
fi
EOF
    
    chmod +x start_legal_ai.sh
    
    # Create PDF processing script
    cat > process_pdfs.sh << 'EOF'
#!/bin/bash

echo "📄 Legal AI PDF Processor"
echo "========================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./deploy_local.sh first."
    exit 1
fi

# Check if PDFs exist
if [ ! -d "pdf" ] || [ -z "$(ls -A pdf/*.pdf 2>/dev/null)" ]; then
    echo "⚠️  No PDF files found in /pdf directory"
    echo "Please add PDF files to the /pdf directory and try again"
    exit 1
fi

echo "🔍 Found $(find pdf -name "*.pdf" | wc -l) PDF files to process"

# Activate virtual environment and process
source venv/bin/activate
cd scripts
python process_existing_pdfs.py
cd ..

echo "✅ PDF processing completed"
EOF
    
    chmod +x process_pdfs.sh
    
    # Create status check script
    cat > check_status.sh << 'EOF'
#!/bin/bash

echo "📊 Legal AI System Status"
echo "========================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running (http://localhost:8000)"
    echo "📚 API docs: http://localhost:8000/docs"
else
    echo "❌ Backend is not running"
fi

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running (http://localhost:3000)"
else
    echo "❌ Frontend is not running"
fi

# Check database
source venv/bin/activate
cd backend
python -c "
try:
    from app.core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM documents'))
        count = result.scalar()
        print(f'✅ Database connected - {count} documents indexed')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
cd ..

# Check PDF files
if [ -d "pdf" ]; then
    PDF_COUNT=$(find pdf -name "*.pdf" 2>/dev/null | wc -l)
    echo "📄 $PDF_COUNT PDF files in /pdf directory"
else
    echo "📄 No PDF directory found"
fi
EOF
    
    chmod +x check_status.sh
    
    log_success "Management scripts created"
}

final_setup_steps() {
    log_step "Final setup steps..."
    
    # Create logs directory
    mkdir -p logs
    
    # Set proper permissions
    chmod +x setup.sh 2>/dev/null || true
    
    # Create a simple README for deployment
    cat > DEPLOYMENT_README.md << 'EOF'
# Legal AI Local Deployment

## Quick Start

1. **Start the system:**
   ```bash
   ./start_legal_ai.sh
   ```

2. **Process PDF files:**
   ```bash
   ./process_pdfs.sh
   ```

3. **Check system status:**
   ```bash
   ./check_status.sh
   ```

## Accessing the System

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000 (if available)

## Managing PDF Documents

1. Place PDF files in the `/pdf` directory
2. Run `./process_pdfs.sh` to process them
3. Documents will be indexed and available for search

## Configuration

Edit the `.env` file to configure:
- OpenRouter API key (required for AI features)
- Database settings
- Model preferences
- Other API keys

## Troubleshooting

1. **Port conflicts:** Check if ports 8000 and 3000 are available
2. **Permission errors:** Ensure scripts are executable: `chmod +x *.sh`
3. **Missing dependencies:** Re-run `./deploy_local.sh`
4. **PDF processing issues:** Check logs in `backend/logs/`

## System Requirements

- Python 3.9+
- Node.js 16+ (for frontend)
- 2GB+ RAM
- 5GB+ disk space
EOF
    
    log_success "Final setup completed"
}

show_next_steps() {
    log_header "🎉 Deployment Successful!"
    
    echo ""
    echo -e "${GREEN}Your Legal AI system is ready!${NC}"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "  1. ${YELLOW}Configure API keys:${NC} Edit .env file with your OpenRouter API key"
    echo -e "  2. ${YELLOW}Start the system:${NC} ./start_legal_ai.sh"
    echo -e "  3. ${YELLOW}Process PDFs:${NC} ./process_pdfs.sh (if you have PDFs in /pdf directory)"
    echo -e "  4. ${YELLOW}Access the system:${NC}"
    echo -e "     • Backend: ${BLUE}http://localhost:8000${NC}"
    echo -e "     • API Docs: ${BLUE}http://localhost:8000/docs${NC}"
    if [ "$SKIP_FRONTEND" != true ] && [ -d "frontend" ]; then
        echo -e "     • Frontend: ${BLUE}http://localhost:3000${NC}"
    fi
    echo ""
    echo -e "${CYAN}Management Commands:${NC}"
    echo -e "  • ${YELLOW}./check_status.sh${NC} - Check system status"
    echo -e "  • ${YELLOW}./process_pdfs.sh${NC} - Process new PDF files"
    echo -e "  • ${YELLOW}./start_legal_ai.sh${NC} - Start all services"
    echo ""
    echo -e "${PURPLE}For server deployment, use:${NC} ./deploy_server.sh"
    echo ""
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "Legal AI Local Deployment Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --skip-frontend    Skip frontend setup"
        echo "  --help, -h         Show this help message"
        echo ""
        echo "This script will:"
        echo "  • Set up Python virtual environment"
        echo "  • Install all dependencies"
        echo "  • Configure database"
        echo "  • Process PDF files"
        echo "  • Create management scripts"
        echo ""
        exit 0
        ;;
    --skip-frontend)
        SKIP_FRONTEND=true
        main
        ;;
    *)
        main
        ;;
esac 