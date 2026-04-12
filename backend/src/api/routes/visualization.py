"""
Visualization API routes.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

from src.tools.python_repl import PythonREPL
from src.tools.data_tools import dataset_manager

import os
import plotly.io as pio
from pathlib import Path
from config import settings

router = APIRouter(prefix="/api/visualization", tags=["visualization"])

# Store plots globally
plot_store = {}


def save_plot_to_disk(plot_id: str, fig):
    """Save a plot to disk as JSON."""
    try:
        os.makedirs(settings.plots_dir, exist_ok=True)
        file_path = Path(settings.plots_dir) / f"{plot_id}.json"
        # Write with plain JSON engine to avoid bdata serialization issues
        pio.write_json(fig, str(file_path), engine="json")
    except Exception as e:
        print(f"Error saving plot {plot_id}: {e}")


def load_plots_from_disk():
    """Load all plots from disk into memory."""
    try:
        if not os.path.exists(settings.plots_dir):
            return
        
        for file_name in os.listdir(settings.plots_dir):
            if file_name.endswith(".json"):
                plot_id = file_name[:-5]
                file_path = Path(settings.plots_dir) / file_name
                try:
                    # Read directly as a dictionary to avoid Plotly validation errors on binary arrays
                    with open(file_path, "r", encoding="utf-8") as f:
                        fig_dict = json.load(f)
                    plot_store[plot_id] = fig_dict
                except Exception as e:
                    print(f"Error loading plot {plot_id}: {e}")
    except Exception as e:
        print(f"Error initializing plot store: {e}")


# Initial load
load_plots_from_disk()


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
        # Try loading from disk if not in store (lazy load)
        file_path = Path(settings.plots_dir) / f"{plot_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    fig_dict = json.load(f)
                plot_store[plot_id] = fig_dict
            except Exception:
                raise HTTPException(status_code=404, detail="Plot not found")
        else:
            raise HTTPException(status_code=404, detail="Plot not found")
    
    fig = plot_store[plot_id]
    
    # If the stored object is already a dict, return it directly.
    # Otherwise, convert the Plotly figure to a dictionary.
    if isinstance(fig, dict):
        return JSONResponse(content=fig)
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
    Register a plot in the global store and persist it.
    
    Args:
        plot_id: Unique plot identifier
        fig: Plotly figure object
    """
    plot_store[plot_id] = fig
    save_plot_to_disk(plot_id, fig)
