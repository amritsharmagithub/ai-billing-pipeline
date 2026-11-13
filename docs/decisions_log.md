# Decisions Log

This file records the main choices I made in this project: what the options were, what I picked, and why.

---

## Decision 1: Build on dbt v1 now, upgrade to dbt v2 at the end

**Date:** November 13, 2026
**Phase:** 1 — Setup

### Context
After installing dbt-duckdb, `dbt --version` showed dbt Core 1.12.7 with the DuckDB adapter 1.11.1. It also printed a notice that **dbt v2** is available and is now the default for new installations.

I looked into it before going further:
- dbt 2.0.0 was released on September 14, 2026. It is a rewrite of the dbt engine in Rust. It is faster and stricter about checking project code.
- dbt v2 ships with a built-in DuckDB adapter, so it does not need the separate dbt-duckdb package.
- dbt's upgrade guide says v1 is still fully supported, but new features will only be added to v2.
- The project language (SQL models, YAML, and how models depend on each other) carries over from v1 to v2.

### Options
| | A. Stay on v1 now, upgrade at the end | B. Switch to v2 now |
|---|---|---|
| Matches my learning video | Yes. The MotherDuck video uses dbt-duckdb (v1). | No. Setup and some commands differ from the video. |
| Already installed | Yes | No |
| Risk while learning | Low | Higher. v2 was about two months old, and I would be learning from a video that does not match my tools. |

### Decision
**Option A.** Build the project on dbt v1 (dbt-core 1.12.7 + dbt-duckdb 1.11.1). In Phase 8, upgrade the finished project to dbt v2 and document the upgrade.

### Why
- I am learning dbt from a video that uses v1. If I changed tools at the same time, it would be hard to tell whether an error came from my SQL or from the version difference.
- v1 is still fully supported, so building on it is not a dead end.
- My SQL models and tests carry over to v2, so the work is not wasted.
- Planning the upgrade as its own step lets me show how I handle a tool changing during a project.

### What I will do to keep the upgrade easy
- Use current dbt syntax only. For example, use `--select` / `-s` instead of older flags like `--models`, which v2 no longer accepts.
- Treat dbt deprecation warnings as things to fix right away, not ignore.

### Sources
- DuckDB blog, "DuckDB Now Ships inside dbt v2" (September 22, 2026): https://duckdb.org/2026/09/22/dbt-fusion
- dbt docs, "Upgrading to v2": https://docs.getdbt.com/docs/dbt-versions/dbt-upgrade/upgrading-to-v2

**Update (same day):** Decision 2 made the v2 upgrade an optional stretch goal instead of a planned Phase 8 step.

---

## Decision 2: Focus the project on analytics and finance roles, and drop Airflow

**Date:** November 13, 2026
**Phase:** Before Phase 2

### Context
Before starting Phase 2, I stepped back and asked whether the original plan (8 phases, including Airflow) fit the roles I'm targeting: **analytics, finance, and billing roles, and possibly data science**. I'm not targeting data engineering roles.

### The goal of the project, in one sentence
Show that I can take messy billing data and turn it into revenue numbers people can trust: model it, test it, reconcile it, and explain the breaks.

### Options
| | Keep all 8 phases | Focus on the core |
|---|---|---|
| Airflow (Phase 6) | Included | **Dropped** |
| Fit for analytics / finance roles | Airflow adds setup time but is rarely what these roles ask about | Time goes into SQL, data quality, reconciliation, and presenting numbers, which are what these roles test |
| Time to a finished project | Longer | Shorter (target: 2–3 weeks) |

### Decision
**Core scope:**
1. Phase 2: Generate billing data (Python)
2. Phase 3: dbt models
3. Phase 4: dbt tests
4. Phase 5: Reconciliation report (the centerpiece)
5. Phase 6: Dashboard
6. Phase 7: Publish (README and docs)

**Dropped:** Airflow. The pipeline will run end to end with one simple command instead.

