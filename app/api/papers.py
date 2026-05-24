"""
Paper API Routes

Defines all endpoints for paper management:
- POST /upload - Upload a new paper
- GET / - List all papers
- GET /{paper_id} - Get paper details
- GET /{paper_id}/summary - Get or generate summary
- DELETE /{paper_id} - Delete a paper

Key Concepts:
- Router: Organize related endpoints
- Depends: Dependency injection (database, authentication, etc.)
- HTTPException: Return error responses
- UploadFile: FastAPI's file upload handling
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os

# Import models, schemas, and services
from app.database import get_db
from app.models import Paper
from app.schemas import PaperResponse, PaperSummaryResponse, ErrorResponse
from app.services.pdf_service import pdf_service
from app.services.ai_service import ai_service

# Create router for paper endpoints
router = APIRouter()


# ============================================================================
# POST /api/papers/upload - Upload a new paper
# ============================================================================
@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new research paper PDF.
    
    Args:
        file: PDF file to upload
        db: Database session (injected)
        
    Returns:
        PaperResponse: Created paper details
        
    Errors:
        400: Invalid file format or too large
        500: Server error during upload
        
    Example:
        curl -X POST "http://localhost:8000/api/papers/upload" \\
             -F "file=@paper.pdf"
    """
    
    # Step 1: Validate the uploaded file
    await pdf_service.validate_upload(file)
    
    # Step 2: Save file to disk
    stored_filename = await pdf_service.save_upload(file)
    file_path = f"uploads/{stored_filename}"
    
    try:
        # Step 3: Extract text from PDF
        # This might fail if PDF is corrupted or not readable
        content = pdf_service.extract_text(file_path)
        
        # Step 4: Use filename (without extension) as title
        # In production, you might extract this from PDF metadata
        title = file.filename.replace(".pdf", "").replace("_", " ")
        
        # Step 5: Create Paper record in database
        paper = Paper(
            title=title,
            original_filename=file.filename,
            filename=stored_filename,
            file_path=file_path,
            content=content,  # Stored for later AI processing
        )
        
        # Step 6: Save to database
        db.add(paper)
        db.commit()
        db.refresh(paper)  # Reload to get database-generated fields
        
        return paper
        
    except Exception as e:
        # If anything fails, clean up the uploaded file
        pdf_service.cleanup_file(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


# ============================================================================
# GET /api/papers/ - List all papers
# ============================================================================
@router.get("/", response_model=List[PaperResponse])
async def list_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all uploaded papers with pagination.
    
    Args:
        skip: Number of papers to skip (for pagination)
        limit: Maximum number to return
        db: Database session (injected)
        
    Returns:
        List[PaperResponse]: List of papers
        
    Example:
        curl "http://localhost:8000/api/papers/"
        curl "http://localhost:8000/api/papers/?skip=10&limit=20"
    
    Pagination tip:
        To get page 2 with 10 items per page:
        skip = (page - 1) * limit = (2 - 1) * 10 = 10
    """
    papers = db.query(Paper).offset(skip).limit(limit).all()
    return papers


# ============================================================================
# GET /api/papers/{paper_id} - Get single paper details
# ============================================================================
@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific paper.
    
    Args:
        paper_id: UUID of the paper
        db: Database session (injected)
        
    Returns:
        PaperResponse: Paper details
        
    Errors:
        404: Paper not found
        
    Example:
        curl "http://localhost:8000/api/papers/123e4567-e89b-12d3-a456-426614174000"
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )
    
    return paper


# ============================================================================
# GET /api/papers/{paper_id}/summary - Get or generate summary
# ============================================================================
@router.get("/{paper_id}/summary", response_model=PaperSummaryResponse)
async def get_or_create_summary(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """
    Get summary of a paper. Generates if not already created.
    
    Args:
        paper_id: UUID of the paper
        db: Database session (injected)
        
    Returns:
        PaperSummaryResponse: Paper summary
        
    Errors:
        404: Paper not found
        500: AI service unavailable
        
    Example:
        curl "http://localhost:8000/api/papers/123e4567-e89b-12d3-a456-426614174000/summary"
    
    Note:
        First call generates summary (might take a few seconds).
        Subsequent calls return cached summary instantly.
    """
    
    # Step 1: Find the paper
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )
    
    # Step 2: Check if summary already exists
    if paper.is_summarized and paper.summary:
        return PaperSummaryResponse(
            id=paper.id,
            title=paper.title,
            summary=paper.summary,
            generated_at=paper.updated_at
        )
    
    # Step 3: Check if PDF content was extracted
    if not paper.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from PDF for summarization"
        )
    
    # Step 4: Check if AI service is available
    if not ai_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Set CLAUDE_API_KEY in .env"
        )
    
    # Step 5: Generate summary using Claude
    summary = ai_service.generate_summary(paper.title, paper.content)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary"
        )
    
    # Step 6: Save summary to database
    paper.summary = summary
    paper.is_summarized = True
    db.commit()
    
    return PaperSummaryResponse(
        id=paper.id,
        title=paper.title,
        summary=summary,
        generated_at=paper.updated_at
    )


# ============================================================================
# DELETE /api/papers/{paper_id} - Delete a paper
# ============================================================================
@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a paper and its PDF file.
    
    Args:
        paper_id: UUID of the paper
        db: Database session (injected)
        
    Errors:
        404: Paper not found
        
    Example:
        curl -X DELETE "http://localhost:8000/api/papers/123e4567-e89b-12d3-a456-426614174000"
    """
    
    # Find the paper
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )
    
    # Delete PDF file from disk
    pdf_service.cleanup_file(paper.file_path)
    
    # Delete database record
    db.delete(paper)
    db.commit()
    
    # Return 204 No Content (success with no response body)
