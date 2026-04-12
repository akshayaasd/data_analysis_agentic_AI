"""
Image Analysis API routes.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from src.agents.image_analysis_agent import ImageAnalysisAgent
from config import settings

router = APIRouter(prefix="/api/images", tags=["images"])

# Store uploaded images metadata
uploaded_images = {}


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for analysis.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Image upload response with metadata
    """
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique image ID
    image_id = str(uuid.uuid4())
    
    # Save file
    file_path = Path(settings.upload_dir) / f"{image_id}{file_ext}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Store metadata
    uploaded_images[image_id] = {
        'filename': file.filename,
        'file_path': str(file_path),
        'upload_time': datetime.now(),
        'file_size': file_path.stat().st_size,
        'file_ext': file_ext
    }
    
    return {
        'image_id': image_id,
        'filename': file.filename,
        'file_path': str(file_path),
        'upload_time': datetime.now().isoformat(),
        'file_size': file_path.stat().st_size
    }


@router.post("/analyze/{image_id}")
async def analyze_image(image_id: str):
    """
    Analyze an uploaded image.
    
    Args:
        image_id: Image identifier
        
    Returns:
        Image analysis with insights
    """
    if image_id not in uploaded_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    metadata = uploaded_images[image_id]
    filename = metadata['filename']
    
    try:
        # Initialize agent (no LLM needed for mock API)
        agent = ImageAnalysisAgent()
        
        # Run analysis
        result = await agent.analyze_image(filename)
        
        return {
            'image_id': image_id,
            'filename': filename,
            'analysis': result.get('final_answer'),
            'execution_time': result.get('execution_time'),
            'success': True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


@router.get("/list")
async def list_images():
    """Get all uploaded images."""
    images = []
    for image_id, metadata in uploaded_images.items():
        images.append({
            'image_id': image_id,
            'filename': metadata['filename'],
            'upload_time': metadata['upload_time'].isoformat(),
            'file_size': metadata['file_size']
        })
    
    return {'images': images}


@router.get("/{image_id}")
async def get_image_metadata(image_id: str):
    """Get image metadata."""
    if image_id not in uploaded_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    metadata = uploaded_images[image_id]
    return {
        'image_id': image_id,
        'filename': metadata['filename'],
        'upload_time': metadata['upload_time'].isoformat(),
        'file_size': metadata['file_size']
    }


@router.delete("/{image_id}")
async def delete_image(image_id: str):
    """Delete an uploaded image."""
    if image_id not in uploaded_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    metadata = uploaded_images[image_id]
    file_path = Path(metadata['file_path'])
    
    if file_path.exists():
        file_path.unlink()
    
    del uploaded_images[image_id]
    
    return {'message': 'Image deleted'}
