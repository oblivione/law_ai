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

# Default deployment type
DEPLOYMENT_TYPE="docker-compose"
SCALE_BACKEND=2
SCALE_WORKERS=1
USE_SSL=false
DOMAIN=""
EMAIL=""
PRODUCTION_MODE=false

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)
                DEPLOYMENT_TYPE="$2"
                shift 2
                ;;
            --scale-backend)
                SCALE_BACKEND="$2"
                shift 2
                ;;
            --scale-workers)
                SCALE_WORKERS="$2"
                shift 2
                ;;
            --ssl)
                USE_SSL=true
                DOMAIN="$2"
                shift 2
                ;;
            --email)
                EMAIL="$2"
                shift 2
                ;;
            --production)
                PRODUCTION_MODE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    echo "Legal AI Server Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --type TYPE            Deployment type: docker-compose, kubernetes, or standalone"
    echo "  --scale-backend N      Number of backend instances (default: 2)"
    echo "  --scale-workers N      Number of worker instances (default: 1)"
    echo "  --ssl DOMAIN          Enable SSL with Let's Encrypt for domain"
    echo "  --email EMAIL         Email for Let's Encrypt certificate"
    echo "  --production          Enable production optimizations"
    echo "  --help, -h            Show this help message"
    echo ""
    echo "Deployment Types:"
    echo "  docker-compose        Multi-container Docker deployment (recommended)"
    echo "  kubernetes           Kubernetes cluster deployment"
    echo "  standalone           Single server deployment"
    echo ""
    echo "Examples:"
    echo "  $0 --type docker-compose --production"
    echo "  $0 --type docker-compose --ssl legal-ai.example.com --email admin@example.com"
    echo "  $0 --type kubernetes --scale-backend 4 --scale-workers 2"
    echo ""
}

# Main deployment function
main() {
    log_header "Legal AI Server Deployment"
    
    log_info "Deployment Type: $DEPLOYMENT_TYPE"
    log_info "Backend Instances: $SCALE_BACKEND"
    log_info "Worker Instances: $SCALE_WORKERS"
    log_info "Production Mode: $PRODUCTION_MODE"
    
    if [ "$USE_SSL" = true ]; then
        log_info "SSL Domain: $DOMAIN"
    fi
    
    echo ""
    
    # Pre-flight checks
    preflight_checks
    
    # Setup production environment
    setup_production_environment
    
    # Deploy based on type
    case $DEPLOYMENT_TYPE in
        docker-compose)
            deploy_docker_compose
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
        standalone)
            deploy_standalone
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    # Post-deployment setup
    post_deployment_setup
    
    log_success "Server deployment completed successfully!"
    show_deployment_info
}

preflight_checks() {
    log_step "Running pre-flight checks..."
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ] || [ ! -d "backend" ]; then
        log_error "This doesn't appear to be the Legal AI project root directory."
        exit 1
    fi
    
    # Check Docker for docker-compose deployment
    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        if ! command_exists docker; then
            log_error "Docker is required for docker-compose deployment."
            log_error "Please install Docker and try again."
            exit 1
        fi
        
        if ! command_exists docker-compose; then
            log_error "Docker Compose is required."
            log_error "Please install Docker Compose and try again."
            exit 1
        fi
        
        log_success "Docker and Docker Compose found"
    fi
    
    # Check kubectl for Kubernetes deployment
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
        if ! command_exists kubectl; then
            log_error "kubectl is required for Kubernetes deployment."
            exit 1
        fi
        
        if ! kubectl cluster-info > /dev/null 2>&1; then
            log_error "Kubernetes cluster not accessible."
            exit 1
        fi
        
        log_success "Kubernetes cluster accessible"
    fi
    
    # Check system resources
    check_system_resources
    
    # Check PDF files
    if [ -d "pdf" ]; then
        PDF_COUNT=$(find pdf -name "*.pdf" 2>/dev/null | wc -l)
        if [ $PDF_COUNT -gt 0 ]; then
            log_success "Found $PDF_COUNT PDF files for processing"
        else
            log_warning "No PDF files found in /pdf directory"
        fi
    fi
    
    log_success "Pre-flight checks completed"
}

check_system_resources() {
    # Check available memory
    if command_exists free; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ $MEMORY_GB -lt 4 ]; then
            log_warning "Low memory detected ($MEMORY_GB GB). Consider upgrading for better performance."
        else
            log_success "Memory: $MEMORY_GB GB available"
        fi
    fi
    
    # Check available disk space
    DISK_SPACE=$(df -h . | tail -1 | awk '{print $4}')
    log_info "Available disk space: $DISK_SPACE"
}

