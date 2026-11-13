# Main flow for the Lumen AI billing data generator.
# Reading this file should tell you every step of the generator.
# Run it from the project folder with: python -m generator.main

import random
from collections import Counter

from generator.config import RANDOM_SEED, REPORT_DATE
from generator.generate import (
    calculate_overage_cents,
    generate_customers,
    generate_subscriptions,
    generate_usage_events,
    generate_invoices,
    generate_payments,
)
from generator.errors import plant_errors
from generator.db import write_csv, load_into_duckdb, DB_PATH


def main():
    # Step 1: Set the seed so the random data is the same on every run.
    random.seed(RANDOM_SEED)

    # Step 2: Check the overage math against a known example before using it.
    # Pro plan, 60 million tokens: 10 million over, at 150 cents per million = 1,500 cents.
    assert calculate_overage_cents(10_000_000, 150) == 1_500, "Overage math is wrong!"

    # Step 3: Build the clean tables.
    customers = generate_customers()
    subscriptions = generate_subscriptions(customers)
    usage_events = generate_usage_events(subscriptions)
    invoices = generate_invoices(subscriptions, usage_events)
    payments = generate_payments(invoices, REPORT_DATE)

    # Step 4: Plant the errors, and keep the answer key.
    invoices, payments, planted_errors = plant_errors(invoices, payments, subscriptions, REPORT_DATE)

    # Step 5: Quick check of what was built.
    print(f"Customers: {len(customers)} rows")
    print(f"Subscriptions: {len(subscriptions)} rows")
    print(f"Usage events: {len(usage_events)} rows")
    print(f"Invoices: {len(invoices)} rows")
    print(f"Payments: {len(payments)} rows (as of {REPORT_DATE})")
    print(f"Total billed: ${sum(i['total_cents'] for i in invoices) / 100:,.2f}")
    print(f"Total collected: ${sum(p['amount_cents'] for p in payments) / 100:,.2f}")
    print(f"\nPlanted errors: {len(planted_errors)}")
    for error_type, count in sorted(Counter(e["error_type"] for e in planted_errors).items()):
        print(f"  {error_type}: {count}")

    # Step 6: Save each table to a CSV file.
    # planted_errors is the answer key, used in Phase 5 to check the reconciliation found everything.
    tables = {
        "customers": customers,
        "subscriptions": subscriptions,
        "usage_events": usage_events,
        "invoices": invoices,
        "payments": payments,
        "planted_errors": planted_errors,
    }
    csv_paths = {name: write_csv(name, rows) for name, rows in tables.items()}
    print(f"\nWrote {len(csv_paths)} CSV files to data/raw/")

    # Step 7: Load the CSVs into DuckDB.
    print(f"Loading into {DB_PATH}:")
    load_into_duckdb(csv_paths)


# This runs main() only when the file is run directly, not when another file imports it.
if __name__ == "__main__":
    main()
