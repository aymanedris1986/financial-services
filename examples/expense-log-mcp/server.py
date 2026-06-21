#!/usr/bin/env python3
"""Expense log MCP — posts formatted expense lines to ntfy.sh (free, no API key).

Exposes one tool: log_line(text). View saved messages at https://ntfy.sh/<topic>.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP

HOST = os.environ.get("EXPENSE_LOG_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("EXPENSE_LOG_MCP_PORT", "8001"))
NTFY_TOPIC = os.environ.get("EXPENSE_LOG_NTFY_TOPIC", "expense-noter-demo")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

mcp = FastMCP("expense-log", json_response=True, host=HOST, port=PORT)


@mcp.tool()
def log_line(text: str) -> dict:
    """Save an expense line to a free online log (ntfy.sh). Returns the public topic URL."""
    text = text.strip()
    if not text:
        raise ValueError("text must not be empty")
    if len(text) > 4000:
        raise ValueError("text exceeds 4000 characters")

    req = urllib.request.Request(
        NTFY_URL,
        data=text.encode("utf-8"),
        method="POST",
        headers={
            "User-Agent": "expense-noter/1.0",
            "Title": "Expense note",
            "Tags": "receipt,money_clip",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                raise RuntimeError(f"ntfy returned HTTP {resp.status}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"failed to post to ntfy: {e}") from e

    return {"url": NTFY_URL, "source": "ntfy", "topic": NTFY_TOPIC}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