setup_production_environment() {
    log_step "Setting up production environment..."
    
    # Create production environment file
    if [ ! -f ".env.production" ]; then
        log_info "Creating production environment file..."
        cp env.example .env.production
        
        # Generate secure secret key
        if command_exists openssl; then
            SECRET_KEY=$(openssl rand -hex 32)
            sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/" .env.production
        fi
        
        # Set production defaults
        sed -i 's/DEBUG=true/DEBUG=false/' .env.production
        sed -i 's/sqlite:\/\/\./postgresql:\/\/legal_ai_user:legal_ai_password@postgres:5432/' .env.production
        
        log_warning "⚠️  Please configure .env.production with:"
        echo "   - OpenRouter API key"
        echo "   - Database passwords"
        echo "   - Domain names"
        echo "   - Other production settings"
        echo ""
        
        if [ "$PRODUCTION_MODE" = true ]; then
            read -p "Do you want to edit .env.production now? (y/n): " edit_env
            if [[ $edit_env =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env.production
            fi
        fi
    else
        log_info "Production environment file already exists"
    fi
    
    # Create SSL configuration if needed
    if [ "$USE_SSL" = true ]; then
        setup_ssl_configuration
    fi
    
    log_success "Production environment setup completed"
}

setup_ssl_configuration() {
    log_info "Setting up SSL configuration for $DOMAIN..."
    
    if [ -z "$EMAIL" ]; then
        log_error "Email is required for SSL certificate generation"
        exit 1
    fi
    
    # Create nginx SSL configuration
    mkdir -p nginx/ssl
    
    cat > nginx/nginx-ssl.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name $DOMAIN;
        return 301 https://\$server_name\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

    log_success "SSL configuration created"
}

deploy_docker_compose() {
    log_step "Deploying with Docker Compose..."
    
    # Create production docker-compose file
    cat > docker-compose.production.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: legal_ai_postgres_prod
    environment:
      POSTGRES_DB: legal_ai
      POSTGRES_USER: legal_ai_user
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-legal_ai_secure_password_$(openssl rand -hex 8)}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - legal_ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U legal_ai_user -d legal_ai"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: legal_ai_redis_prod
    command: redis-server --requirepass \${REDIS_PASSWORD:-legal_ai_redis_secure_$(openssl rand -hex 8)}
    volumes:
      - redis_data:/data
    networks:
      - legal_ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  chromadb:
    image: chromadb/chroma:latest
    container_name: legal_ai_chromadb_prod
    environment:
      - CHROMA_HOST_PORT=8001
      - CHROMA_HOST_ADDR=0.0.0.0
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - legal_ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    environment:
      - DATABASE_URL=postgresql://legal_ai_user:\${POSTGRES_PASSWORD:-legal_ai_secure_password_$(openssl rand -hex 8)}@postgres:5432/legal_ai
      - REDIS_URL=redis://:\${REDIS_PASSWORD:-legal_ai_redis_secure_$(openssl rand -hex 8)}@redis:6379
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8001
    env_file:
      - .env.production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./pdf:/app/pdf
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chromadb:
        condition: service_healthy
    networks:
      - legal_ai_network
    restart: unless-stopped
    deploy:
      replicas: $SCALE_BACKEND
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
      args:
        - REACT_APP_API_URL=\${REACT_APP_API_URL:-http://localhost:8000}
    depends_on:
      - backend
    networks:
      - legal_ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PDF Processing Worker
  pdf-processor:
    build:
      context: .
      dockerfile: scripts/Dockerfile.pdf-processor
    environment:
      - DATABASE_URL=postgresql://legal_ai_user:\${POSTGRES_PASSWORD:-legal_ai_secure_password_$(openssl rand -hex 8)}@postgres:5432/legal_ai
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8001
    env_file:
      - .env.production
    volumes:
      - ./pdf:/app/pdf
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      chromadb:
        condition: service_healthy
    networks:
      - legal_ai_network
    restart: "no"
    deploy:
      replicas: $SCALE_WORKERS

EOF

    # Add SSL configuration if enabled
    if [ "$USE_SSL" = true ]; then
        cat >> docker-compose.production.yml << EOF
  nginx:
    image: nginx:alpine
    container_name: legal_ai_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx-ssl.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - backend
      - frontend
    networks:
      - legal_ai_network
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    container_name: legal_ai_certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    command: certonly --webroot -w /var/www/certbot --force-renewal --email $EMAIL -d $DOMAIN --agree-tos
    depends_on:
      - nginx
EOF
    else
        cat >> docker-compose.production.yml << EOF
  nginx:
    image: nginx:alpine
    container_name: legal_ai_nginx_prod
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
    networks:
      - legal_ai_network
    restart: unless-stopped
EOF
    fi

    # Complete the compose file
    cat >> docker-compose.production.yml << EOF

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  chroma_data:
    driver: local

networks:
  legal_ai_network:
    driver: bridge
EOF

    # Create production startup script
    create_production_scripts

    # Build and start services
    log_info "Building and starting production services..."
    docker-compose -f docker-compose.production.yml up -d --build

    # Process PDFs if available
    if [ -d "pdf" ] && [ "$(find pdf -name "*.pdf" 2>/dev/null | wc -l)" -gt 0 ]; then
        log_info "Processing PDF files..."
        docker-compose -f docker-compose.production.yml run --rm pdf-processor
    fi

    log_success "Docker Compose deployment completed"
}

deploy_kubernetes() {
    log_step "Deploying to Kubernetes..."
    
    # Create Kubernetes namespace
    kubectl create namespace legal-ai --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Kubernetes manifests
    create_kubernetes_manifests
    
    # Apply manifests
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f k8s/ -n legal-ai
    
    # Wait for deployments
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=600s deployment --all -n legal-ai
    
    log_success "Kubernetes deployment completed"
}

deploy_standalone() {
    log_step "Deploying standalone server..."
    
    # This would be similar to the local deployment but with production settings
    log_warning "Standalone deployment is not yet implemented in this script."
    log_info "Please use docker-compose deployment for production environments."
    exit 1
}

create_production_scripts() {
    log_info "Creating production management scripts..."
    
    # Production management script
    cat > manage_production.sh << 'EOF'
#!/bin/bash

COMPOSE_FILE="docker-compose.production.yml"

case "$1" in
    start)
        echo "🚀 Starting Legal AI Production Environment..."
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    stop)
        echo "🛑 Stopping Legal AI Production Environment..."
        docker-compose -f $COMPOSE_FILE down
        ;;
    restart)
        echo "🔄 Restarting Legal AI Production Environment..."
        docker-compose -f $COMPOSE_FILE restart
        ;;
    logs)
        SERVICE=${2:-backend}
        echo "📝 Showing logs for $SERVICE..."
        docker-compose -f $COMPOSE_FILE logs -f $SERVICE
        ;;
    status)
        echo "📊 Legal AI Production Status:"
        docker-compose -f $COMPOSE_FILE ps
        ;;
    backup)
        echo "💾 Creating database backup..."
        docker-compose -f $COMPOSE_FILE exec postgres pg_dump -U legal_ai_user legal_ai > "backups/backup_$(date +%Y%m%d_%H%M%S).sql"
        ;;
    process-pdfs)
        echo "📄 Processing PDF files..."
        docker-compose -f $COMPOSE_FILE run --rm pdf-processor
        ;;
    scale)
        SERVICE=$2
        REPLICAS=$3
        if [ -z "$SERVICE" ] || [ -z "$REPLICAS" ]; then
            echo "Usage: $0 scale <service> <replicas>"
            exit 1
        fi
        echo "⚖️  Scaling $SERVICE to $REPLICAS replicas..."
        docker-compose -f $COMPOSE_FILE up -d --scale $SERVICE=$REPLICAS
        ;;
    update)
        echo "🔄 Updating Legal AI..."
        git pull
        docker-compose -f $COMPOSE_FILE build
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    *)
        echo "Legal AI Production Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|logs|status|backup|process-pdfs|scale|update}"
        echo ""
        echo "Commands:"
        echo "  start          Start all services"
        echo "  stop           Stop all services"
        echo "  restart        Restart all services"
        echo "  logs [service] Show logs (default: backend)"
        echo "  status         Show service status"
        echo "  backup         Create database backup"
        echo "  process-pdfs   Process PDF files"
        echo "  scale <service> <replicas>  Scale a service"
        echo "  update         Update and restart services"
        echo ""
        exit 1
        ;;
