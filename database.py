"""
Database models and functions for the RAG system.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database configuration
DATABASE_URL = "sqlite:///./rag_system.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database Models
class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String)
    file_type = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    chunks_created = Column(Integer, default=0)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    document_count = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)

class UserQuery(Base):
    __tablename__ = "user_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text)
    response_text = Column(Text)
    query_time = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float, nullable=True)
    file_id = Column(Integer, nullable=True)  # Reference to uploaded file
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

class SystemStatus(Base):
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String, unique=True, index=True)
    status_value = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)

# Database functions
def init_database():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_uploaded_file(db: Session, filename: str, file_path: str, file_size: int, 
                     original_filename: str = None, file_type: str = None):
    """Add a new uploaded file record."""
    db_file = UploadedFile(
        filename=filename,
        original_filename=original_filename or filename,
        file_type=file_type or "unknown",
        file_path=file_path,
        file_size=file_size
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def update_file_processing_status(db: Session, file_id: int, status: str, error: str = None, 
                                document_count: int = None, processing_time: float = None,
                                processed: bool = None, chunks_created: int = None):
    """Update file processing status."""
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if db_file:
        db_file.processing_status = status
        if error:
            db_file.processing_error = error
        if document_count is not None:
            db_file.document_count = document_count
        if processing_time is not None:
            db_file.processing_time = processing_time
        if processed is not None:
            db_file.processed = processed
        if chunks_created is not None:
            db_file.chunks_created = chunks_created
        db.commit()
        return db_file
    return None

def add_user_query(db: Session, question: str, answer: str = None, 
                  processing_time: float = None, documents_used: int = None,
                  chunks_retrieved: int = None, success: bool = True, 
                  error_message: str = None):
    """Add a new user query record."""
    db_query = UserQuery(
        query_text=question,
        response_text=answer,
        response_time=processing_time,
        is_successful=success,
        error_message=error_message
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def get_file_stats(db: Session):
    """Get file statistics."""
    total_files = db.query(UploadedFile).count()
    processed_files = db.query(UploadedFile).filter(UploadedFile.processing_status == "completed").count()
    failed_files = db.query(UploadedFile).filter(UploadedFile.processing_status == "failed").count()
    pending_files = db.query(UploadedFile).filter(UploadedFile.processing_status == "pending").count()
    
    return {
        "total_files": total_files,
        "processed_files": processed_files,
        "failed_files": failed_files,
        "pending_files": pending_files
    }

def get_query_stats(db: Session):
    """Get query statistics."""
    total_queries = db.query(UserQuery).count()
    successful_queries = db.query(UserQuery).filter(UserQuery.is_successful == True).count()
    failed_queries = db.query(UserQuery).filter(UserQuery.is_successful == False).count()
    
    return {
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "failed_queries": failed_queries
    }

def update_system_status(db: Session, vector_store_loaded: bool = None, total_documents: int = None, 
                        total_queries: int = None, ollama_status: str = None):
    """Update system status."""
    status = db.query(SystemStatus).first()
    if not status:
        status = SystemStatus()
        db.add(status)
    
    status.last_update = datetime.utcnow()
    if vector_store_loaded is not None:
        status.vector_store_loaded = vector_store_loaded
    if total_documents is not None:
        status.total_documents = total_documents
    if total_queries is not None:
        status.total_queries = total_queries
    if ollama_status is not None:
        status.ollama_status = ollama_status
    
    db.commit()
    db.refresh(status)
    return status
