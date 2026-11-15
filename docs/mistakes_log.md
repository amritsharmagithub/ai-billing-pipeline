# Mistakes Log

The main technical mistakes I made and how I fixed them.

### 1. Gaps in my reconciliation logic
My first invoice check was one-sided, so it could not find a month with usage but no invoice, and some old invoices were counted as both aged and short-paid. I made the check two-sided and added exclusion logic so each break is reported once.

### 2. A library update broke my report script
DuckDB 2.0 removed a method my script used to read results. I switched to the supported `execute()` method and pinned package versions in `requirements.txt`, so the project runs the same way for anyone who clones it.
