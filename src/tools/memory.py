"""Memory-Tools — Persistenter Speicher für AI-Agents."""

from mcp.server.fastmcp import FastMCP

from src import db


def register_memory_tools(mcp: FastMCP):
    """Memory-bezogene MCP-Tools registrieren."""

    @mcp.tool()
    async def memory_store(
        key: str,
        value: str,
        namespace: str = "default",
        tags: list[str] = None,
    ) -> dict:
        """Wissen persistent speichern.

        Speichert einen Key-Value-Eintrag der über Sessions hinweg
        erhalten bleibt. Ideal für Fakten, Präferenzen, Kontext.

        Args:
            key: Eindeutiger Schlüssel (z.B. "user_preference_language")
            value: Der zu speichernde Inhalt (Text, JSON, etc.)
            namespace: Namespace zur Trennung (z.B. "project_x", "user_123")
            tags: Optionale Tags zum Kategorisieren (z.B. ["preference", "important"])
        """
        return db.store(namespace, key, value, tags)

    @mcp.tool()
    async def memory_retrieve(key: str, namespace: str = "default") -> dict:
        """Gespeichertes Wissen abrufen.

        Args:
            key: Schlüssel des gesuchten Eintrags
            namespace: Namespace (Standard: "default")
        """
        result = db.retrieve(namespace, key)
        if result:
            return result
        return {"found": False, "key": key, "namespace": namespace}

    @mcp.tool()
    async def memory_search(
        query: str,
        namespace: str = None,
        tags: list[str] = None,
        limit: int = 10,
    ) -> dict:
        """Memories durchsuchen.

        Sucht in Keys und Values nach dem Suchbegriff.
        Optional filterbar nach Namespace und Tags.

        Args:
            query: Suchbegriff
            namespace: Optional — nur in diesem Namespace suchen
            tags: Optional — nur Memories mit diesen Tags
            limit: Maximale Ergebnisse (Standard: 10)
        """
        results = db.search(query, namespace, tags, limit)
        return {
            "query": query,
            "results_count": len(results),
            "results": results,
        }

    @mcp.tool()
    async def memory_list(namespace: str = None, limit: int = 20) -> dict:
        """Alle Memories auflisten.

        Args:
            namespace: Optional — nur diesen Namespace zeigen
            limit: Maximale Anzahl (Standard: 20)
        """
        results = db.list_memories(namespace, limit)
        return {
            "total": len(results),
            "memories": results,
        }

    @mcp.tool()
    async def memory_delete(key: str, namespace: str = "default") -> dict:
        """Ein Memory löschen.

        Args:
            key: Schlüssel des zu löschenden Eintrags
            namespace: Namespace (Standard: "default")
        """
        return db.delete(namespace, key)

    @mcp.tool()
    async def memory_namespaces() -> dict:
        """Alle Namespaces mit Anzahl Memories auflisten.

        Zeigt eine Übersicht aller verwendeten Namespaces.
        """
        namespaces = db.list_namespaces()
        return {
            "total_namespaces": len(namespaces),
            "namespaces": namespaces,
        }

    @mcp.tool()
    async def memory_stats() -> dict:
        """Speicher-Statistiken abrufen.

        Zeigt: Gesamtzahl Memories, Namespaces, meistgenutzte
        und zuletzt aktualisierte Einträge.
        """
        return db.get_stats()
