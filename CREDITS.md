# Credits

## Learning material
- **Mehdi Ouazza (MotherDuck)**, *End-to-End Data Engineering Project*
  - Part 1: https://motherduck.com/videos/90/duckdb-python-end-to-end-data-engineering-project-13
  - Part 2: https://www.youtube.com/watch?v=SpfEQQXBGMQ
  - Part 3: https://youtu.be/ta_Pzc2EEEo
  - This series provided the project's foundation: Python ingestion into DuckDB, transformation and testing with dbt, and dashboards as code. I adapted it to a billing and revenue use case.

## Documentation
- **dbt Labs**, "Upgrading to v2": https://docs.getdbt.com/docs/dbt-versions/dbt-upgrade/upgrading-to-v2
- **DuckDB**, "DuckDB Now Ships inside dbt v2": https://duckdb.org/2026/09/22/dbt-fusion
- I used both for the dbt version decision (Decision 1 in the [decisions log](docs/decisions_log.md)).

## Tools
- **Python**: https://www.python.org
- **DuckDB**: https://duckdb.org
- **dbt Core** and **dbt-duckdb**: https://github.com/dbt-labs/dbt-core, https://github.com/duckdb/dbt-duckdb
- **Streamlit**: https://streamlit.io
- **Altair**: https://altair-viz.github.io
- **pandas**: https://pandas.pydata.org

## AI assistance
- **Claude (Anthropic)** provided technical guidance, helped write and test code, and reviewed my work. I designed the billing data and planted errors from my settlement experience, ran and validated every step, and made the design decisions.
