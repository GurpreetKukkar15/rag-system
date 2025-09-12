import os
import sys
import shutil
import time
import requests
import traceback
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models and functions
from database import (
    init_database, get_db, add_uploaded_file, update_file_processing_status,
    add_user_query, get_file_stats, get_query_stats, update_system_status,
    UploadedFile, UserQuery, SystemStatus
)

# Import RAG components
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Global variables for RAG components
vector_store = None
embeddings = None
llm = None

# Configuration
DATA_DIR = "data"
UPLOAD_DIR = "uploads"
FAISS_INDEX_PATH = "data/faiss_index"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("static", exist_ok=True)

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    processing_time: float
    documents_used: int
    chunks_retrieved: int
    query_id: int

class FileUploadResponse(BaseModel):
    message: str
    file_id: int
    filename: str
    file_size: int

class DocumentInfo(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_date: str  # This will be populated from upload_time field
    processed: bool
    chunks_created: int
    processing_status: str

class SystemStats(BaseModel):
    files: dict
    queries: dict
    system: dict

# Define the lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on application startup
    global vector_store, embeddings, llm
    
    print("[STARTUP] Starting Enhanced RAG System with Database...")
    
    # Initialize database
    init_database()
    print("[OK] Database initialized")
    
    # Load embeddings
    print("Loading embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load or create FAISS index
    try:
        if os.path.exists(FAISS_INDEX_PATH):
            print("Loading FAISS vector store...")
            vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            print("[OK] FAISS vector store loaded successfully")
        else:
            print("No existing FAISS index found. Will create one when documents are uploaded.")
            vector_store = None
    except Exception as e:
        print(f"[WARNING] Error loading FAISS index: {e}")
        vector_store = None
    
    # Initialize LLM (using Ollama)
    try:
        llm = OllamaLLM(model="mistral")
        print("[OK] LLM initialized (using Ollama: mistral)")
    except Exception as e:
        print(f"[WARNING] Error initializing Ollama LLM: {e}")
        print("   Falling back to test LLM...")
        from langchain_community.llms.fake import FakeListLLM
        llm = FakeListLLM(responses=["I'm a test LLM. This is a placeholder response."])
        print("[OK] LLM initialized (using test LLM fallback)")
    
    print("[OK] RAG resources loaded successfully")
    
    yield  # This is where the application runs
    
    # This code runs on application shutdown
    print("Application shutdown event: Releasing resources...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Enhanced RAG System with Database", 
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": False,
        "faiss": False,
        "llm": False,
        "ollama": False
    }
    
    # Database check
    try:
        from database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        status["database"] = True
        db.close()
    except Exception as e:
        status["database_error"] = str(e)
    
    # FAISS check
    try:
        if vector_store is not None:
            _ = vector_store.index.ntotal
            status["faiss"] = True
            status["faiss_documents"] = vector_store.index.ntotal
    except Exception as e:
        status["faiss_error"] = str(e)
    
    # LLM check
    try:
        if llm is not None:
            status["llm"] = True
            status["llm_type"] = type(llm).__name__
    except Exception as e:
        status["llm_error"] = str(e)
    
    # Ollama check
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            status["ollama"] = True
            status["ollama_models"] = [model["name"] for model in models]
    except Exception as e:
        status["ollama_error"] = str(e)
    
    # Overall status
    if not all([status["database"], status["faiss"], status["llm"]]):
        status["status"] = "degraded"
    
    return status

# Get system statistics
@app.get("/api/stats", response_model=SystemStats)
async def get_system_stats(db: Session = Depends(get_db)):
    files_stats = get_file_stats(db)
    queries_stats = get_query_stats(db)
    
    return SystemStats(
        files=files_stats,
        queries=queries_stats,
        system={
            "vector_store_loaded": vector_store is not None,
            "total_documents": files_stats["processed_files"],
            "system_version": "2.0.0"
        }
    )

# List all documents
@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents(db: Session = Depends(get_db)):
    files = db.query(UploadedFile).order_by(UploadedFile.upload_time.desc()).all()
    
    return [
        DocumentInfo(
            id=file.id,
            filename=file.filename,
            original_filename=file.original_filename,
            file_type=file.file_type,
            file_size=file.file_size,
            upload_date=file.upload_time.isoformat(),
            processed=file.processed,
            chunks_created=file.chunks_created,
            processing_status=file.processing_status
        )
        for file in files
    ]

# Upload file endpoint
@app.post("/uploadfile/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Add to database
        file_record = add_uploaded_file(
            db=db,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_extension[1:].upper(),
            file_size=file_size
        )
        
        # Process file in background (simplified for now)
        try:
            process_single_document(file_path, file_record.id, db)
        except Exception as e:
            update_file_processing_status(
                db=db,
                file_id=file_record.id,
                processed=False,
                status="failed",
                error=str(e)
            )
        
        return FileUploadResponse(
            message=f"File '{file.filename}' uploaded successfully",
            file_id=file_record.id,
            filename=unique_filename,
            file_size=file_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

# Process single document
def process_single_document(file_path: str, file_id: int, db: Session):
    global vector_store
    
    try:
        # Update status to processing
        update_file_processing_status(
            db=db,
            file_id=file_id,
            processed=False,
            status="processing"
        )
        
        # Load document
        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')
        
        documents = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create or update FAISS index
        if vector_store is None:
            vector_store = FAISS.from_documents(chunks, embeddings)
        else:
            vector_store.add_documents(chunks)
        
        # Save FAISS index
        vector_store.save_local(FAISS_INDEX_PATH)
        
        # Update file status
        update_file_processing_status(
            db=db,
            file_id=file_id,
            processed=True,
            chunks_created=len(chunks),
            status="completed"
        )
        
        # Update system status
        update_system_status(
            db=db,
            vector_store_loaded=True,
            total_documents=db.query(UploadedFile).filter(UploadedFile.processed == True).count()
        )
        
        print(f"[OK] Processed file {file_path}: {len(chunks)} chunks created")
        
    except Exception as e:
        print(f"[ERROR] Error processing file {file_path}: {e}")
        update_file_processing_status(
            db=db,
            file_id=file_id,
            processed=False,
            status="failed",
            error=str(e)
        )
        raise

# Delete document
@app.delete("/api/documents/{file_id}")
async def delete_document(file_id: int, db: Session = Depends(get_db)):
    global vector_store
    
    try:
        # Get file record
        file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete physical file
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        
        # Delete from database
        db.delete(file_record)
        db.commit()
        
        # Note: In a production system, you'd want to rebuild the FAISS index
        # For now, we'll just mark that it needs rebuilding
        print(f"[WARNING] File {file_record.filename} deleted. FAISS index may need rebuilding.")
        
        return {"message": f"File '{file_record.original_filename}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_documents(
    query: QueryRequest,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    try:
        # Debug: Check vector store status
        if vector_store is None:
            print("[ERROR] Vector store is None")
            raise HTTPException(status_code=400, detail="No documents available. Please upload some documents first.")
        
        if not hasattr(vector_store, 'index') or vector_store.index.ntotal == 0:
            print(f"[ERROR] Vector store has no documents. ntotal: {getattr(vector_store, 'index', {}).ntotal if hasattr(vector_store, 'index') else 'no index'}")
            raise HTTPException(status_code=400, detail="No documents available. Please upload some documents first.")
        
        if llm is None:
            print("[ERROR] LLM is None")
            raise HTTPException(status_code=500, detail="LLM not available")
        
        print(f"[DEBUG] Processing query: {query.question}")
        print(f"[DEBUG] Vector store has {vector_store.index.ntotal} documents")
        
        # Retrieve relevant documents
        retrieved_docs = vector_store.similarity_search(query.question, k=3)
        print(f"[DEBUG] Retrieved {len(retrieved_docs)} documents")
        
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        print(f"[DEBUG] Context length: {len(context)} characters")
        
        # Create prompt
        prompt_template = PromptTemplate.from_template(
            "Use the following context to answer the question.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
        )
        
        # Generate response with fallback
        print("[DEBUG] Invoking LLM...")
        try:
            rag_chain = prompt_template | llm
            response = rag_chain.invoke({"context": context, "question": query.question})
            print(f"[DEBUG] LLM response: {response[:100]}...")
        except Exception as llm_error:
            print(f"[WARNING] LLM failed: {llm_error}")
            print("[DEBUG] Using fallback response...")
            # Fallback response when LLM fails
            response = f"Based on the available documents, I found {len(retrieved_docs)} relevant sections. However, I'm experiencing technical difficulties with the language model. Here's what I found:\n\n{context[:500]}..."
        
        processing_time = time.time() - start_time
        
        # Save query to database
        query_record = add_user_query(
            db=db,
            question=query.question,
            answer=response,
            processing_time=processing_time,
            documents_used=len(retrieved_docs),
            chunks_retrieved=len(retrieved_docs),
            success=True
        )
        
        # Update system stats
        update_system_status(
            db=db,
            total_queries=db.query(UserQuery).count()
        )
        
        return QueryResponse(
            answer=response,
            processing_time=round(processing_time, 2),
            documents_used=len(retrieved_docs),
            chunks_retrieved=len(retrieved_docs),
            query_id=query_record.id
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Print full traceback to logs
        tb_str = traceback.format_exc()
        print(f"[ERROR] Query processing failed:\n{tb_str}")
        
        # Save failed query to database
        try:
            add_user_query(
                db=db,
                question=query.question,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
        except Exception as db_exc:
            print(f"[ERROR] Failed to save failed query: {db_exc}")
        
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return FileResponse("static/enhanced_index.html")

# Get recent queries
@app.get("/api/queries")
async def get_recent_queries(limit: int = 10, db: Session = Depends(get_db)):
    queries = db.query(UserQuery).order_by(UserQuery.query_date.desc()).limit(limit).all()
    
    return [
        {
            "id": query.id,
            "question": query.question,
            "answer": query.answer,
            "query_date": query.query_date.isoformat(),
            "processing_time": query.processing_time,
            "success": query.success
        }
        for query in queries
    ]