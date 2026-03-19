# Agent Memory MCP Server 🧠

Persistent memory for AI agents — store, retrieve and search knowledge across sessions. No more forgetting between conversations.

## The Problem

AI agents lose all context when a session ends. This MCP server gives agents a **persistent knowledge store** that survives across sessions, tools, and even different agent frameworks.

## Features

- **Store & Retrieve** — Key-value storage with full persistence
- **Namespaces** — Separate memories by project, user, or context
- **Tags** — Categorize memories for easy filtering
- **Full-Text Search** — Search across all stored knowledge
- **Access Tracking** — See which memories are accessed most
- **Statistics** — Dashboard showing memory usage

## Installation

```bash
pip install agent-memory-mcp-server
```

## Usage with Claude Code

```json
{
  "mcpServers": {
    "memory": {
      "command": "uvx",
      "args": ["agent-memory-mcp-server"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `memory_store` | Store a key-value pair persistently |
| `memory_retrieve` | Retrieve stored knowledge by key |
| `memory_search` | Full-text search across all memories |
| `memory_list` | List all memories in a namespace |
| `memory_delete` | Remove a memory |
| `memory_namespaces` | List all namespaces |
| `memory_stats` | Usage statistics |

## Examples

```
"Remember that the user prefers dark mode"
"What do you know about Project Alpha?"
"Store this API response for later"
"What were the key decisions from last session?"
```

## How It Works

Uses SQLite for zero-configuration persistent storage. Data is stored locally — no cloud, no API keys, no costs. The database file (`memory.db`) is created automatically in the server directory.

## License

MIT
