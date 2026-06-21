#!/usr/bin/env python3
"""Read-only FX MCP for the expense-noter hello-world agent.

Exposes one tool: convert(amount, from_currency, to="USD").
Run locally, then point expense-noter/.mcp.json (Cowork) or FX_MCP_URL (cloud) at /mcp.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

# Demo rates — replace with a live feed in production.
RATES_TO_USD: dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.0784,
    "GBP": 1.2650,
    "AED": 0.2723,
    "JPY": 0.0067,
    "CHF": 1.1200,
}

HOST = os.environ.get("FX_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("FX_MCP_PORT", "8000"))

mcp = FastMCP("fx", json_response=True, host=HOST, port=PORT)


@mcp.tool()
def convert(amount: float, from_currency: str, to: str = "USD") -> dict:
    """Convert an amount from one currency to USD (read-only, side-effect free)."""
    from_currency = from_currency.upper().strip()
    to = to.upper().strip()
    if to != "USD":
        raise ValueError("This demo server only converts to USD")
    rate = RATES_TO_USD.get(from_currency)
    if rate is None:
        raise ValueError(f"Unsupported currency: {from_currency}")
    usd = round(amount * rate, 2)
    return {"usd": usd, "rate": rate, "source": "fx-mcp"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
