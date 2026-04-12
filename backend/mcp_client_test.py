import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_demo():
    print("====================================================")
    print("   AGENTIC DATA ANALYST - MCP DEMO SESSION          ")
    print("====================================================\n")

    # Construct the path to the server script
    server_path = os.path.join(os.path.dirname(__file__), "mcp_bridge.py")
    
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-u", server_path],
        env=os.environ.copy()
    )

    print(f"[*] Connecting to MCP Bridge at: {server_path}")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("[*] Initializing MCP Session...")
                await session.initialize()
                
                # 1. List available tools
                print("\n[STEP 1] Discovery: Listing Registered Tools")
                print("----------------------------------------------------")
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    print(f"  > Tool: {tool.name}")
                    print(f"    Desc: {tool.description.split('.')[0]}.") # Show first sentence
                
                # 2. Call list_datasets tool
                print("\n[STEP 2] Asset Management: Listing Available Datasets")
                print("----------------------------------------------------")
                datasets_response = await session.call_tool("list_datasets")
                # FastMCP tool results are typically in content[0].text as JSON or string
                datasets_text = datasets_response.content[0].text
                print(f"  Files Found: {datasets_text}")

                # 3. Call web_research tool
                print("\n[STEP 3] Research: Fetching External Context")
                print("----------------------------------------------------")
                query = "Current status and main features of the Model Context Protocol (MCP) by Anthropic"
                print(f"  Querying: '{query}'")
                research_response = await session.call_tool("web_research", arguments={"query": query})
                research_text = research_response.content[0].text
                print(f"\n  Research Summary:\n{research_text[:500]}...") # Truncate for demo brevity

                # 4. Call analyze_data tool on the demo dataset
                print("\n[STEP 4] Analysis: Querying the Dataset")
                print("----------------------------------------------------")
                # Use the stem of our demo file as the dataset_id
                dataset_id = "demo_sales"
                analysis_query = "What was the total profit for Laptops in the North region? Also, what is the best selling product by quantity?"
                print(f"  Target: {dataset_id}")
                print(f"  Query: '{analysis_query}'")
                
                analysis_response = await session.call_tool("analyze_data", arguments={
                    "dataset_id": dataset_id,
                    "query": analysis_query
                })
                analysis_text = analysis_response.content[0].text
                print(f"\n  Agent Analysis Result:\n{analysis_text}")

                print("\n====================================================")
                print("   DEMO COMPLETED SUCCESSFULLY                      ")
                print("====================================================")

    except Exception as e:
        print(f"\n[!] ERROR During Demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_mcp_demo())
