# Enhanced RAG System

A powerful Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, and FAISS for intelligent document question-answering.

## Features

- **Document Upload**: Support for PDF and TXT files
- **Intelligent Search**: FAISS vector store for semantic search
- **AI-Powered Q&A**: Ollama LLM integration for natural language responses
- **Database Tracking**: SQLite database for document and query management
- **Web Interface**: Modern, responsive frontend
- **Health Monitoring**: Comprehensive system status checks

## Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rag-system.git
cd rag-system

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the system
python main.py
```

Visit: http://localhost:8000

### Deploy to Vercel
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **AI/ML**: LangChain, FAISS, Sentence Transformers
- **Database**: SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript
- **LLM**: Ollama (Mistral)

## Project Structure

```
rag-system/
├── src/
│   ├── api.py          # FastAPI application
│   ├── database.py     # Database models
│   └── init_db.py      # Database initialization
├── static/             # Frontend assets
├── uploads/            # Uploaded documents
├── data/              # FAISS vector store
├── main.py            # Vercel entry point
├── requirements.txt   # Python dependencies
└── vercel.json       # Vercel configuration
```

## Configuration

### Environment Variables
- `OLLAMA_URL`: Ollama server URL (default: http://localhost:11434)
- `PYTHONPATH`: Python path for imports

### Database
The system automatically creates and manages a SQLite database with:
- Document metadata
- Query history
- System statistics

## API Endpoints

- `GET /` - Web interface
- `GET /api/health` - System health check
- `GET /api/documents` - List uploaded documents
- `POST /uploadfile/` - Upload documents
- `POST /query` - Ask questions
- `GET /docs` - API documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the [troubleshooting guide](DEPLOYMENT.md#troubleshooting)
2. Open an issue on GitHub
3. Review the API documentation at `/docs`

---

**Built with FastAPI and LangChain**
