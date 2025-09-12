"""
Database initialization and migration check for the RAG system.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text
from database import Base, engine, SessionLocal

# Import emoji-safe logging
try:
    from safe_print import safe_log_info, safe_log_error, safe_log_warning
except ImportError:
    # Fallback if safe_print not available
    def safe_log_info(msg): print(f"[INFO] {msg}")
    def safe_log_error(msg): print(f"[ERROR] {msg}")
    def safe_log_warning(msg): print(f"[WARNING] {msg}")

def check_and_migrate():
    """Check database schema and create tables if missing."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ["uploaded_files", "user_queries", "system_status"]
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            safe_log_warning(f"Database schema missing tables: {missing_tables}")
            safe_log_info("Creating missing tables...")
            Base.metadata.create_all(bind=engine)
            safe_log_info("Database schema created successfully")
        else:
            safe_log_info("Database schema verified")
            
        # Test database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            safe_log_info("Database connection test passed")
        except Exception as e:
            safe_log_error(f"Database connection test failed: {e}")
        finally:
            db.close()
            
    except Exception as e:
        safe_log_error(f"Database migration check failed: {e}")
        raise

if __name__ == "__main__":
    check_and_migrate()
