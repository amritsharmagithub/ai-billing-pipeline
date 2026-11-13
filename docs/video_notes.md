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

### What I learned (key takeaways)
I watched the full video (November 13, 2026). I kept these notes short on purpose: I'm applying the ideas hands-on in Phase 2, and the code and build log will show the details.

1. **Keep the main flow in one file.** The main pipeline file reads like a list of steps, and each step lives in its own module. You can understand the pipeline by reading one file.
2. **Parameterize the pipeline instead of hardcoding.** Values like the date window go into a Pydantic model and are passed in from the command line (he uses Fire to build the CLI from the model). The same pipeline can then be rerun for any period without editing code.
3. **Validate the source schema before loading.** A Pydantic model describes what a valid source row looks like, and the pipeline stops if the data doesn't match. Problems surface at the door instead of deep inside the pipeline.
4. **Test with small, typed sample data.** He built a pytest fixture by loading a few sample rows into an in-memory DuckDB table with a defined schema. He also tested that *bad* data raises an error, not only that good data passes.
5. **DuckDB makes moving data easy.** Once data is in DuckDB, one `COPY` command writes it to CSV, Parquet on S3 (partitioned by year and month), or MotherDuck.
6. **Make writes idempotent.** Before inserting a period's data, delete any existing rows for that period, so running the pipeline twice does not create duplicates.
7. **Keep secrets in a `.env` file that is in `.gitignore`.** (Same idea as my Phase 1 `.gitignore`.)
8. **Pick stable versions.** He used Python 3.11 instead of the newer 3.12 because libraries take time to catch up. Same reasoning as my Decision 1 to stay on dbt v1 for now.
9. **Scheduling isn't covered in the series.** He mentions tools like Airflow but leaves them out. I decided to leave Airflow out of my project too, because I'm targeting analytics and finance roles (see Decision 2).

### What I'll do differently for billing
| In the video | In my project | Why |
|---|---|---|
| Pulls real PyPI data from BigQuery | **Generates** fictional Lumen AI billing data in Python | No cloud account or query costs, and I control which errors go into the data |
| Uses Poetry and a Dev Container | Uses a `venv` + `requirements.txt` | Already set up in Phase 1, and simpler for me |
| Validation stops the pipeline on any bad row | **Two levels:** stop on *structural* problems (wrong types, missing columns); let *business* errors through (duplicate payments, refunds larger than the charge, usage without a subscription) | Those business errors are the point of the project. dbt tests and the reconciliation report need to find them. |
| Idempotent writes by time window | **Essential** for billing: rerunning a billing period must never double-count charges or payments | Double-billing is one of the most serious errors in billing |
| Parameters: date window, project, destination | Parameters: billing period, number of customers, error rate, and a **random seed** | A fixed seed makes the fake data the same every run, so results can be checked and reproduced |
| Writes to CSV, S3, and MotherDuck | Writes to a **local DuckDB file** only, for now | Keeps the project free and simple. Cloud storage can come later if needed. |
| (Not covered) | Store money as **integer cents** or `Decimal`, never float | Floats can't represent amounts like 0.10 exactly, which causes rounding breaks in reconciliation |

### Source
Overview and timestamps are based on the video page and transcript at the Part 1 link above. All credit for the content goes to Mehdi Ouazza and MotherDuck.
