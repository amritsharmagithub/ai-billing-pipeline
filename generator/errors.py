# Planting deliberate errors in the clean billing data.
# Every error is recorded in an answer key (planted_errors), so the dbt tests and the
# reconciliation report in Phase 5 can be checked: did they find ALL of them?
# Each invoice (and its payments) gets at most one error, so every break has exactly one cause.

import random
from datetime import timedelta

from generator.generate import calculate_overage_cents

# Some banks deduct a fee from incoming wire payments, so the customer's payment arrives short.
WIRE_FEE_CENTS = 2_500   # $25.00


def plant_errors(invoices, payments, subscriptions, report_date):
    """Plant errors in the invoices and payments.

    Returns (invoices, payments, planted_errors). planted_errors is the answer key.
    """
    # Overage price per subscription, needed to re-price understated invoices.
    rate_by_subscription = {s["subscription_id"]: s["overage_cents_per_million"] for s in subscriptions}

    planted_errors = []
    touched_invoice_ids = set()   # invoices that already have an error

    def record(error_type, record_id, details):
        """Add one line to the answer key."""
        planted_errors.append({
            "error_id": f"E{len(planted_errors) + 1:02d}",
            "error_type": error_type,
            "record_id": record_id,
            "details": details,
        })

    def pick_invoices(pool, how_many):
        """Pick invoices that don't have an error yet, and mark them as used."""
        available = [i for i in pool if i["invoice_id"] not in touched_invoice_ids]
        chosen = random.sample(available, how_many)
        for inv in chosen:
            touched_invoice_ids.add(inv["invoice_id"])
        return chosen

    def pick_payments(pool, how_many):
        """Pick payments whose invoice doesn't have an error yet, and mark the invoice as used."""
        available = [p for p in pool if p["invoice_id"] not in touched_invoice_ids]
        chosen = random.sample(available, how_many)
        for pay in chosen:
            touched_invoice_ids.add(pay["invoice_id"])
        return chosen

    # ---------------------------------------------------------------
    # Invoice errors
    # ---------------------------------------------------------------

    # Error 4a: Unbilled usage, missing invoice. The usage happened, but no invoice was ever created.
    # The invoice and its payment are removed, which also leaves a gap in the invoice numbers.
    mid_period = [i for i in invoices if 2 <= i["period_start"].month <= 5]
    missing = pick_invoices(mid_period, 2)
    missing_ids = {i["invoice_id"] for i in missing}
    for inv in missing:
        record("unbilled_usage_missing_invoice", inv["invoice_id"],
               f"No invoice created for {inv['subscription_id']} for {inv['period_start']:%B %Y}. "
               f"{inv['usage_tokens']:,} tokens were used but never billed "
               f"(${inv['total_cents'] / 100:,.2f} of lost revenue).")
    invoices = [i for i in invoices if i["invoice_id"] not in missing_ids]
    payments = [p for p in payments if p["invoice_id"] not in missing_ids]

    # Error 4b: Unbilled usage, understated. The invoice shows 20-40% less usage than really happened.
    # The overage and total are recalculated from the wrong usage, so the invoice math still looks right.
    with_overage = [i for i in invoices if i["overage_tokens"] > 0]
    for inv in pick_invoices(with_overage, 2):
        correct_total = inv["total_cents"]
        inv["usage_tokens"] = int(inv["usage_tokens"] * (1 - random.uniform(0.20, 0.40)))
        inv["overage_tokens"] = max(0, inv["usage_tokens"] - inv["included_tokens"])
        inv["overage_cents"] = calculate_overage_cents(
            inv["overage_tokens"], rate_by_subscription[inv["subscription_id"]])
        inv["total_cents"] = inv["subscription_fee_cents"] + inv["overage_cents"]
        record("unbilled_usage_understated", inv["invoice_id"],
               f"Invoice usage understated. Under-billed by ${(correct_total - inv['total_cents']) / 100:,.2f}.")

    # Error 5: Invoice math error. The overage was left off the total (total = subscription fee only).
    # Only invoices with at least $20 of overage, so each error is large enough to matter.
    with_overage = [i for i in invoices if i["overage_cents"] >= 2_000]
    for inv in pick_invoices(with_overage, 3):
        record("invoice_math_error", inv["invoice_id"],
               f"Total should be ${(inv['subscription_fee_cents'] + inv['overage_cents']) / 100:,.2f} "
               f"but shows ${inv['subscription_fee_cents'] / 100:,.2f}: "
               f"overage of ${inv['overage_cents'] / 100:,.2f} was left off.")
        inv["total_cents"] = inv["subscription_fee_cents"]

    # Customers pay what their invoice says, so payments for changed invoices follow the new total.
    # This keeps each error to a single cause (no extra overpayment breaks).
    invoice_by_id = {i["invoice_id"]: i for i in invoices}
    for pay in payments:
        if pay["invoice_id"] in touched_invoice_ids:
            pay["amount_cents"] = invoice_by_id[pay["invoice_id"]]["total_cents"]

    # ---------------------------------------------------------------
    # Payment errors
    # ---------------------------------------------------------------

    # Error 3a: Short payment, wire fee. The customer's bank deducted a $25.00 fee from a wire payment.
    wires = [p for p in payments if p["payment_method"] == "wire" and p["amount_cents"] > WIRE_FEE_CENTS]
    for pay in pick_payments(wires, 2):
        pay["amount_cents"] -= WIRE_FEE_CENTS
        record("short_payment_wire_fee", pay["payment_id"],
               f"Wire payment for {pay['invoice_id']} arrived $25.00 short (bank fee deducted).")

    # Error 3b: Short payment, no clear reason (for example, a dispute). Paid 5-20% less than invoiced.
    for pay in pick_payments(payments, 2):
        invoiced = pay["amount_cents"]
        pay["amount_cents"] = int(invoiced * (1 - random.uniform(0.05, 0.20)))
        record("short_payment_unexplained", pay["payment_id"],
               f"Paid ${pay['amount_cents'] / 100:,.2f} against {pay['invoice_id']} "
               f"for ${invoiced / 100:,.2f}: ${(invoiced - pay['amount_cents']) / 100:,.2f} short, no reason given.")

    # Error 6: Month-end cutoff. The payment is dated in the prior month, before the invoice even existed.
    for pay in pick_payments(payments, 3):
        invoice_date = invoice_by_id[pay["invoice_id"]]["invoice_date"]
        correct_date = pay["payment_date"]
        pay["payment_date"] = invoice_date - timedelta(days=random.randint(1, 3))
        record("cutoff_error", pay["payment_id"],
               f"Payment for {pay['invoice_id']} dated {pay['payment_date']} (prior month), "
               f"but received {correct_date}. The invoice is dated {invoice_date}.")

    # New payments get the next free payment number.
    next_number = max(int(p["payment_id"][1:]) for p in payments) + 1

    # Error 2: Duplicate payment. An existing payment recorded a second time, under a new payment ID.
    for pay in pick_payments(payments, 3):
        duplicate = dict(pay)   # copy every column
        duplicate["payment_id"] = f"P{next_number:04d}"
        next_number += 1
        payments.append(duplicate)
        record("duplicate_payment", duplicate["payment_id"],
               f"Duplicate of {pay['payment_id']}: same invoice ({pay['invoice_id']}), "
               f"amount (${pay['amount_cents'] / 100:,.2f}), and date.")

    # Error 1: Unapplied cash. A customer pays an unpaid invoice, but the payment has no invoice reference.
    # The money is real; the team just doesn't know what it's for until someone matches it.
    paid_ids = {p["invoice_id"] for p in payments}
    unpaid = [i for i in invoices if i["invoice_id"] not in paid_ids]
    for inv in pick_invoices(unpaid, 3):
        payment_date = min(inv["invoice_date"] + timedelta(days=random.randint(5, 25)), report_date)
        payment = {
            "payment_id": f"P{next_number:04d}",
            "invoice_id": None,   # no invoice reference: this is what makes it "unapplied"
            "customer_id": inv["customer_id"],
            "payment_date": payment_date,
            "amount_cents": inv["total_cents"],
            "payment_method": "ACH",
        }
        next_number += 1
        payments.append(payment)
        record("unapplied_cash", payment["payment_id"],
               f"${inv['total_cents'] / 100:,.2f} received from {inv['customer_id']} with no invoice reference. "
               f"It matches unpaid invoice {inv['invoice_id']}.")

    # Keep payments in date order, like a real bank or payments report.
    payments.sort(key=lambda p: (p["payment_date"], p["payment_id"]))

    return invoices, payments, planted_errors
