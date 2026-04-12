"""
MCP Bridge - Agentic Data Analyst
==================================
FastMCP server exposing AI data analysis tools via the Model Context Protocol.

Tools:
  - list_datasets  : Discover uploaded datasets
  - analyze_data   : AI-powered analysis via ReAct agent
  - web_research   : External web search and summarization

Run directly for MCP mode:
    python mcp_bridge.py

Or import via stdio_client in mcp_test.py / mcp_client_test.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Add backend directory and src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "src"))

try:
    from src.services.llm_service import get_llm_service
    from src.core.orchestrator import AgentOrchestrator
    from src.tools.python_repl import PythonREPL
    from src.tools.data_tools import dataset_manager, DataTools
    from config import settings
except ImportError as e:
    print(f"Import error (src.*): {e}", file=sys.stderr)
    from services.llm_service import get_llm_service
    from core.orchestrator import AgentOrchestrator
    from tools.python_repl import PythonREPL
    from tools.data_tools import dataset_manager, DataTools
    from config import settings

# Optional web research tool
try:
    from src.tools.unstructured_tool import UnstructuredDataTool
    _has_web_research = True
except ImportError:
    try:
        from tools.unstructured_tool import UnstructuredDataTool
        _has_web_research = True
    except ImportError:
        _has_web_research = False
        print("web_research tool not available (unstructured_tool not found)", file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("Agentic Data Analyst")

# Cache of orchestrators keyed by dataset_id
_orchestrators: dict = {}


def _get_or_load_dataset(dataset_id: str):
    """Load dataset into manager if not already present."""
    df = dataset_manager.get_dataset(dataset_id)
    if df is not None:
        return df

    upload_dir = Path(settings.upload_dir)
    for ext in [".csv", ".xlsx", ".xls"]:
        candidate = upload_dir / f"{dataset_id}{ext}"
        if candidate.exists():
            df = DataTools.load_file(str(candidate))
            dataset_manager.add_dataset(dataset_id, df, candidate.name, str(candidate))
            return df
    return None


def _get_orchestrator(dataset_id: str) -> AgentOrchestrator:
    if dataset_id not in _orchestrators:
        df = _get_or_load_dataset(dataset_id)
        if df is None:
            raise ValueError(f"Dataset '{dataset_id}' not found.")
        llm = get_llm_service()
        repl = PythonREPL(df)
        _orchestrators[dataset_id] = AgentOrchestrator(llm, repl)
    return _orchestrators[dataset_id]


# ── Tool: list_datasets ────────────────────────────────────────────────────────

@mcp.tool()
async def list_datasets():
    """
    List all available datasets in the uploads directory.
    Returns a JSON string with dataset metadata.
    """
    upload_dir = Path(settings.upload_dir)
    if upload_dir.exists():
        for fp in upload_dir.glob("*"):
            if fp.is_file() and fp.suffix.lower() in [".csv", ".xlsx", ".xls"]:
                did = fp.stem
                if did not in dataset_manager.list_datasets():
                    try:
                        df = DataTools.load_file(str(fp))
                        dataset_manager.add_dataset(did, df, fp.name, str(fp))
                    except Exception as ex:
                        print(f"Could not load {fp.name}: {ex}", file=sys.stderr)

    results = []
    for did in dataset_manager.list_datasets():
        meta = dataset_manager.get_metadata(did)
        results.append({
            "id": did,
            "filename": meta["filename"],
            "rows": meta["info"]["rows"],
            "columns": meta["info"]["column_names"],
        })
    return json.dumps(results, indent=2)


# ── Tool: analyze_data ─────────────────────────────────────────────────────────

@mcp.tool()
async def analyze_data(dataset_id: str, query: str):
    """
    Run an AI Data Agent on a specific dataset.

    Args:
        dataset_id: Dataset ID from list_datasets (usually the filename without extension).
        query: Natural language question about the dataset.

    Returns:
        Agent's final answer as a string.
    """
    try:
        orchestrator = _get_orchestrator(dataset_id)
        result = await orchestrator.execute(query, dataset_id=dataset_id)
        return result.get("final_answer", "No answer produced.")
    except Exception as e:
        return f"Error: {str(e)}"


# ── Tool: web_research ─────────────────────────────────────────────────────────

@mcp.tool()
async def web_research(query: str):
    """
    Search the web and summarize results for a given query.

    Args:
        query: The topic or question to research online.

    Returns:
        Summarized web research result.
    """
    if not _has_web_research:
        return "web_research tool is not available (unstructured_tool.py not installed)."
    try:
        tool = UnstructuredDataTool()
        return await tool.search_and_summarize(query)
    except Exception as e:
        return f"Error during web research: {str(e)}"


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Agentic Data Analyst MCP server starting...", file=sys.stderr)
    mcp.run()
