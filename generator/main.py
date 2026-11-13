# Main flow for the Lumen AI billing data generator.
# Reading this file should tell you every step of the generator.
# Run it from the project folder with: python -m generator.main

import random
from collections import Counter

from generator.config import RANDOM_SEED
from generator.generate import (
    calculate_overage_cents,
    generate_customers,
    generate_subscriptions,
    generate_usage_events,
    generate_invoices,
)
from generator.db import write_csv, load_into_duckdb, DB_PATH


def main():
    # Step 1: Set the seed so the random data is the same on every run.
    random.seed(RANDOM_SEED)

    # Step 2: Check the overage math against a known example before using it.
    # Pro plan, 60 million tokens: 10 million over, at 150 cents per million = 1,500 cents.
    assert calculate_overage_cents(10_000_000, 150) == 1_500, "Overage math is wrong!"

    # Step 3: Build the tables.
    customers = generate_customers()
    subscriptions = generate_subscriptions(customers)
    usage_events = generate_usage_events(subscriptions)
    invoices = generate_invoices(subscriptions, usage_events)

    # Step 4: Quick check of what was built.
    print(f"Customers: {len(customers)} rows")
    print(f"Subscriptions: {len(subscriptions)} rows")
    print("Plans:", Counter(s["plan"] for s in subscriptions))
    print("Cancelled:", sum(1 for s in subscriptions if s["end_date"] is not None))
    print(f"Usage events: {len(usage_events)} rows")
    print(f"Total tokens used: {sum(u['tokens_used'] for u in usage_events):,}")
    print(f"Invoices: {len(invoices)} rows")
    print(f"Invoices with overage: {sum(1 for i in invoices if i['overage_cents'] > 0)}")
    print(f"Total billed: ${sum(i['total_cents'] for i in invoices) / 100:,.2f}")

    # Step 5: Save each table to a CSV file.
    tables = {
        "customers": customers,
        "subscriptions": subscriptions,
        "usage_events": usage_events,
        "invoices": invoices,
    }
    csv_paths = {name: write_csv(name, rows) for name, rows in tables.items()}
    print(f"\nWrote {len(csv_paths)} CSV files to data/raw/")

    # Step 6: Load the CSVs into DuckDB.
    print(f"Loading into {DB_PATH}:")
    load_into_duckdb(csv_paths)


# This runs main() only when the file is run directly, not when another file imports it.
if __name__ == "__main__":
    main()
    