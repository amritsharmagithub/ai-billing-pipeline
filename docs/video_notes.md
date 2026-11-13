# Video Notes

Notes from the video series I learned from, with timestamps. For each section I write what was shown, what I learned, and what I did differently for my billing project.

**Series:** "DuckDB & Python: End-To-End Data Engineering Project" by **Mehdi Ouazza (MotherDuck)**, 3 parts.
- Part 1: https://motherduck.com/videos/90/duckdb-python-end-to-end-data-engineering-project-13
- Part 2: https://www.youtube.com/watch?v=SpfEQQXBGMQ

---

## Part 1: Ingestion with Python and DuckDB (about 42 minutes, published February 2, 2024)

### What the video covers (overview)
The video builds the ingestion part of a pipeline that turns PyPI download data (from a public BigQuery dataset) into usage insights for the DuckDB Python package. It covers the pipeline architecture, Pydantic models for CLI parameters and the source schema, schema validation, logging, unit tests, and saving results with DuckDB to a local CSV, S3, or MotherDuck. Later parts cover transformation with dbt and a dashboard.

Approximate timestamps (from the transcript; the page has no official chapters):

| Time | Topic |
|---|---|
| 0:00 | Intro and goals |
| ~1:20 | Architecture |
| ~3:30 | GCP and BigQuery setup |
| ~8:35 | Dev Container setup |
| ~10:06 | Installing dependencies |
| ~13:52 | Pipeline entry point and Makefile |
| ~15:00 | BigQuery client module |
| ~19:08 | Pydantic parameter models |
| ~22:46 | Fire CLI |
| ~26:32 | Source schema validation |
| ~32:06 | DuckDB helper functions |
| ~35:02 | Running the pipeline to CSV, S3, and MotherDuck |
| ~40:12 | Recap |

### How Part 1 maps to my project
| In the video | In my project |
|---|---|
| Pulls real data from BigQuery | I **generate** fictional billing data in Python (Phase 2), so I skip the GCP/BigQuery setup |
| Pydantic model for the source schema | Could validate my billing records (for example, invoice amounts, currencies, dates) |
| Schema validation step | Useful for catching bad data early. But my project has *deliberate* errors, so I need to decide which errors to catch at ingestion and which to let through for dbt tests and reconciliation to find |
| Logging and unit tests | Same idea for my data generator |
| Saves data with DuckDB | Same: I load the generated data into DuckDB |

### My notes while watching
*(I fill these in myself as I watch.)*

| Time | What was shown | What I learned | What I'll do differently for billing |
|---|---|---|---|
| | | | |

### Questions I had
-

### Source
Overview and timestamps are based on the video page and transcript at the Part 1 link above. All credit for the content goes to Mehdi Ouazza and MotherDuck.
