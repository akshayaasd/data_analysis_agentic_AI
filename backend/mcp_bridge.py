import os
import sys
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
from pathlib import Path

# Add the current directory and src directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "src"))

try:
    from src.services.llm_service import get_llm_service
    from src.core.orchestrator import AgentOrchestrator
    from src.tools.python_repl import PythonREPL
    from src.tools.data_tools import dataset_manager, DataTools
    from src.tools.unstructured_tool import UnstructuredDataTool
    from config import settings
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    # Fallback for different execution contexts
    from services.llm_service import get_llm_service
    from core.orchestrator import AgentOrchestrator
    from tools.python_repl import PythonREPL
    from tools.data_tools import dataset_manager, DataTools
    from tools.unstructured_tool import UnstructuredDataTool
    from config import settings

# Initialize FastMCP
mcp = FastMCP("Agentic Data Analyst")

# Dictionary to store orchestrators per dataset
active_orchestrators: Dict[str, AgentOrchestrator] = {}

def get_orchestrator(dataset_id: str) -> AgentOrchestrator:
    if dataset_id not in active_orchestrators:
        df = dataset_manager.get_dataset(dataset_id)
        if df is None:
            # Try to load if not in memory but file exists
            upload_dir = Path(settings.upload_dir)
            file_path = None
            # Check for potential extensions
            for ext in ['.csv', '.xlsx', '.xls']:
                # The ID might be the filename without extension
                potential_path = upload_dir / f"{dataset_id}{ext}"
                if potential_path.exists():
                    file_path = str(potential_path)
                    break
            
            if not file_path:
                # Try directory search
                if upload_dir.exists():
                    for p in upload_dir.glob("*"):
                        if p.stem == dataset_id:
                            file_path = str(p)
                            break

            if not file_path:
                raise ValueError(f"Dataset {dataset_id} not found in {upload_dir}")
            
            df = DataTools.load_file(file_path)
            dataset_manager.add_dataset(dataset_id, df, Path(file_path).name, file_path)
        
        llm = get_llm_service()
        repl = PythonREPL(df)
        active_orchestrators[dataset_id] = AgentOrchestrator(llm, repl)
        
    return active_orchestrators[dataset_id]

@mcp.tool()
async def list_datasets() -> List[Dict[str, Any]]:
    """List all available datasets in the project."""
    # Pre-load datasets from upload dir if manager is empty
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        for file_path in upload_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                dataset_id = file_path.stem
                if dataset_id not in dataset_manager.list_datasets():
                    try:
                        df = DataTools.load_file(str(file_path))
                        dataset_manager.add_dataset(dataset_id, df, file_path.name, str(file_path))
                    except Exception as e:
                        print(f"Failed to load {file_path.name}: {e}", file=sys.stderr)

    ids = dataset_manager.list_datasets()
    results = []
    for d_id in ids:
        meta = dataset_manager.get_metadata(d_id)
        results.append({
            "id": d_id,
            "filename": meta['filename'],
            "columns": meta['info']['column_names'],
            "rows": meta['info']['rows']
        })
    return results

@mcp.tool()
async def analyze_data(dataset_id: str, query: str) -> str:
    """
    Query a specific dataset using an AI Data Agent.
    
    Args:
        dataset_id: The ID of the dataset to analyze (get this from list_datasets).
        query: Natural language question about the data.
    """
    try:
        orchestrator = get_orchestrator(dataset_id)
        result = await orchestrator.execute(query, dataset_id=dataset_id)
        return result['final_answer']
    except Exception as e:
        return f"Error analyzing dataset: {str(e)}"

@mcp.tool()
async def web_research(query: str) -> str:
    """
    Search the web for external information or context.
    
    Args:
        query: The search query or topic to research.
    """
    tool = UnstructuredDataTool()
    return await tool.search_and_summarize(query)

if __name__ == "__main__":
    print("Agentic Data Analyst MCP server starting...", file=sys.stderr)
    mcp.run()
