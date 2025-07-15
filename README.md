# LegalAI - Legal Document Search & Analysis Platform

A comprehensive AI-powered legal document search and analysis platform built with FastAPI, React, and advanced AI models. This system provides semantic search, legal reasoning, document analysis, and intelligent categorization for legal professionals.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Search    │ │   Upload    │ │  Analysis   │           │
│  │   Interface │ │   System    │ │  Dashboard  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            │
                     ┌──────┴──────┐
                     │             │
┌────────────────────▼─────────────▼───────────────────────────┐
│                Backend (FastAPI)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  Document    │ │   Vector     │ │      AI      │        │
│  │  Processor   │ │   Store      │ │   Analyzer   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                            │
                 ┌──────────┼──────────┐
                 │          │          │
          ┌──────▼───┐ ┌────▼───┐ ┌───▼────┐
          │PostgreSQL│ │ChromaDB│ │OpenAI  │
          │Database  │ │Vectors │ │Models  │
          └──────────┘ └────────┘ └────────┘
```

## ✨ Features

### 🔍 Advanced Search
- **Semantic Search**: Find documents by meaning, not just keywords
- **Keyword Search**: Traditional full-text search with filters
- **Hybrid Search**: Combine semantic and keyword approaches
- **Citation Search**: Find documents by legal citations
- **Advanced Filters**: Filter by jurisdiction, document type, date range

### 🧠 AI-Powered Analysis
- **Legal Reasoning**: Get comprehensive analysis of legal issues
- **Document Summarization**: AI-generated summaries and key points
- **Citation Extraction**: Automatic identification of legal citations
- **Precedent Analysis**: Find related cases and precedents
- **Counterargument Detection**: Identify alternative legal perspectives

### 📄 Document Processing
- **Multi-Format Support**: PDF, DOCX, TXT files
- **OCR Capability**: Extract text from scanned documents
- **Intelligent Chunking**: Break documents into semantic sections
- **Metadata Extraction**: Automatic categorization and tagging
- **Legal Entity Recognition**: Identify legal concepts and entities

### 📊 Analytics & Insights
- **Document Analytics**: Readability scores, complexity analysis
- **Search Analytics**: Track popular queries and trends
- **Usage Statistics**: Monitor system performance and user behavior
- **Similar Document Detection**: Find related documents automatically

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+ (production) or SQLite (development)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd law_ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Database Setup

```bash
# For development (SQLite)
cd backend
python -m app.core.database

# For production (PostgreSQL)
# Ensure PostgreSQL is running and create database
createdb legal_ai
```

### 5. Start Development Servers

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

Visit `http://localhost:3000` to access the application.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenRouter AI Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# AI Model Configuration
DOCUMENT_ANALYSIS_MODEL=anthropic/claude-3-sonnet
LEGAL_REASONING_MODEL=anthropic/claude-3-opus
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Database Configuration
DATABASE_URL=sqlite:///./legal_ai.db  # Development
# DATABASE_URL=postgresql://user:password@localhost/legal_ai  # Production

# Vector Database
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION_NAME=legal_documents

# File Processing
MAX_FILE_SIZE_MB=50
SUPPORTED_FILE_TYPES=.pdf,.docx,.txt
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Search Configuration
MAX_SEARCH_RESULTS=50
SIMILARITY_THRESHOLD=0.7
ENABLE_HYBRID_SEARCH=true

# Optional: Advanced Features
REDIS_URL=redis://localhost:6379  # For caching
ELASTICSEARCH_URL=http://localhost:9200  # For advanced search
```

### Model Configuration

The system supports various AI models through OpenRouter:

- **Document Analysis**: `anthropic/claude-3-sonnet` (default)
- **Legal Reasoning**: `anthropic/claude-3-opus` (default)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`

## 📁 Project Structure

```
law_ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   └── requirements.txt
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── styles/            # CSS/Tailwind
│   └── package.json
├── pdf/                       # Legal documents
└── README.md
```

## 🎯 Usage Guide

### 1. Document Upload

1. Navigate to the Upload page
2. Drag and drop PDF, DOCX, or TXT files
3. Wait for processing to complete
4. Documents are automatically indexed for search

### 2. Search Documents

**Semantic Search:**
```
"What are the requirements for establishing breach of contract?"
```

**Keyword Search:**
```
contract AND breach AND damages
```

**Citation Search:**
```
cite:"42 U.S.C. § 1983"
```

### 3. AI Analysis

1. Go to the Analysis page
2. Enter your legal question
3. Select analysis type (General, Case Law, Statutory, Precedent)
4. Choose options (citations, counterarguments)
5. Get comprehensive AI-powered analysis

### 4. Document Viewing

- View document content in organized chunks
- Access metadata and legal concepts
- See AI-generated analysis and key points
- Find similar documents automatically

## 🔌 API Documentation

### Authentication

Currently using API key authentication. Include your API key in the header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/documents
```

### Key Endpoints

- `POST /api/documents/upload` - Upload documents
- `GET /api/search/semantic` - Semantic search
- `GET /api/search/keyword` - Keyword search
- `POST /api/analysis/analyze` - AI analysis
- `GET /api/documents/{id}` - Get document details

Full API documentation is available at `http://localhost:8000/docs` when running the backend.

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Container Build

```bash
# Backend
docker build -t legal-ai-backend ./backend

# Frontend
docker build -t legal-ai-frontend ./frontend
```

## 📊 Performance & Scalability

### Database Optimization

- Indexed fields for fast search queries
- Chunked document storage for efficient retrieval
- Vector embeddings for semantic similarity

### Caching Strategy

- Redis for search result caching
- Application-level caching for expensive operations
- CDN for static assets in production

### Monitoring

- Built-in logging for all operations
- Performance metrics collection
- Error tracking and alerting

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Run full test suite
npm run test:integration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation as needed

## 📋 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Database connection errors:**
```bash
# Check database configuration in .env
# Ensure PostgreSQL is running (production)
```

**Frontend build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Logs and Debugging

- Backend logs: Check console output or log files
- Frontend logs: Open browser developer tools
- Database logs: Check PostgreSQL/SQLite logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for AI model access
- ChromaDB for vector database
- FastAPI and React communities
- Legal professionals who provided domain expertise

## 📞 Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Contact the development team

---

**Built with ❤️ for the legal community** 