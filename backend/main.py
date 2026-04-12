"""
FastAPI main application.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path
from src.tools.data_tools import dataset_manager, DataTools
from fastapi.middleware.cors import CORSMiddleware
from config import settings

from src.api.routes import chat, data, suggestions, visualization

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading existing datasets...")
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        for file_path in upload_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                dataset_id = file_path.stem
                try:
                    df = DataTools.load_file(str(file_path))
                    dataset_manager.add_dataset(
                        dataset_id=dataset_id,
                        df=df,
                        filename=file_path.name,
                        file_path=str(file_path)
                    )
                    print(f"Loaded dataset: {dataset_id}")
                except Exception as e:
                    print(f"Failed to load {file_path.name}: {e}")
    yield

# Create FastAPI app
app = FastAPI(
    title="Agentic Data Analysis API",
    description="Multi-agent system for data analysis and visualization",
    version="1.0.0",
    lifespan=lifespan
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
        "message": "Agentic Data Analysis API is running!",
        "version": "1.0.0",
        "instructions": "Visit the frontend at http://localhost:5173 to use the application.",
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
        reload=True,
        reload_dirs=["src"]
    )
