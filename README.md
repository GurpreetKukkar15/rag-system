# RAG System

A Retrieval-Augmented Generation system built with FastAPI, LangChain, and FAISS for intelligent document question-answering.

## Features

- Document upload and processing (PDF, TXT)
- Semantic search using FAISS vector store
- AI-powered Q&A with Ollama LLM integration
- SQLite database for tracking documents and queries
- Modern web interface with real-time status
- Health monitoring and system diagnostics

## Technology Stack

- **Backend**: FastAPI, Uvicorn
- **AI/ML**: LangChain, FAISS, Sentence Transformers
- **Database**: SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript
- **LLM**: Ollama (Mistral, Phi, TinyLlama)

## Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed and running
- 4GB+ RAM recommended

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rag-system.git
   cd rag-system
   ```

2. **Setup environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # source venv/bin/activate     # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama**
   ```bash
   ollama serve
   ```

5. **Install model (optional)**
   ```bash
   ollama pull mistral
   ```

6. **Run application**
   ```bash
   python src/main.py
   ```

7. **Access application**
   - Web Interface: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

### Web Interface

1. Upload documents by dragging and dropping files
2. Ask questions using the query interface
3. View AI-generated answers based on your documents
4. Monitor system status and statistics

### API Endpoints

- `GET /` - Web interface
- `GET /api/health` - System health check
- `GET /api/documents` - List uploaded documents
- `POST /uploadfile/` - Upload documents
- `POST /query` - Ask questions
- `GET /api/stats` - System statistics

### Example API Usage

```bash
# Upload document
curl -X POST "http://localhost:8000/uploadfile/" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"

# Ask question
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this document about?"}'

# Check health
curl http://localhost:8000/api/health
```

## Project Structure

```
rag-system/
├── src/
│   ├── api.py              # FastAPI application
│   ├── main.py             # Entry point
│   ├── ingestion.py        # Document processing
│   └── safe_print.py       # Logging utilities
├── static/                 # Frontend assets
├── uploads/                # Uploaded documents
├── data/                   # FAISS vector store
├── logs/                   # System logs
├── database.py             # Database models
├── init_db.py             # Database initialization
└── requirements.txt        # Dependencies
```

## Configuration

### Environment Variables

- `OLLAMA_URL`: Ollama server URL (default: http://localhost:11434)

### Database

SQLite database automatically manages:
- Document metadata and processing status
- Query history and performance metrics
- System statistics

## Troubleshooting

### Common Issues

1. **Port 8000 in use**
   ```bash
   taskkill /IM python.exe /F
   ```

2. **Ollama not responding**
   ```bash
   ollama serve
   curl http://localhost:11434/api/tags
   ```

3. **Memory issues**
   - Use smaller models (phi, tinyllama)
   - Close other applications
   - Check available RAM

4. **Database errors**
   ```bash
   rm rag_system.db
   python init_db.py
   ```

### Health Check

Visit http://localhost:8000/api/health to verify:
- Database connectivity
- FAISS vector store status
- LLM availability
- System statistics

## Development

### Development Mode

```bash
uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

### Database Management

```bash
python init_db.py
```

## Performance Tips

1. Use appropriate models for your hardware
2. Limit document size for faster processing
3. Monitor memory usage during operation
4. Regular database maintenance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License

## Support

For issues:
1. Check troubleshooting section
2. Review API documentation at `/docs`
3. Open an issue on GitHub
4. Check logs in `logs/` directory

---

Built with FastAPI and LangChain