**Optional, only after the core is finished:** a short analysis notebook for data science roles (for example, flagging unusual usage or forecasting next month's revenue), and the dbt v2 upgrade.

### Why
- Analytics and finance roles care most about SQL, metric definitions, data quality, reconciliation, and clear reporting. Airflow is mostly a data engineering skill.
- The reconciliation report connects directly to my settlement background, so it should get the most time.
- A finished, simple project helps my job search more than a bigger one that takes much longer.

### Also decided: lighter logging for routine steps
Phase 1's build log recorded every command, which made it long. From Phase 2 on:
- **Full detail** for mistakes, decisions, and lessons.
- **Short entries** for routine steps (a few lines per milestone).
- **Screenshots** for results only: the data, test results, the reconciliation report, and the dashboard.

---

## Decision 3: Data design and planted errors (first version)

**Date:** November 13, 2026
**Phase:** 2 — Generate billing data
**Status:** First version. I may adjust it while building, and I will record any changes here.

### Context
The project needs fictional billing data with realistic errors for the dbt tests (Phase 4) and the reconciliation report (Phase 5) to find. I based the errors on problems I handled as a Senior Settlement Analyst at Fiserv / First Data, so each one connects to real work I have done.

### Tables
| Table | One row = |
|---|---|
| `customers` | one customer company |
| `subscriptions` | one plan a customer is on (Starter / Pro / Enterprise), with a monthly fee and included usage credits |
| `usage_events` | one customer's API usage for one day |
| `invoices` | one monthly bill: subscription fee + overage (usage beyond the included credits) |
| `payments` | money received against invoices |
| `credits_refunds` | money given back, linked to an invoice |

### Planted errors
| # | Error | Connects to my experience |
|---|---|---|
| 1 | **Unapplied cash:** a payment with no matching invoice | Resolving $4M in untraceable funds |
| 2 | **Duplicate payment:** the same payment recorded twice | Daily and monthly reconciliation discrepancies |
| 3 | **Short payment:** a customer pays less than the invoice | Variance analysis |
| 4 | **Unbilled usage:** usage that never made it onto an invoice | Billing variances and lost revenue |
| 5 | **Invoice math error:** total does not equal subscription fee + overage | Billing accuracy |
| 6 | **Month-end cutoff:** a payment dated in the wrong month | Month-end close |
| 7 | **Old unpaid invoices:** feed an aging report | Reducing monthly write-offs by $215K |

### Why
- Errors that really happen in billing make the project realistic and give me real stories for interviews.
- Each error maps to a check in Phase 4 or 5, and the Phase 5 report will suggest a correcting journal entry for each break, using my month-end close experience.

---

## Decision 4: Price snapshots and whole-month subscriptions

**Date:** November 13, 2026
**Phase:** 2 — Generate billing data

### Decision
1. **Copy the plan prices onto each subscription** (monthly fee, included tokens, overage price) instead of looking them up from the plan list every time.
2. **Subscriptions start on the 1st of a month and end on the last day of a month.** No partial months.

### Why
- **Price snapshots:** real billing systems save the price a customer signed up at. If Lumen AI changed its prices later, existing customers should not suddenly be billed at the new price. Saving the price on the subscription keeps each invoice traceable to the price that applied.
- **Whole months:** starting or ending mid-month would require **proration** (charging for part of a month). Proration is real and important, but it adds a lot of complexity. Leaving it out keeps the focus on the planted errors and the reconciliation. I could add it later as an extension.

---

## Decision 5: Overage rounding rule

**Date:** November 13, 2026
**Phase:** 2 — Generate billing data

### Context
Overage is priced per million tokens, so it often comes out to part of a cent. For example, 1,234,567 extra tokens at 150 cents per million is 185.185 cents. A billing system has to pick one rounding rule and apply it the same way every time, or invoices and reconciliations won't match.

### Decision
Round overage to the **nearest cent, with half a cent rounding up**. Calculate it with whole numbers only:

```python
(overage_tokens * cents_per_million + 500_000) // 1_000_000
```

Adding 500,000 (half of 1,000,000) before whole-number division rounds to the nearest cent.

### Why
- Whole-number math avoids decimal rounding errors entirely.
- One documented rule means anyone can recalculate any invoice and get the same number, which is what makes reconciliation possible.
- An `assert` in `main.py` checks the rule against a known example (10,000,000 tokens at 150 cents per million = 1,500 cents) before any invoices are built.
