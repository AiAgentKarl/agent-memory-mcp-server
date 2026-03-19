"""Agent Memory MCP Server — Persistenter Speicher für AI-Agents."""

from mcp.server.fastmcp import FastMCP

from src.tools.memory import register_memory_tools

mcp = FastMCP(
    "Agent Memory Server",
    instructions=(
        "Provides persistent memory for AI agents across sessions. "
        "Store facts, preferences, context and knowledge that survives "
        "session boundaries. Supports namespaces, tags and full-text search."
    ),
)

register_memory_tools(mcp)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
