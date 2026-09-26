import shutil
from contextlib import asynccontextmanager

from langchain.mcp import MCPAdapter

from config import AWS_MCP_URL, AWS_PROFILE, AWS_REGION


# Explicitly select the tools this assistant needs.
ALLOWED_TOOLS = {
    "run_script",
    "get_tasks",
    "list_regions",
    "search_documentation",
    "read_documentation",
    "get_regional_availability",
}


def base_tool_name(name):
    # Example: aws___run_script -> run_script
    return name.rsplit("___", 1)[-1]


@asynccontextmanager
async def load_tools():
    uvx = shutil.which("uvx")

    if uvx is None:
        raise RuntimeError(
            "uvx was not found. Ensure uv is installed, "
            "then restart your terminal."
        )

    connection = {
        "mcpServers": {
            "aws": {
                "command": uvx,
                "args": [
                    "mcp-proxy-for-aws-cli@latest",
                    AWS_MCP_URL,
                    "--profile",
                    AWS_PROFILE,
                    "--metadata",
                    f"AWS_REGION={AWS_REGION}",
                ],
            }
        }
    }

    async with MCPAdapter(connection) as adapter:
        discovered = await adapter.list_tools()

        selected = [
            tool
            for tool in discovered
            if base_tool_name(tool.name) in ALLOWED_TOOLS
        ]

        if not any(
            base_tool_name(tool.name) == "run_script"
            for tool in selected
        ):
            names = ", ".join(
                sorted(tool.name for tool in discovered)
            )

            raise RuntimeError(
                "AWS MCP did not expose run_script. "
                f"Discovered tools: {names or '(none)'}"
            )

        yield selected