esac
EOF
    
    chmod +x manage_production.sh
    
    # Create monitoring script
    cat > monitor.sh << 'EOF'
#!/bin/bash

echo "🔍 Legal AI System Monitoring"
echo "============================="

# Check container health
echo "📦 Container Status:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🩺 Health Checks:"

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API is not responding"
fi

# Check database
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U legal_ai_user > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database connection failed"
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis connection failed"
fi

echo ""
echo "📊 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "📄 Document Count:"
docker-compose -f docker-compose.production.yml exec -T backend python -c "
from app.core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM documents'))
        count = result.scalar()
        print(f'📚 {count} documents indexed')
except Exception as e:
    print(f'❌ Failed to query documents: {e}')
"
EOF
    
    chmod +x monitor.sh
    
    log_success "Production scripts created"
}

create_kubernetes_manifests() {
    log_info "Creating Kubernetes manifests..."
    
    mkdir -p k8s
    
    # Namespace
    cat > k8s/namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  name: legal-ai
EOF

    # ConfigMap for environment variables
    cat > k8s/configmap.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: legal-ai-config
  namespace: legal-ai
data:
  DATABASE_URL: "postgresql://legal_ai_user:legal_ai_password@postgres:5432/legal_ai"
  REDIS_URL: "redis://:legal_ai_redis_password@redis:6379"
  CHROMA_HOST: "chromadb"
  CHROMA_PORT: "8001"
EOF

    # PostgreSQL deployment
    cat > k8s/postgres.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: legal-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: "legal_ai"
        - name: POSTGRES_USER
          value: "legal_ai_user"
        - name: POSTGRES_PASSWORD
          value: "legal_ai_password"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: legal-ai
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: legal-ai
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF

    # Backend deployment
    cat > k8s/backend.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: legal-ai
spec:
  replicas: $SCALE_BACKEND
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: legal-ai/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: legal-ai-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: legal-ai
spec:
  ports:
  - port: 8000
  selector:
    app: backend
EOF

    # Add more Kubernetes manifests as needed...
    
    log_success "Kubernetes manifests created"
}

