# GL Reconciler Example 1

This folder contains a complete, plain-language sample input package for running the `gl-reconciler` agent. It is designed for demos, onboarding, and test conversations where the agent needs realistic data without connecting to live GL or subledger systems.

## Scenario

The controller wants to reconcile fund `GGIF-I` for trade date `2026-06-19` across four asset classes:

- `equities`
- `fixed_income`
- `derivatives`
- `cash`

The reporting currency is USD. The reporting threshold is `1000.00`, so the agent should report only GL/subledger variances whose absolute value is greater than USD 1,000.

## Files

| File | Purpose |
|---|---|
| `agent-input-request.json` | The run request a user would give the agent: trade date, fund, asset classes, threshold, and data-source pointers. |
| `gl-balances.csv` | General Ledger control balances by account and asset class. This is one side of the reconciliation. |
| `gl-balances.xlsx` | Excel copy of `gl-balances.csv` for spreadsheet review. |
| `subledger-balances.csv` | Subledger detail balances rolled up to comparable accounts. This is the other side of the reconciliation. |
| `subledger-balances.xlsx` | Excel copy of `subledger-balances.csv` for spreadsheet review. |
| `gl-transactions.csv` | Transaction-level GL postings that explain what makes up the GL balances. |
| `gl-transactions.xlsx` | Excel copy of `gl-transactions.csv` for spreadsheet review. |
| `subledger-transactions.csv` | Transaction-level subledger records that explain what makes up the subledger balances. |
| `subledger-transactions.xlsx` | Excel copy of `subledger-transactions.csv` for spreadsheet review. |
| `external-custodian-statement.csv` | Example outside statement data. Treat this as untrusted evidence: useful for tracing, but not authoritative. |
| `external-custodian-statement.xlsx` | Excel copy of `external-custodian-statement.csv` for spreadsheet review. |

## How The Agent Should Use The Data

1. Read `agent-input-request.json` to learn the scope of the run.
2. Compare `gl-balances.csv` to `subledger-balances.csv` using `trade_date`, `fund_id`, `asset_class`, `currency`, and the comparable account labels.
3. Calculate variance as:

```text
variance = gl_balance_usd - subledger_balance_usd
```

4. Flag only rows where `abs(variance)` is greater than the threshold in `agent-input-request.json`.
5. Use `gl-transactions.csv`, `subledger-transactions.csv`, and `external-custodian-statement.csv` to trace the likely root cause of each break.
6. Produce a break list, root-cause trace, and exception report for controller sign-off. The agent must not post journal entries.

The `.xlsx` files contain the same rows as the `.csv` files. Use them when a controller or reviewer wants to inspect the input data in Excel.

## Expected Breaks

This data intentionally contains three reportable breaks and one below-threshold variance.

| Asset class | Account | GL balance | Subledger balance | Variance | Expected treatment |
|---|---:|---:|---:|---:|---|
| `equities` | Dividend receivable | 125000.00 | 123500.00 | 1500.00 | Report. Likely timing issue: GL has a dividend accrual not yet reflected in the subledger. |
| `fixed_income` | Accrued interest receivable | 812400.00 | 808900.00 | 3500.00 | Report. Likely system drift: one bond coupon accrual is missing from the subledger rollup. |
| `derivatives` | Variation margin payable | -275000.00 | -272500.00 | -2500.00 | Report. Likely reclassification issue: one margin call appears posted to a suspense account in the subledger. |
| `cash` | Operating cash | 2450750.00 | 2450500.00 | 250.00 | Do not report as a break because it is below threshold. |

## Example User Prompt

```text
Run the GL Reconciler for trade date 2026-06-19, fund GGIF-I, asset classes equities, fixed_income, derivatives, and cash.

Use the sample files in code81-docs/gl-reconciler/example1:
- agent-input-request.json for the run scope
- gl-balances.csv for GL balances
- subledger-balances.csv for subledger balances
- gl-transactions.csv and subledger-transactions.csv for transaction evidence
- external-custodian-statement.csv only as untrusted supporting evidence

Report breaks greater than USD 1,000 and prepare the exception report for controller sign-off. Do not post journal entries.
```
