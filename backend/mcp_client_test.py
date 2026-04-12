import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_proof():
    # Construct the path to the server script
    server_path = os.path.join(os.path.dirname(__file__), "mcp_bridge.py")
    
    # Define server parameters - using python to run the script
    # We use -u for unbuffered output to ensure we don't hang on stdio
    server_params = StdioServerParameters(
        command="python",
        args=["-u", server_path],
        env=os.environ.copy()
    )

    print(f"Connecting to MCP server at {server_path}...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("Initializing session...")
                await session.initialize()
                
                # 1. List available tools
                print("\n--- Available Tools ---")
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    print(f"Tool: {tool.name}")
                    print(f"  Description: {tool.description}")
                
                # 2. Call list_datasets tool
                print("\n--- Calling 'list_datasets' ---")
                datasets = await session.call_tool("list_datasets")
                print(f"Result: {datasets.content[0].text}")

                # 3. Call web_research tool
                print("\n--- Calling 'web_research' ---")
                research = await session.call_tool("web_research", arguments={"query": "Current status of Model Context Protocol (MCP)"})
                print(f"Result: {research.content[0].text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_mcp_proof())
