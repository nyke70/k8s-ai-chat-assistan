"""Where the tools come from."""
from langchain_mcp_adapters.client import MultiServerMCPClient

from config import MCP_URL


async def load_tools():
    """Connect to the MCP server and return the tools it offers."""
    client = MultiServerMCPClient({"k8s": {"transport": "streamable_http", "url": MCP_URL}})
    return await client.get_tools()