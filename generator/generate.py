# Functions that build each billing table.
# Each function returns a list of rows, and each row is a dictionary (column name -> value).

import random
from collections import defaultdict
from datetime import date, timedelta

from generator.config import NUM_CUSTOMERS, BILLING_START, BILLING_END, PLANS

# Word lists for building made-up company names, for example "Nova Analytics".
NAME_FIRST_WORDS = ["Blue", "North", "Bright", "Swift", "Prime", "Silver", "Green", "Atlas", "Nova", "Pixel"]
NAME_SECOND_WORDS = ["Labs", "Analytics", "Health", "Logistics", "Finance", "Media", "Robotics", "Retail", "Legal", "Studio"]

# "US" appears 3 times so it gets picked more often, like a real customer base.
COUNTRIES = ["US", "US", "US", "CA", "GB", "DE", "IN", "AU"]

# Most customers are small: 60% Starter, 30% Pro, 10% Enterprise.
PLAN_NAMES = ["Starter", "Pro", "Enterprise"]
PLAN_WEIGHTS = [60, 30, 10]

# Lumen AI's models. The smaller, cheaper model is used more often.
MODELS = ["lumen-small", "lumen-large"]
MODEL_WEIGHTS = [70, 30]

# Payment terms: invoices are due 30 days after the invoice date ("Net 30").
PAYMENT_TERMS_DAYS = 30


def last_day_of_month(year, month):
    """Return the last day of a month, for example 2026-03-31 for March 2026."""
    if month == 12:
        return date(year, 12, 31)
    # The day before the 1st of next month is the last day of this month.
    return date(year, month + 1, 1) - timedelta(days=1)


def calculate_overage_cents(overage_tokens, cents_per_million):
    """Price the overage, rounded to the nearest cent (half a cent rounds up).

    Uses whole numbers only. Adding 500,000 before dividing by 1,000,000
    rounds to the nearest cent without any decimal rounding errors.
    Example: 10,000,000 extra tokens at 150 cents per million = 1,500 cents ($15.00).
    """
    return (overage_tokens * cents_per_million + 500_000) // 1_000_000


def generate_customers():
    """Build the customers table: one row per customer company."""
    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):
        customers.append({
            "customer_id": f"C{i:03d}",                         # C001, C002, ... C050
            "company_name": f"{random.choice(NAME_FIRST_WORDS)} {random.choice(NAME_SECOND_WORDS)}",
            "country": random.choice(COUNTRIES),
            # Signed up sometime in the year before billing starts (during 2025).
            "signup_date": BILLING_START - timedelta(days=random.randint(1, 365)),
        })

    return customers


def generate_subscriptions(customers):
    """Build the subscriptions table: one plan per customer.

    Subscriptions start and end on whole months, so there is no proration
    (charging for part of a month). This is a simplification chosen on purpose.
    """
    subscriptions = []

    for i, customer in enumerate(customers, start=1):
        plan = random.choices(PLAN_NAMES, weights=PLAN_WEIGHTS)[0]
        prices = PLANS[plan]

        # Most start on Jan 1. About 1 in 5 join on Feb 1 or Mar 1 instead.
        if random.random() < 0.20:
            start_date = date(2026, random.choice([2, 3]), 1)
        else:
            start_date = BILLING_START

        # Most stay active. About 1 in 10 cancel at the end of March, April, or May.
        if random.random() < 0.10:
            end_date = last_day_of_month(2026, random.choice([3, 4, 5]))
        else:
            end_date = None   # None means still active

        subscriptions.append({
            "subscription_id": f"S{i:03d}",
            "customer_id": customer["customer_id"],
            "plan": plan,
            # Prices are copied from the plan at signup ("price snapshot"),
            # so a later price change would not affect existing customers.
            "monthly_fee_cents": prices["monthly_fee_cents"],
            "included_tokens": prices["included_tokens"],
            "overage_cents_per_million": prices["overage_cents_per_million"],
            "start_date": start_date,
            "end_date": end_date,
        })

    return subscriptions


