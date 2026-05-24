"""
Database Configuration

This module sets up SQLite connection and provides database utilities.

Key Concepts:
- SQLAlchemy: Python ORM (Object-Relational Mapping) for database operations
- Engine: Connection pool to the database
- SessionLocal: Factory for creating database sessions
- Base: SQLAlchemy declarative base for defining models
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
import os


# Create database engine
# SQLite uses a file-based database (data/papers.db)
# StaticPool: keeps connection open (good for SQLite, single-threaded)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    poolclass=StaticPool,  # Use static pool for SQLite
)

# SessionLocal is a factory for creating database sessions
# Each session is like a "transaction" - read/write data within it
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
# Models inherit from this to define database tables
Base = declarative_base()


def get_db():
    """
    Dependency injection for database sessions.
    
    Usage in FastAPI routes:
        @app.get("/papers")
        async def get_papers(db: Session = Depends(get_db)):
            papers = db.query(Paper).all()
            return papers
    
    Why use Depends?
    - Automatic session creation and cleanup
    - Type hints work correctly
    - Testable and mockable
    """
    db = SessionLocal()
    try:
        yield db  # Provide session to route
    finally:
        db.close()  # Always close session when done


def init_db():
    """
    Initialize database - create all tables.
    
    Called on application startup.
    Safe to call multiple times - only creates missing tables.
    """
    # Create all tables defined in models.py
    Base.metadata.create_all(bind=engine)
    
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
