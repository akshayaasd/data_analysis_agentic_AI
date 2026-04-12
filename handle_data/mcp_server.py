import asyncio
from mcp.server.fastmcp import FastMCP
from handle_unstructured_data import UnstructuredDataHandler

# Initialize the FastMCP server
mcp = FastMCP("Data Analyst MCP")

# Instantiate the handler once; it loads env vars locally inside its __init__
handler = UnstructuredDataHandler()

@mcp.tool()
async def scrape_and_process(query: str) -> str:
    """
    Search the web and extract structured insights using Gemini based on the user query.
    
    Args:
        query: The search query to scrape and process (e.g., "latest AI news Feb 2025").
    """
    result = await handler.scrape_and_process(query)
    return result

if __name__ == "__main__":
    # Run the server via standard input/output (stdio)
    mcp.run()
