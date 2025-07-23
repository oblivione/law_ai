# Legal AI System - Deployment Guide

This guide provides comprehensive instructions for deploying the Legal AI system both locally and on production servers with PDF processing capabilities.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Local Deployment](#local-deployment)
- [Server Deployment](#server-deployment)
- [PDF Processing](#pdf-processing)
- [Configuration](#configuration)
- [Scaling & Production](#scaling--production)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **Python 3.9+** (3.11 recommended)
- **Node.js 16+** (for frontend)
- **Docker & Docker Compose** (for containerized deployment)
- **4GB+ RAM** (8GB+ recommended for production)
- **10GB+ disk space**

### API Keys
- **OpenRouter API Key** (required for AI features)
- **Database credentials** (for production PostgreSQL)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd law_ai
```

### 2. Local Development Setup
```bash
# Run the comprehensive local setup
./deploy_local.sh

# Start the system
./start_legal_ai.sh
```

### 3. Access the System
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000 (if available)

## 🏠 Local Deployment

### Simple Setup
```bash
# Basic deployment with default settings
./deploy_local.sh

# Skip frontend if not needed
./deploy_local.sh --skip-frontend
```

### What the Local Deployment Does:
1. ✅ Sets up Python virtual environment
2. ✅ Installs all dependencies
3. ✅ Configures database (SQLite for development)
4. ✅ Processes PDFs from `/pdf` directory
5. ✅ Creates management scripts
6. ✅ Sets up environment variables

### Management Commands
```bash
# Start all services
./start_legal_ai.sh

# Process new PDFs
./process_pdfs.sh

# Check system status
./check_status.sh
```

## 🌐 Server Deployment

### Docker Compose (Recommended)
```bash
# Basic production deployment
./deploy_server.sh --type docker-compose --production

# With SSL and custom domain
./deploy_server.sh --type docker-compose --ssl yourdomain.com --email admin@yourdomain.com --production

# Scale backend and workers
./deploy_server.sh --type docker-compose --scale-backend 4 --scale-workers 2
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes cluster
./deploy_server.sh --type kubernetes --scale-backend 3 --scale-workers 2

# Check deployment status
kubectl get pods -n legal-ai
```

### What Server Deployment Includes:
- 🐘 **PostgreSQL** database with persistent storage
- 🔴 **Redis** for caching and queues
- 🔍 **ChromaDB** for vector storage
- 🐳 **Backend API** with multiple replicas
- 🎨 **Frontend** application
- 🔒 **Nginx** reverse proxy with SSL support
- 📊 **Monitoring** and health checks
- 💾 **Automated backups**

## 📄 PDF Processing

### Automatic Processing
PDFs in the `/pdf` directory are automatically processed during deployment:

```bash
# Your PDFs are already included:
pdf/
├── constitution_of_india.pdf
├── bns.pdf
├── bnss.pdf
├── bsa.pdf
├── contract.pdf
├── easement\ act.pdf
├── THE\ CODE\ OF\ CIVIL\ PROCEDURE,\ 1908.pdf
└── 51_Property_Law.pdf
```

### Manual Processing
```bash
# Process new PDFs manually
./process_pdfs.sh

# Use the standalone processor with options
python scripts/process_pdfs_standalone.py --batch-size 10 --concurrent 4 --verbose

# Force reprocess all files
python scripts/process_pdfs_standalone.py --force
```

### Advanced PDF Processing
```bash
# Dry run to see what would be processed
python scripts/process_pdfs_standalone.py --dry-run --verbose

# Process from custom directory
python scripts/process_pdfs_standalone.py --pdf-dir /path/to/pdfs --output-dir /path/to/output

# With custom database
python scripts/process_pdfs_standalone.py --database-url postgresql://user:pass@host:5432/db
```

## ⚙️ Configuration

### Environment Files
- `.env` - Local development settings
- `.env.production` - Production settings (created automatically)
- `config/production.yaml` - Advanced production configuration

### Key Settings to Configure

#### 1. OpenRouter API Key (Required)
```bash
# Edit .env or .env.production
OPENROUTER_API_KEY="your-api-key-here"
```

#### 2. Database Configuration
```bash
# For production PostgreSQL
DATABASE_URL="postgresql://user:password@host:5432/legal_ai"

# For development SQLite (default)
DATABASE_URL="sqlite:///./legal_docs.db"
```

#### 3. AI Model Settings
```bash
DOCUMENT_ANALYSIS_MODEL="anthropic/claude-3-sonnet"
REASONING_MODEL="anthropic/claude-3-opus"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

#### 4. File Processing Limits
```bash
MAX_FILE_SIZE=104857600  # 100MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 📈 Scaling & Production

### Production Management
```bash
# Start production services
./manage_production.sh start

# Check service status
./manage_production.sh status

# View logs
./manage_production.sh logs backend

# Scale services
./manage_production.sh scale backend 4

# Create database backup
./manage_production.sh backup

# Update system
./manage_production.sh update
```

### Monitoring
```bash
# Check system health
./monitor.sh

# Set up monitoring stack (Prometheus + Grafana)
docker-compose -f docker-compose.monitoring.yml up -d
```

### Load Balancing & High Availability
The system is designed for horizontal scaling:

- **Backend API:** Scale with `--scale-backend N`
- **PDF Workers:** Scale with `--scale-workers N`
- **Database:** PostgreSQL with read replicas
- **Vector Store:** ChromaDB with persistence
- **Caching:** Redis cluster support

### SSL/TLS Configuration
```bash
# Deploy with Let's Encrypt SSL
./deploy_server.sh --ssl yourdomain.com --email admin@yourdomain.com

# Manual SSL certificate setup
# Place certificates in nginx/ssl/
# Update nginx configuration
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000

# Kill conflicting processes
pkill -f "uvicorn"
pkill -f "npm start"
```

#### 2. PDF Processing Failures
```bash
# Check PDF processor logs
cat logs/pdf_processing.log

# Test individual PDF
python scripts/process_pdfs_standalone.py --pdf-dir test_pdf --verbose --dry-run

# Check system dependencies
sudo apt-get install tesseract-ocr poppler-utils  # Ubuntu/Debian
brew install tesseract poppler                    # macOS
```

#### 3. Database Connection Issues
```bash
# Check database status
./check_status.sh

# For Docker deployment
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Reset database (WARNING: destroys data)
rm -f backend/legal_docs.db  # SQLite only
```

#### 4. Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Reduce concurrent workers
# Edit .env: set lower values for batch_size and concurrent workers
```

#### 5. API Key Issues
```bash
# Verify API key is set
grep OPENROUTER_API_KEY .env

# Test API key
curl -H "Authorization: Bearer YOUR_KEY" https://openrouter.ai/api/v1/models
```

### Logs and Debugging

#### Log Locations
- **Local Development:** `backend/logs/`
- **Docker Deployment:** `logs/` (mounted volume)
- **Processing Reports:** `processed/`

#### Debug Commands
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Check service health
curl http://localhost:8000/health

# View detailed logs
./manage_production.sh logs backend
docker-compose -f docker-compose.production.yml logs -f
```

### Performance Optimization

#### 1. Database Optimization
```bash
# For PostgreSQL, tune these settings:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB
```

#### 2. Vector Store Optimization
```bash
# Increase ChromaDB memory
# Set CHROMA_MEMORY_LIMIT in environment
```

#### 3. Processing Optimization
```bash
# Reduce batch size for limited memory
python scripts/process_pdfs_standalone.py --batch-size 3 --concurrent 2

# Use faster embedding models for development
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

## 📞 Support

### Getting Help
1. Check the logs first: `./check_status.sh`
2. Review this deployment guide
3. Check the API documentation: http://localhost:8000/docs
4. Verify your environment configuration

### System Information
```bash
# Get system info for troubleshooting
./check_status.sh > system_status.txt
cat system_status.txt
```

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Local deployment
./deploy_local.sh

# Start system
./start_legal_ai.sh

# Process PDFs
./process_pdfs.sh

# Server deployment
./deploy_server.sh --type docker-compose --production

# Production management
./manage_production.sh status
./monitor.sh
```

### URLs
- **Local API:** http://localhost:8000
- **Local Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Monitoring:** http://localhost:3001 (if enabled)

### Important Files
- `deploy_local.sh` - Local deployment script
- `deploy_server.sh` - Server deployment script
- `start_legal_ai.sh` - Start services locally
- `manage_production.sh` - Production management
- `.env` - Environment configuration
- `pdf/` - PDF files to process

The Legal AI system is now ready for deployment! 🚀 