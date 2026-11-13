# Settings for the Lumen AI billing data generator.
# All settings live here, so nothing is hardcoded in the rest of the code.

from datetime import date

# Makes the random data the same on every run, so results can be checked and reproduced.
RANDOM_SEED = 42

# Small enough to check by hand, big enough to show patterns.
NUM_CUSTOMERS = 50

# 6 months of billing: enough history for an aging report and month-end cutoffs.
BILLING_START = date(2026, 1, 1)
BILLING_END = date(2026, 6, 30)

# Plans Lumen AI sells. Money is in cents (whole numbers) to avoid rounding errors with decimals.
# Bigger plans pay less per extra token (a common volume discount).
PLANS = {
    "Starter": {
        "monthly_fee_cents": 5_000,           # $50.00
        "included_tokens": 2_000_000,          # 2 million tokens per month
        "overage_cents_per_million": 200,      # $2.00 per extra million tokens
    },
    "Pro": {
        "monthly_fee_cents": 50_000,          # $500.00
        "included_tokens": 50_000_000,         # 50 million tokens per month
        "overage_cents_per_million": 150,      # $1.50 per extra million tokens
    },
    "Enterprise": {
        "monthly_fee_cents": 500_000,         # $5,000.00
        "included_tokens": 1_000_000_000,      # 1 billion tokens per month
        "overage_cents_per_million": 100,      # $1.00 per extra million tokens
    },
}


# The "month-end close" date: only payments received on or before this date are included.
# June invoices are dated July 1, so this gives them a month to be paid.
REPORT_DATE = date(2026, 7, 31)