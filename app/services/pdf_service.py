"""
PDF Processing Service

Handles PDF file operations: uploading, storing, and extracting text.

Key Concepts:
- Service layer: Separate business logic from API routes
- Error handling: Graceful failure with meaningful messages
- File validation: Check file type and size before processing
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4
from fastapi import UploadFile, HTTPException, status
from app.config import settings

# PyPDF2 or pdfplumber for PDF processing
try:
    import PyPDF2
    PDF_LIBRARY = "PyPDF2"
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = "pdfplumber"
    except ImportError:
        PDF_LIBRARY = None


class PDFService:
    """Service for handling PDF file operations"""
    
    @staticmethod
    async def validate_upload(file: UploadFile) -> None:
        """
        Validate uploaded file before saving.
        
        Args:
            file: UploadFile from FastAPI
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check file extension
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [f".{ext}" for ext in settings.ALLOWED_EXTENSIONS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {settings.ALLOWED_EXTENSIONS} files allowed"
            )
        
        # Check file size by reading content
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large (max {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB)"
            )
        
        # Reset file pointer for later reading
        await file.seek(0)
    
    @staticmethod
    async def save_upload(file: UploadFile) -> str:
        """
        Save uploaded file to disk.
        
        Args:
            file: UploadFile from FastAPI
            
        Returns:
            Stored filename (UUID-based)
        """
        # Generate unique filename to prevent collisions
        # Use UUID4 for security: prevents users from accessing each other's files
        file_ext = Path(file.filename).suffix
        stored_filename = f"{uuid4()}{file_ext}"
        file_path = Path("uploads") / stored_filename
        
        # Save file to disk
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
        
        return stored_filename
    
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            if PDF_LIBRARY == "PyPDF2":
                return PDFService._extract_with_pypdf2(file_path)
            elif PDF_LIBRARY == "pdfplumber":
                return PDFService._extract_with_pdfplumber(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
    
    @staticmethod
    def _extract_with_pypdf2(file_path: str) -> str:
        """Extract text using PyPDF2"""
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    @staticmethod
    def _extract_with_pdfplumber(file_path: str) -> str:
        """Extract text using pdfplumber"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    
    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """
        Delete file from disk.
        Useful if extraction fails and we want to clean up.
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file: {e}")


# Create global instance
pdf_service = PDFService()
