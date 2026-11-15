# Lessons Learned

The main technical skills I learned while building this project.

## dbt

- **Layered models.** Staging views clean up names and types, mart tables hold business logic, and report tables answer specific questions. Each layer builds on the one before it.
- **`source()` and `ref()`.** These link models together, so dbt works out the run order on its own and draws the lineage graph.
- **Tests.** Generic tests (`not_null`, `unique`, `accepted_values`, `relationships`) are declared in YAML. A singular test is a SQL query that fails if it returns any rows. `severity: warn` flags an issue without stopping the build.
- **Macros and variables.** A Jinja macro keeps the currency conversion in one place. A project variable sets the report date without editing SQL.

## SQL

- **Window functions.** `row_number()` and `first_value()` find duplicate payments by comparing rows within a group.
- **`QUALIFY`.** Filters on a window function result directly, without a subquery.
- **Full outer joins.** Compare two sides and keep unmatched rows from both, which is how reconciliation works.
- **Regular expressions.** `regexp_extract()` pulls IDs out of text fields so they can be matched.

## DuckDB and Python

- **DuckDB as a local warehouse.** It loads CSV files with `read_csv` and runs SQL on a single file with no server.
- **Idempotent loads.** `CREATE OR REPLACE` means rerunning the pipeline never duplicates data.
- **Read-only connections.** The report and dashboard open the database read-only, so they can't change data or lock it.
- **Reproducible data.** A fixed random seed makes every run generate the same data.
- **Exact money math.** Store amounts as integer cents and convert to `DECIMAL`, never floats, so totals don't drift.
- **Running modules.** `python -m package.module` from the project root keeps imports working across folders.

## Dashboard

- **Streamlit and Altair.** A Streamlit app reads from DuckDB into pandas, and Altair builds the charts declaratively from that data.
