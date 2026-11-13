# Saving the generated tables: first to CSV files, then into a DuckDB database.
# The CSVs act like exports from Lumen AI's systems. DuckDB is where dbt will read them.
# Run the generator from the project folder, because these paths are relative to it.

import csv
from pathlib import Path

import duckdb

RAW_DIR = Path("data/raw")
DB_PATH = Path("data/lumen_billing.duckdb")


def write_csv(table_name, rows):
    """Write one table to data/raw/<table_name>.csv and return the file path."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)   # create the folder if it doesn't exist
    path = RAW_DIR / f"{table_name}.csv"

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()     # first line: column names
        writer.writerows(rows)   # one line per row

    return path


def load_into_duckdb(csv_paths):
    """Load each CSV into the DuckDB database as a table in the 'raw' schema.

    CREATE OR REPLACE means each run replaces the old table instead of adding to it,
    so running the generator twice never creates duplicate rows (idempotent).
    """
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for table_name, path in csv_paths.items():
        con.execute(
            f"CREATE OR REPLACE TABLE raw.{table_name} AS "
            f"SELECT * FROM read_csv('{path}', header = true)"
        )
        row_count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
        print(f"  raw.{table_name}: {row_count} rows")

    con.close()
    