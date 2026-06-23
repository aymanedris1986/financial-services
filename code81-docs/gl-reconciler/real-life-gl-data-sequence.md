# Real-Life GL Data Sequence

This note explains which accounting data usually exists first in real life, and which files are normally derived from earlier records.

## High-Level Sequence

In a real accounting environment, the starting point is not a GL file. The starting point is the actual business activity.

```text
Business events
        ↓
Subledger transactions
        ↓
Subledger balances
        ↓
GL transactions / journal postings
        ↓
GL balances
        ↓
Reconciliation report / exception list
```

## Step-by-Step Explanation

### 1. Business Events

These are the real-world activities that happen first, such as:

- A trade is executed.
- A dividend is declared or accrued.
- A bond coupon accrues.
- A margin call is received.
- A cash movement happens.

These events are the true economic source. They are not usually represented by one reconciliation file; they come from trading systems, treasury systems, bank feeds, custodian records, or other operational systems.

### 2. Subledger Transactions

`subledger-transactions.csv` represents the detailed records created from those business events.

Examples include individual trades, positions, accruals, cash movements, dividend receivables, coupon accruals, and margin activity.

This is usually the first accounting-style dataset in the sequence because the subledger stores detailed activity before it is summarized.

### 3. Subledger Balances

`subledger-balances.csv` is normally derived from `subledger-transactions.csv`.

It is a rolled-up total by fields such as:

- Trade date
- Fund
- Asset class
- Currency
- Reconciliation account

In simple terms:

```text
subledger-transactions.csv
        ↓ rolled up into
subledger-balances.csv
```

### 4. GL Transactions

`gl-transactions.csv` represents journal postings in the General Ledger.

These postings are often created from subledger activity, but not always. In real companies, GL transactions can also come from:

- Manual journal entries
- Bank feeds
- Treasury systems
- Expense systems
- Payroll systems
- Month-end adjustments

So `gl-transactions.csv` may be partly derived from `subledger-transactions.csv`, but it can also contain GL-only postings.

### 5. GL Balances

`gl-balances.csv` is normally derived from `gl-transactions.csv`.

It is the account-level ending balance after the GL postings have been summarized for the relevant date.

In simple terms:

```text
gl-transactions.csv
        ↓ rolled up into
gl-balances.csv
```

### 6. Reconciliation Output

The reconciliation report or exception list comes after both sides are available.

The usual comparison is:

```text
gl-balances.csv
        compared with
subledger-balances.csv
```

If the balances do not match, the transaction files are used to explain why:

```text
gl-transactions.csv
subledger-transactions.csv
        ↓
root-cause investigation
```

## Important Nuance

The subledger side and GL side are related, but the GL is not always a perfect derivative of the subledger.

For investment accounting, the common flow is:

```text
subledger-transactions
        ↓ create or support journal postings
gl-transactions
        ↓ roll up
gl-balances
```

However, GL transactions can include extra postings that never came from the investment subledger. Those extra postings are one common reason reconciliations find breaks.