def generate_usage_events(subscriptions):
    """Build the usage_events table: one row per subscription per active day.

    The usage data is kept clean on purpose. The "unbilled usage" error is planted
    later, in the invoices, so the break is easy to trace back to its source.
    """
    usage_events = []
    usage_number = 1

    for sub in subscriptions:
        # Each customer uses between 50% and 150% of their included tokens per month.
        # About half stay under their included tokens, and about half go over (overage).
        usage_level = random.uniform(0.5, 1.5)
        daily_average = sub["included_tokens"] * usage_level / 30

        # Active from the start date until the end date (or the end of the billing period).
        last_day = sub["end_date"] if sub["end_date"] is not None else BILLING_END
        day = sub["start_date"]

        while day <= last_day:
            # Daily usage goes up and down by up to 30%, like real traffic.
            tokens = int(daily_average * random.uniform(0.7, 1.3))

            usage_events.append({
                "usage_id": f"U{usage_number:05d}",            # U00001, U00002, ...
                "customer_id": sub["customer_id"],
                "subscription_id": sub["subscription_id"],
                "usage_date": day,
                "model": random.choices(MODELS, weights=MODEL_WEIGHTS)[0],
                "tokens_used": tokens,
            })

            usage_number += 1
            day += timedelta(days=1)

    return usage_events


def generate_invoices(subscriptions, usage_events):
    """Build the invoices table: one invoice per subscription per active month.

    These are the CORRECT invoices. Errors are planted in a separate step,
    so we always know exactly which errors were added.
    """
    # Step 1: Total tokens per subscription per month.
    # Example key: ("S001", 2026, 1) -> total tokens S001 used in January 2026.
    monthly_usage = defaultdict(int)
    for u in usage_events:
        key = (u["subscription_id"], u["usage_date"].year, u["usage_date"].month)
        monthly_usage[key] += u["tokens_used"]

    # Step 2: One invoice for each month each subscription was active.
    invoices = []
    invoice_number = 1

    for sub in subscriptions:
        last_day = sub["end_date"] if sub["end_date"] is not None else BILLING_END
        period_start = sub["start_date"]

        while period_start <= last_day:
            period_end = last_day_of_month(period_start.year, period_start.month)

            usage_tokens = monthly_usage[(sub["subscription_id"], period_start.year, period_start.month)]
            overage_tokens = max(0, usage_tokens - sub["included_tokens"])   # never below 0
            overage_cents = calculate_overage_cents(overage_tokens, sub["overage_cents_per_million"])

            # Billed on the 1st of the next month, due 30 days later.
            invoice_date = period_end + timedelta(days=1)

            invoices.append({
                "invoice_id": f"INV-{invoice_number:04d}",     # INV-0001, INV-0002, ...
                "customer_id": sub["customer_id"],
                "subscription_id": sub["subscription_id"],
                "period_start": period_start,
                "period_end": period_end,
                "invoice_date": invoice_date,
                "due_date": invoice_date + timedelta(days=PAYMENT_TERMS_DAYS),
                "usage_tokens": usage_tokens,
                "included_tokens": sub["included_tokens"],
                "overage_tokens": overage_tokens,
                "subscription_fee_cents": sub["monthly_fee_cents"],
                "overage_cents": overage_cents,
                "total_cents": sub["monthly_fee_cents"] + overage_cents,
            })

            invoice_number += 1
            period_start = period_end + timedelta(days=1)   # move to the 1st of next month

    return invoices



# How customers pay: card is most common, wire is used mostly by big customers.
PAYMENT_METHODS = ["card", "ACH", "wire"]
PAYMENT_METHOD_WEIGHTS = [50, 35, 15]


def generate_payments(invoices, report_date):
    """Build the payments table: money received against invoices.

    These are the CORRECT payments. Errors are planted in a separate step.
    - Most invoices are paid in full, 5-40 days after the invoice date.
      Invoices are due in 30 days, so some payments arrive late.
    - About 1 in 20 invoices are never paid. These feed the aging report.
    - Only payments received on or before the report date are included (month-end cutoff).
    """
    payments = []
    payment_number = 1

    for inv in invoices:
        # About 1 in 20 invoices are never paid.
        if random.random() < 0.05:
            continue   # "continue" skips to the next invoice

        payment_date = inv["invoice_date"] + timedelta(days=random.randint(5, 40))

        # Not received yet as of the report date, so it doesn't exist in our data.
        if payment_date > report_date:
            continue

        payments.append({
            "payment_id": f"P{payment_number:04d}",            # P0001, P0002, ...
            "invoice_id": inv["invoice_id"],
            "customer_id": inv["customer_id"],
            "payment_date": payment_date,
            "amount_cents": inv["total_cents"],                 # paid in full
            "payment_method": random.choices(PAYMENT_METHODS, weights=PAYMENT_METHOD_WEIGHTS)[0],
        })

        payment_number += 1

    return payments

