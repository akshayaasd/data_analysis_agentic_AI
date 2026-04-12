"""
Visualization API routes.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

from src.tools.python_repl import PythonREPL
from src.tools.data_tools import dataset_manager

router = APIRouter(prefix="/api/visualization", tags=["visualization"])

# Store plots globally (in production, use a database)
plot_store = {}


@router.get("/{plot_id}")
async def get_plot(plot_id: str):
    """
    Get a plot by ID.
    
    Args:
        plot_id: Plot identifier
        
    Returns:
        Plotly figure JSON
    """
    if plot_id not in plot_store:
        raise HTTPException(status_code=404, detail="Plot not found")
    
    fig = plot_store[plot_id]
    return JSONResponse(content=json.loads(fig.to_json()))


@router.get("/list/{dataset_id}")
async def list_plots(dataset_id: str):
    """
    List all plots for a dataset.
    
    Args:
        dataset_id: Dataset identifier
        
    Returns:
        List of plot IDs
    """
    # Filter plots by dataset_id prefix
    plots = [
        plot_id for plot_id in plot_store.keys()
        if plot_id.startswith(dataset_id)
    ]
    
    return {"plots": plots}


def register_plot(plot_id: str, fig):
    """
    Register a plot in the global store.
    
    Args:
        plot_id: Unique plot identifier
        fig: Plotly figure object
    """
    plot_store[plot_id] = fig
