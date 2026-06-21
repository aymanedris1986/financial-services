# FX MCP (expense-noter hello-world)

Read-only exchange-rate MCP for the `expense-noter` agent. One tool: `convert`.

## Run locally

```bash
cd examples/fx-mcp
pip install -r requirements.txt
python server.py
```

Listens at `http://127.0.0.1:8000/mcp` by default. Override with `FX_MCP_HOST` / `FX_MCP_PORT`.

## Wire to Cowork

The `expense-noter` plugin `.mcp.json` points at `http://127.0.0.1:8000/mcp`. Start this server before opening Cowork.

For remote Cowork sessions, tunnel the port (e.g. `ngrok http 8000`) and update
`plugins/agent-plugins/expense-noter/.mcp.json` with the public `/mcp` URL.

## Wire to Managed Agent (cloud)

```bash
export FX_MCP_URL=https://your-host/mcp
scripts/deploy-managed-agent.sh expense-noter
```

## Tool contract

`convert(amount, from_currency, to="USD")` returns:

```json
{ "usd": 13.48, "rate": 1.0784, "source": "fx-mcp" }
```

Matches the `expense-format` skill audit trail: `(rate 1.0784, src fx-mcp)`.
