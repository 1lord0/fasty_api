# 📄 PDF RAG API v2.0

Advanced PDF Retrieval-Augmented Generation (RAG) system with FastAPI, ChromaDB, and Groq LLM.

## 🌟 Features

### Core Features
- ✅ **PDF Processing**: Upload and process PDF documents with intelligent chunking
- ✅ **Vector Search**: Semantic search using sentence transformers and ChromaDB
- ✅ **RAG System**: Question answering with context from uploaded documents
- ✅ **LLM Integration**: Groq API integration with Llama models

### Advanced Features
- 🔧 **Configuration Management**: Pydantic-based settings with environment variables
- 📊 **Database Integration**: SQLAlchemy async database for metadata and tracking
- 📝 **Professional Logging**: Loguru with rotation and multiple log levels
- 🐳 **Dockerized**: Production-ready Docker setup
- 🧪 **Testing**: Comprehensive test suite with pytest
- 📈 **Monitoring**: Built-in statistics and query history
- 🔒 **Security**: Rate limiting and API key support (configurable)
- ⚡ **Performance**: GZip compression and optimized chunking

## 🏗️ Architecture

```
fast_api_project/
├── api/                    # API routes
│   ├── routes.py          # Main API endpoints
│   └── __init__.py
├── config/                 # Configuration
│   ├── settings.py        # Pydantic settings
│   └── __init__.py
├── db/                     # Database
│   ├── database.py        # DB connection
│   ├── models.py          # SQLAlchemy models
│   └── vectordb.py        # Vector DB config
├── models/                 # Pydantic models
│   └── schemas.py         # Request/Response models
├── services/              # Business logic
│   ├── llm_service.py    # LLM integration
│   ├── pdf_processor.py  # PDF processing
│   ├── vector_service.py # Vector search
│   └── __init__.py
├── utils/                 # Utilities
│   ├── logger.py         # Logging setup
│   └── __init__.py
├── tests/                 # Test suite
│   ├── test_api.py       # API tests
│   └── __init__.py
├── data/                  # Data directory
│   ├── chroma/           # Vector database
│   └── uploads/          # Uploaded files
├── logs/                  # Log files
├── main.py               # FastAPI app
├── streamlit_app.py      # Streamlit UI
├── requirements.txt      # Dependencies
├── Dockerfile           # Docker image
├── docker-compose.yml   # Docker compose
└── .env.example        # Environment template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Groq API Key ([Get it here](https://console.groq.com/))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo>
cd fast_api_project
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Using Docker

1. **Build and run**
```bash
docker-compose up --build
```

2. **Stop**
```bash
docker-compose down
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### 📤 Upload PDF
```bash
POST /upload
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

#### ❓ Ask Question
```bash
POST /ask?question=What is this about?&k=5

curl -X POST "http://localhost:8000/ask?question=What%20is%20this%20about&k=5"
```

#### 📊 Get Statistics
```bash
GET /stats

curl "http://localhost:8000/stats"
```

#### 📄 List Documents
```bash
GET /documents?limit=50&offset=0

curl "http://localhost:8000/documents"
```

#### 🔍 Query History
```bash
GET /queries?limit=50&offset=0

curl "http://localhost:8000/queries"
```

#### ❤️ Health Check
```bash
GET /health

curl "http://localhost:8000/health"
```

## 🎨 Streamlit UI

Run the interactive UI:
```bash
streamlit run streamlit_app.py
```

Features:
- Upload PDFs through web interface
- Ask questions with visual feedback
- View document sources
- Adjust search parameters

## 🧪 Testing

Run tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## ⚙️ Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key | Required |
| `LLM_MODEL` | LLM model name | `llama-3.1-8b-instant` |
| `MAX_FILE_SIZE_MB` | Max upload size | `50` |
| `CHUNK_SIZE_LARGE` | Chunk size for large docs | `800` |
| `DEFAULT_SEARCH_K` | Default search results | `5` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📊 Database Schema

### Documents Table
- `doc_id`: Unique document ID
- `filename`: Original filename
- `pdf_hash`: MD5 hash (deduplication)
- `pages`: Number of pages
- `chunks`: Number of text chunks
- `status`: Processing status
- `created_at`: Upload timestamp

### Queries Table
- `question`: User question
- `answer`: LLM response
- `doc_id`: Related document (optional)
- `k_value`: Number of chunks used
- `response_time`: Processing time
- `status`: Query status
- `created_at`: Query timestamp

## 🔧 Advanced Usage

### Custom Chunking Strategy
Edit `services/pdf_processor.py`:
```python
def get_chunk_params(text):
    length = len(text)
    if length < 10_000:
        return 300, 50  # chunk_size, chunk_overlap
    elif length < 50_000:
        return 500, 100
    else:
        return 800, 150
```

### Multiple LLM Models
Edit `config/settings.py`:
```python
LLM_MODEL: str = "llama-3.3-70b-versatile"  # More powerful model
```

### Enable Redis Caching
1. Uncomment Redis service in `docker-compose.yml`
2. Set `USE_CACHE=true` in `.env`

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

**2. Database Errors**
```bash
# Delete and recreate database
rm data/app.db
python main.py  # Will auto-create
```

**3. Vector DB Issues**
```bash
# Clear ChromaDB
rm -rf data/chroma/*
```

**4. API Key Errors**
```bash
# Verify GROQ_API_KEY in .env
echo $GROQ_API_KEY
```

## 📈 Performance Tips

1. **Batch Processing**: For multiple PDFs, use async upload
2. **Chunk Size**: Adjust based on document type
3. **Search K**: Start with k=5, increase for better context
4. **Caching**: Enable Redis for frequently asked questions
5. **Database**: Use PostgreSQL for production (update DATABASE_URL)

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable `ENABLE_API_KEY=true`
- [ ] Configure proper CORS origins
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable Redis caching
- [ ] Set up reverse proxy (nginx)
- [ ] Configure SSL/TLS
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For issues and questions:
- GitHub Issues
- Documentation: `/docs` endpoint

## 🙏 Acknowledgments

- FastAPI
- ChromaDB
- Groq
- Sentence Transformers
- SQLAlchemy

---

Made with ❤️ for better document Q&A
