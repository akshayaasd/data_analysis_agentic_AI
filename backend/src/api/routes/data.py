"""
Data API routes for dataset management.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

from src.models.schemas import DatasetInfo, DataUploadResponse
from src.tools.data_tools import DataTools, dataset_manager
from config import settings
from datetime import datetime

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/upload", response_model=DataUploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file.
    
    Args:
        file: Uploaded file
        
    Returns:
        Dataset information and preview
    """
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique dataset ID
    dataset_id = DataTools.generate_dataset_id(file.filename)
    
    # Save file
    file_path = Path(settings.upload_dir) / f"{dataset_id}{file_ext}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Load dataset
    try:
        df = DataTools.load_file(str(file_path))
    except Exception as e:
        file_path.unlink()  # Delete file if loading fails
        raise HTTPException(status_code=400, detail=f"Failed to load file: {str(e)}")
    
    # Validate dataset
    validation = DataTools.validate_dataframe(df)
    if not validation['valid']:
        file_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dataset: {', '.join(validation['issues'])}"
        )
    
    # Get dataset info
    info_dict = DataTools.get_dataset_info(df, file.filename)
    
    # Add to dataset manager
    dataset_manager.add_dataset(
        dataset_id=dataset_id,
        df=df,
        filename=file.filename,
        file_path=str(file_path)
    )
    
    # Create response
    dataset_info = DatasetInfo(
        dataset_id=dataset_id,
        filename=file.filename,
        rows=info_dict['rows'],
        columns=info_dict['columns'],
        column_names=info_dict['column_names'],
        column_types=info_dict['column_types'],
        upload_time=datetime.now(),
        file_size=file_path.stat().st_size
    )
    
    preview = DataTools.get_preview(df, n_rows=10)
    
    return DataUploadResponse(
        dataset_id=dataset_id,
        info=dataset_info,
        preview=preview
    )


@router.get("/info/{dataset_id}", response_model=DatasetInfo)
async def get_dataset_info(dataset_id: str):
    """Get metadata for a dataset."""
    metadata = dataset_manager.get_metadata(dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    info = metadata['info']
    return DatasetInfo(
        dataset_id=dataset_id,
        filename=info['filename'],
        rows=info['rows'],
        columns=info['columns'],
        column_names=info['column_names'],
        column_types=info['column_types'],
        upload_time=metadata['upload_time'],
        file_size=Path(metadata['file_path']).stat().st_size
    )


@router.get("/preview/{dataset_id}")
async def get_dataset_preview(dataset_id: str, n_rows: int = 10):
    """Get a preview of the dataset."""
    df = dataset_manager.get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {"preview": DataTools.get_preview(df, n_rows)}


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset."""
    metadata = dataset_manager.get_metadata(dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete file
    file_path = Path(metadata['file_path'])
    if file_path.exists():
        file_path.unlink()
    
    # Remove from manager
    dataset_manager.remove_dataset(dataset_id)
    
    return {"message": "Dataset deleted"}


@router.get("/list")
async def list_datasets():
    """List all uploaded datasets."""
    dataset_ids = dataset_manager.list_datasets()
    datasets = []
    
    for dataset_id in dataset_ids:
        metadata = dataset_manager.get_metadata(dataset_id)
        if metadata:
            datasets.append({
                'dataset_id': dataset_id,
                'filename': metadata['info']['filename'],
                'upload_time': metadata['upload_time'].isoformat()
            })
    
    return {"datasets": datasets}
