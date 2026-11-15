# lumen_billing (dbt project)

The dbt project for the AI Billing & Revenue Pipeline. It reads the raw tables loaded by the Python generator and builds three layers in DuckDB.

| Layer | Materialized as | Models |
|---|---|---|
| **staging** | views | `stg_customers`, `stg_subscriptions`, `stg_usage_events`, `stg_invoices`, `stg_payments` |
| **marts** | tables | `fct_invoices`, `fct_monthly_revenue` |
| **reports** | tables | `rpt_reconciliation_breaks`, `rpt_reconciliation_vs_answer_key` |

**Also included**
- `macros/cents_to_dollars.sql`: converts integer cents to exact `DECIMAL(18,2)`.
- `tests/assert_reconciliation_finds_all_planted_errors.sql`: fails the build if the reconciliation misses a planted error or finds an extra one.
- 25 tests in total. The test on unapplied cash is set to warn.
- The `report_date` variable in `dbt_project.yml` sets the as-of date for aging.

**Run** (after `python -m generator.main` from the project root):

```bash
cd transform/lumen_billing
dbt build                             # build all models and run all tests
dbt docs generate && dbt docs serve   # view the lineage graph
```

See the [main README](../../README.md) for the full project.
