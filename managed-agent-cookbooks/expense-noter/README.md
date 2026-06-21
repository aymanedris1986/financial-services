# Expense Noter - managed-agent template (hello-world)

## Overview

Receipt -> USD -> one-line note. The minimal agent that exercises every technical concept in this repo
once. Same source as the `expense-noter` Cowork plugin - this directory is the Managed Agent cookbook
for `POST /v1/agents`.

## Deploy

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export FX_MCP_URL=...            # read-only FX-rate MCP
../../scripts/deploy-managed-agent.sh expense-noter
```

## Steering events

See [`steering-examples.json`](./steering-examples.json). Trigger with a receipt ID.

## Security & handoffs

Receipts are untrusted. Three-tier split:

| Tier | Touches untrusted docs? | Tools | Connectors |
|---|---|---|---|
| **`reader`** | **Yes** | `Read`, `Grep` only | None |
| Orchestrator | No | `Read`, `Grep`, `Glob`, `Agent` | FX (read-only) |
| **`writer`** (Write-holder) | No | `Read`, `Write` | None |

`reader` returns length-capped, schema-validated JSON. `writer` produces `./out/expense-<id>.md`.

**Handoff:** if the USD total exceeds 1000, the orchestrator emits a `handoff_request` for `approver`;
`scripts/orchestrate.py` routes it as a new steering event.

**Not guaranteed:** the note is a draft; nothing is posted to a finance system.
