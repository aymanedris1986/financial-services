---
name: expense-format
description: Format a converted expense as a single audit-friendly line. Use when producing an expense note. Triggers on "expense note", "format expense", "expense line".
---

# Expense Format

Produce exactly one line:

`<DATE> | <MERCHANT> | <AMOUNT> <CCY> = <USD_AMOUNT> USD (rate <RATE>, src <SOURCE>)`

Rules:
- `DATE` is ISO `YYYY-MM-DD`.
- Round `USD_AMOUNT` to 2 decimals.
- Always include the FX rate and its source - this is the audit trail.
- If no rate was retrieved, write `USD [UNSOURCED]` instead of a number, and omit the rate clause.

Example:
`2026-06-18 | Blue Bottle Coffee | 12.50 EUR = 13.48 USD (rate 1.0784, src fx-mcp)`
