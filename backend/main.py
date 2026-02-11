"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

from src.api.routes import chat, data, suggestions, visualization

# Create FastAPI app
app = FastAPI(
    title="Agentic Data Analysis API",
    description="Multi-agent system for data analysis and visualization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(data.router)
app.include_router(suggestions.router)
app.include_router(visualization.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agentic Data Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
