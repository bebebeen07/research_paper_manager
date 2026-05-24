"""
Main FastAPI Application

Entry point for the Research Paper Manager API.
Sets up routes, middleware, and startup/shutdown events.

Key Concepts:
- FastAPI: Modern web framework (async, fast, great docs)
- Middleware: Functions that run on every request
- Events: Startup/shutdown hooks for initialization/cleanup
- Routers: Organize endpoints by feature
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import configuration and database
from app.config import settings
from app.database import init_db
# Import routers (will create these next)
# from app.api import papers

# Create FastAPI instance
# title: Shows up in API documentation
# description: Explains what the API does
# version: For tracking releases
app = FastAPI(
    title="Research Paper Manager",
    description="AI-powered research paper management system with PDF upload and AI summaries",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows frontend running on different origin to call this API
# Example: Frontend on localhost:3000, API on localhost:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Ensure directories exist
Path("data").mkdir(exist_ok=True, parents=True)
Path("uploads").mkdir(exist_ok=True, parents=True)

# Mount static files
# This serves uploaded PDFs directly: /uploads/filename.pdf
try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")


# Health check endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    
    Try it: curl http://localhost:8000/
    
    Returns:
        Status information about the API
    """
    return {
        "message": "Research Paper Manager API",
        "version": "1.0.0",
        "status": "running",
        "docs": {
            "swagger": "http://localhost:8000/docs",
            "redoc": "http://localhost:8000/redoc"
        }
    }


# Startup event - runs when app starts
@app.on_event("startup")
async def startup_event():
    """
    Initialize database and create tables on startup.
    
    Runs once when the app starts.
    Safe to call multiple times - only creates missing tables.
    """
    print("🚀 Starting up Research Paper Manager...")
    init_db()
    print("✅ Database initialized")


# Shutdown event - runs when app stops
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown.
    Runs when the server stops.
    """
    print("🛑 Shutting down Research Paper Manager...")


# Health endpoint
@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint.
    Useful for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


# Include API routers
# These will be available at /api/papers
# We'll create the router next
# app.include_router(papers.router, prefix="/api/papers", tags=["papers"])


# Custom exception handlers could go here
# Example:
# @app.exception_handler(ValueError)
# async def value_error_handler(request, exc):
#     return JSONResponse(status_code=400, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m uvicorn app.main:app --reload
    # Or: python run.py
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
