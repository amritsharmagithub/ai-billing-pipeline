# Run a SQL file against the Lumen AI DuckDB database and print the result.
# Usage (from the project folder): python run_sql.py queries/01_plan_mix.sql

import sys

import duckdb

from generator.db import DB_PATH


def main():
    # sys.argv holds the words typed after "python": [run_sql.py, queries/01_plan_mix.sql]
    if len(sys.argv) != 2:
        print("Usage: python run_sql.py <path to .sql file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    with open(sql_file) as f:
        sql = f.read()

    # read_only=True: a query can never accidentally change or delete the data.
    con = duckdb.connect(str(DB_PATH), read_only=True)
    con.sql(sql).show()
    con.close()


if __name__ == "__main__":
    main()
    