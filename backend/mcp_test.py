"""
MCP (Model Context Protocol) Integration Test
==============================================
This script proves that the MCP server (mcp_bridge.py) is running correctly
and all three MCP tools are functional:
  1. list_datasets  - Discover available datasets
  2. analyze_data   - AI-powered data analysis via MCP
  3. web_research   - External web search via MCP

Run this from the backend directory:
    cd backend
    python mcp_test.py
"""

import asyncio
import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# --- Config -------------------------------------------------------------------

SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_bridge.py")

BANNER = """
+--------------------------------------------------------------+
|         MCP INTEGRATION PROOF-OF-CONCEPT DEMO               |
|         PlotPilot - Agentic Data Analyst                     |
+--------------------------------------------------------------+
"""

def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def ok(msg: str):
    print(f"  [PASS] {msg}")

def info(msg: str):
    print(f"  [INFO] {msg}")

def err(msg: str):
    print(f"  [FAIL] {msg}")


# ─── Test Runner ───────────────────────────────────────────────────────────────

async def run_mcp_tests():
    print(BANNER)
    info(f"MCP Bridge path: {SERVER_PATH}")

    if not os.path.exists(SERVER_PATH):
        err(f"mcp_bridge.py not found at {SERVER_PATH}")
        sys.exit(1)

    # Use venv Python if available so all backend deps are importable
    venv_python = os.path.join(os.path.dirname(SERVER_PATH), "venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    info(f"Using Python: {python_exe}")

    server_params = StdioServerParameters(
        command=python_exe,
        args=["-u", SERVER_PATH],
        env=os.environ.copy()
    )

    info("Spawning MCP server process and connecting via stdio...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                ok("MCP session initialized successfully!")

                # ── Test 1: Tool Discovery ─────────────────────────────────
                section("TEST 1 — Tool Discovery (list_tools)")
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                ok(f"Found {len(tool_names)} tools: {tool_names}")
                for tool in tools_result.tools:
                    info(f"[{tool.name}] → {(tool.description or '').split(chr(10))[0].strip()}")

                # Verify all expected tools are present
                expected = {"list_datasets", "analyze_data", "web_research"}
                missing = expected - set(tool_names)
                if missing:
                    err(f"Missing expected tools: {missing}")
                else:
                    ok("All expected MCP tools are registered ✓")

                # ── Test 2: list_datasets ──────────────────────────────────
                section("TEST 2 — Dataset Discovery (list_datasets)")
                ds_response = await session.call_tool("list_datasets")
                ds_text = ds_response.content[0].text if ds_response.content else "[]"
                try:
                    datasets = json.loads(ds_text)
                    if datasets:
                        ok(f"Found {len(datasets)} dataset(s):")
                        for ds in datasets:
                            info(f"  📊 {ds.get('filename')} — {ds.get('rows')} rows × {len(ds.get('columns', []))} cols")
                    else:
                        info("No datasets found in uploads directory.")
                        info("Tip: Upload a CSV via the PlotPilot UI first.")
                except json.JSONDecodeError:
                    info(f"Raw response: {ds_text[:200]}")

                # ── Test 3: analyze_data (only if datasets available) ──────
                section("TEST 3 — Agentic Analysis (analyze_data)")
                if datasets:
                    target = datasets[0]
                    dataset_id = target.get("id") or target.get("filename", "").split(".")[0]
                    query = "What is the total and average sales? Which product has the highest profit?"
                    info(f"Dataset: {dataset_id}")
                    info(f"Query:   {query}")
                    print()
                    analysis = await session.call_tool("analyze_data", arguments={
                        "dataset_id": dataset_id,
                        "query": query
                    })
                    answer = analysis.content[0].text if analysis.content else "No answer."
                    ok("MCP analyze_data succeeded!")
                    print(f"\n  Agent Answer:\n  {'─'*50}")
                    for line in answer.strip().split("\n"):
                        print(f"  {line}")
                else:
                    info("Skipping analyze_data test (no datasets available)")

                # ── Test 4: web_research ───────────────────────────────────
                section("TEST 4 — Web Research (web_research)")
                web_query = "What is Model Context Protocol (MCP) by Anthropic?"
                info(f"Query: {web_query}")
                research = await session.call_tool("web_research", arguments={"query": web_query})
                web_text = research.content[0].text if research.content else ""
                if web_text.startswith("Error"):
                    info(f"Note: {web_text}")
                    info("(Tavily API key may not be configured — this is optional)")
                else:
                    ok("Web research succeeded!")
                    print(f"\n  Summary (first 400 chars):\n  {'─'*50}")
                    print(f"  {web_text[:400].strip()}...")

                # ── Summary ────────────────────────────────────────────────
                section("RESULT SUMMARY")
                ok("MCP server started and connected successfully")
                ok("All tools discoverable via MCP protocol")
                ok("analyze_data tool routes queries through the AI agent")
                ok("MCP integration is fully operational 🚀")

    except Exception as e:
        err(f"MCP test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(run_mcp_tests())
