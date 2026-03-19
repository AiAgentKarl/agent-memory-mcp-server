"""Datenbank — SQLite-basierter persistenter Speicher für Agent-Memories."""

import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path


_DB_PATH = os.getenv("MEMORY_DB_PATH", str(Path(__file__).resolve().parent.parent / "memory.db"))


def _connect() -> sqlite3.Connection:
    """DB-Verbindung herstellen und Schema anlegen."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Bessere Performance
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace TEXT NOT NULL DEFAULT 'default',
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0,
            UNIQUE(namespace, key)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_namespace ON memories(namespace)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)
    """)
    conn.commit()
    return conn


def store(namespace: str, key: str, value: str, tags: list[str] = None) -> dict:
    """Memory speichern oder aktualisieren."""
    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    tags_str = json.dumps(tags) if tags else None

    conn.execute(
        """INSERT INTO memories (namespace, key, value, tags, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(namespace, key) DO UPDATE SET
               value=excluded.value,
               tags=excluded.tags,
               updated_at=excluded.updated_at""",
        (namespace, key, value, tags_str, now, now),
    )
    conn.commit()
    conn.close()
    return {"namespace": namespace, "key": key, "stored": True, "updated_at": now}


def retrieve(namespace: str, key: str) -> dict | None:
    """Memory abrufen und Zugriffszähler erhöhen."""
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM memories WHERE namespace=? AND key=?",
        (namespace, key),
    ).fetchone()

    if row:
        conn.execute(
            "UPDATE memories SET access_count = access_count + 1 WHERE id=?",
            (row["id"],),
        )
        conn.commit()
        result = dict(row)
        result["tags"] = json.loads(result["tags"]) if result["tags"] else []
        conn.close()
        return result

    conn.close()
    return None


def search(query: str, namespace: str = None, tags: list[str] = None, limit: int = 20) -> list:
    """Memories durchsuchen (Key und Value)."""
    conn = _connect()
    sql = "SELECT * FROM memories WHERE (key LIKE ? OR value LIKE ?)"
    params = [f"%{query}%", f"%{query}%"]

    if namespace:
        sql += " AND namespace=?"
        params.append(namespace)

    if tags:
        for tag in tags:
            sql += " AND tags LIKE ?"
            params.append(f"%{tag}%")

    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        results.append(d)
    return results


def list_memories(namespace: str = None, limit: int = 50) -> list:
    """Alle Memories auflisten."""
    conn = _connect()
    if namespace:
        rows = conn.execute(
            "SELECT * FROM memories WHERE namespace=? ORDER BY updated_at DESC LIMIT ?",
            (namespace, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        results.append(d)
    return results


def delete(namespace: str, key: str) -> dict:
    """Memory löschen."""
    conn = _connect()
    cursor = conn.execute(
        "DELETE FROM memories WHERE namespace=? AND key=?",
        (namespace, key),
    )
    conn.commit()
    conn.close()
    return {"deleted": cursor.rowcount > 0, "namespace": namespace, "key": key}


def list_namespaces() -> list:
    """Alle Namespaces auflisten mit Anzahl Memories."""
    conn = _connect()
    rows = conn.execute(
        "SELECT namespace, COUNT(*) as count FROM memories GROUP BY namespace ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """Statistiken über den Speicher."""
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) as c FROM memories").fetchone()["c"]
    namespaces = conn.execute("SELECT COUNT(DISTINCT namespace) as c FROM memories").fetchone()["c"]
    most_accessed = conn.execute(
        "SELECT namespace, key, access_count FROM memories ORDER BY access_count DESC LIMIT 5"
    ).fetchall()
    recent = conn.execute(
        "SELECT namespace, key, updated_at FROM memories ORDER BY updated_at DESC LIMIT 5"
    ).fetchall()
    conn.close()

    return {
        "total_memories": total,
        "total_namespaces": namespaces,
        "most_accessed": [dict(r) for r in most_accessed],
        "recently_updated": [dict(r) for r in recent],
    }
