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
