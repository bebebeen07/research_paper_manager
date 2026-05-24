"""
SQLAlchemy Data Models

Defines the structure of data in the SQLite database.

Key Concepts:
- Model: Represents a table in the database
- Column: Represents a field/column
- Relationship: Links tables together
- Types: Integer, String, DateTime, etc.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemly.sql import func
from datetime import datetime
import uuid
from app.database import Base


class Paper(Base):
    """
    Represents a research paper in the database.
    
    Table name: papers
    Each paper has:
    - id: Unique identifier (UUID)
    - title: Paper title
    - filename: Uploaded file name
    - original_filename: What user named the file
    - file_path: Where the file is stored
    - content: Extracted text from PDF
    - summary: AI-generated summary
    - created_at: When uploaded
    - updated_at: Last modification time
    """
    
    __tablename__ = "papers"
    
    # Primary Key - unique identifier for each paper
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Paper metadata
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    
    # Content
    content = Column(Text, nullable=True)  # Extracted text from PDF
    summary = Column(Text, nullable=True)  # AI summary
    
    # Status flags
    is_summarized = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Paper(id={self.id}, title={self.title})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "summary": self.summary,
            "is_summarized": self.is_summarized,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
