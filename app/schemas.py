"""
Pydantic Request/Response Schemas

These define the structure of data sent to/from the API.

Key Concepts:
- Pydantic Models: Validate request data automatically
- Type hints: Enforce correct data types
- Optional: Fields that may or may not be present
- Example: Shows sample data in API documentation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaperBase(BaseModel):
    """
    Base paper data - shared by request and response schemas.
    
    This pattern (Base -> Create -> Response) is DRY (Don't Repeat Yourself)
    """
    title: str = Field(..., min_length=1, max_length=255, description="Paper title")


class PaperCreate(PaperBase):
    """
    Schema for uploading a new paper.
    Used to validate the request when uploading.
    """
    pass


class PaperResponse(PaperBase):
    """
    Schema for API responses when returning paper data.
    
    Usage:
        @router.get("/papers/{paper_id}", response_model=PaperResponse)
        async def get_paper(paper_id: str):
            ...
    
    Pydantic will automatically:
    1. Validate the response has all required fields
    2. Convert datetime to ISO format strings
    3. Remove any extra fields
    4. Add this to API documentation
    """
    id: str = Field(..., description="Unique paper identifier")
    filename: str = Field(..., description="Stored filename")
    original_filename: str = Field(..., description="Original filename")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    is_summarized: bool = Field(..., description="Whether summary exists")
    created_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        # Allow conversion from ORM models
        from_attributes = True
        # Example for API docs
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Deep Learning Advances in 2024",
                "filename": "paper_123.pdf",
                "original_filename": "research_paper.pdf",
                "summary": "This paper explores recent advances in deep learning...",
                "is_summarized": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class PaperSummaryResponse(BaseModel):
    """Response when requesting a summary"""
    id: str
    title: str
    summary: str
    generated_at: datetime


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")
    code: str = Field(..., description="Error code")