post_deployment_setup() {
    log_step "Running post-deployment setup..."
    
    # Create backup directory
    mkdir -p backups
    
    # Set up log rotation
    setup_log_rotation
    
    # Create monitoring alerts (if requested)
    if [ "$PRODUCTION_MODE" = true ]; then
        setup_monitoring
    fi
    
    log_success "Post-deployment setup completed"
}

setup_log_rotation() {
    log_info "Setting up log rotation..."
    
    # Create logrotate configuration
    cat > /tmp/legal-ai-logrotate << EOF
/home/$USER/law_ai/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
    
    # Install logrotate configuration (requires sudo)
    if command_exists sudo; then
        sudo mv /tmp/legal-ai-logrotate /etc/logrotate.d/legal-ai || log_warning "Could not install log rotation"
    fi
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create monitoring docker-compose addon
    cat > docker-compose.monitoring.yml << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: legal_ai_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - legal_ai_network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: legal_ai_grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - legal_ai_network
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:

networks:
  legal_ai_network:
    external: true
EOF

    mkdir -p monitoring
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'legal-ai-backend'
    static_configs:
      - targets: ['backend:8000']
EOF

    log_success "Monitoring setup created (run with: docker-compose -f docker-compose.monitoring.yml up -d)"
}

show_deployment_info() {
    log_header "🎉 Deployment Successful!"
    
    echo ""
    echo -e "${GREEN}Your Legal AI server is deployed and running!${NC}"
    echo ""
    
    case $DEPLOYMENT_TYPE in
        docker-compose)
            echo -e "${CYAN}Service URLs:${NC}"
            if [ "$USE_SSL" = true ]; then
                echo -e "  • Main Site: ${BLUE}https://$DOMAIN${NC}"
                echo -e "  • API: ${BLUE}https://$DOMAIN/api${NC}"
                echo -e "  • API Docs: ${BLUE}https://$DOMAIN/api/docs${NC}"
            else
                echo -e "  • Main Site: ${BLUE}http://localhost${NC}"
                echo -e "  • API: ${BLUE}http://localhost:8000${NC}"
                echo -e "  • API Docs: ${BLUE}http://localhost:8000/docs${NC}"
            fi
            echo ""
            echo -e "${CYAN}Management Commands:${NC}"
            echo -e "  • ${YELLOW}./manage_production.sh status${NC} - Check service status"
            echo -e "  • ${YELLOW}./manage_production.sh logs${NC} - View logs"
            echo -e "  • ${YELLOW}./manage_production.sh backup${NC} - Create database backup"
            echo -e "  • ${YELLOW}./manage_production.sh process-pdfs${NC} - Process new PDFs"
            echo -e "  • ${YELLOW}./monitor.sh${NC} - Monitor system health"
            ;;
        kubernetes)
            echo -e "${CYAN}Kubernetes Commands:${NC}"
            echo -e "  • ${YELLOW}kubectl get pods -n legal-ai${NC} - Check pod status"
            echo -e "  • ${YELLOW}kubectl logs -f deployment/backend -n legal-ai${NC} - View backend logs"
            echo -e "  • ${YELLOW}kubectl port-forward service/backend 8000:8000 -n legal-ai${NC} - Access API locally"
            ;;
    esac
    
    echo ""
    echo -e "${PURPLE}Scaling:${NC}"
    if [ "$DEPLOYMENT_TYPE" = "docker-compose" ]; then
        echo -e "  • ${YELLOW}./manage_production.sh scale backend 4${NC} - Scale backend to 4 instances"
    else
        echo -e "  • ${YELLOW}kubectl scale deployment backend --replicas=4 -n legal-ai${NC} - Scale backend"
    fi
    
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Configure monitoring and alerts"
    echo -e "  2. Set up regular database backups"
    echo -e "  3. Configure domain and SSL (if not done)"
    echo -e "  4. Add PDF files and process them"
    echo -e "  5. Test the API endpoints"
    echo ""
}

# Parse arguments and run main function
parse_arguments "$@"
main 