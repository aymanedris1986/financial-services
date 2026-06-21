# Expense log MCP (expense-noter hello-world)

Posts formatted expense lines to [ntfy.sh](https://ntfy.sh) — free, no API key. Messages appear on the public topic page.

## Run locally

```bash
cd examples/expense-log-mcp
pip install -r requirements.txt
python server.py
```

Listens at `http://127.0.0.1:8001/mcp`. Override with `EXPENSE_LOG_MCP_HOST` / `EXPENSE_LOG_MCP_PORT`.

Default topic: `expense-noter-demo` → view at https://ntfy.sh/expense-noter-demo

Set your own topic (recommended for demos):

```bash
export EXPENSE_LOG_NTFY_TOPIC=my-firm-expenses
python server.py
```

## Wire to Cowork

The `expense-noter` plugin `.mcp.json` includes this server. Run it alongside `examples/fx-mcp/server.py` before opening Cowork.

## Wire to Managed Agent (cloud)

```bash
export EXPENSE_LOG_MCP_URL=https://your-host/mcp
scripts/deploy-managed-agent.sh expense-noter
```

The cloud agent must reach a **public** log MCP endpoint; ntfy.sh is called from your MCP server, not directly by Anthropic.

## Tool contract

`log_line(text)` returns:

```json
{ "url": "https://ntfy.sh/expense-noter-demo", "source": "ntfy", "topic": "expense-noter-demo" }
```
