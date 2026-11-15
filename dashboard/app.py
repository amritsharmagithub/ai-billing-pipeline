# Lumen AI billing dashboard (Streamlit).
# Reads the dbt models from the local DuckDB database (read-only), so run `dbt build` first.
# Run from the project folder: streamlit run dashboard/app.py

import sys
from pathlib import Path

import altair as alt
import duckdb
import streamlit as st

# Let this file import the project's settings, no matter which folder it's run from.
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_DIR))
from generator.config import REPORT_DATE  # noqa: E402

DB_PATH = PROJECT_DIR / "data" / "lumen_billing.duckdb"

st.set_page_config(page_title="Lumen AI Billing Dashboard", layout="wide")

# Chart colors, from a palette checked for color-blind readers (blue, then orange).
BLUE = "#2a78d6"
ORANGE = "#eb6834"

# Plain-English names for the reconciliation break types.
BREAK_NAMES = {
    "unapplied_cash": "Unapplied cash",
    "duplicate_payment": "Duplicate payment",
    "short_payment_wire_fee": "Short payment (wire fee)",
    "short_payment_unexplained": "Short payment (unexplained)",
    "unbilled_usage_missing_invoice": "Missing invoice",
    "unbilled_usage_understated": "Understated usage",
    "invoice_math_error": "Invoice math error",
    "cutoff_error": "Month-end cutoff error",
    "aged_90_plus": "Aged 90+ days",
}

AGING_ORDER = ["current", "1-30", "31-60", "61-90", "90+"]


@st.cache_data
def query(sql):
    """Run a query against the DuckDB file (read-only) and return a table (DataFrame)."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()


def money(amount):
    """Format a number as dollars, for example 1234.5 -> $1,234.50."""
    return f"${amount:,.2f}"


# --- Load the data ------------------------------------------------------------

invoices = query("""
    select i.*, s.plan_name
    from main_marts.fct_invoices as i
    join main_staging.stg_subscriptions as s on i.subscription_id = s.subscription_id
""")
monthly = query("select * from main_marts.fct_monthly_revenue order by month")
breaks = query("select * from main_reports.rpt_reconciliation_breaks")
answer_key = query("select * from main_reports.rpt_reconciliation_vs_answer_key")
unapplied = query("select coalesce(sum(amount_usd), 0) as amount from main_staging.stg_payments where invoice_id is null")

for table in (invoices, monthly, breaks):
    for column in table.columns:
        if column.endswith("_usd"):
            table[column] = table[column].astype(float)

# --- Header and headline numbers ----------------------------------------------

st.title("Lumen AI: Billing & Revenue Dashboard")
st.caption(f"As of {REPORT_DATE:%B %d, %Y} (month-end close). Data: dbt models in DuckDB. "
           "Lumen AI is a fictional AI API company; all data is generated.")

total_billed = invoices["total_usd"].sum()
total_collected = monthly["total_collected_usd"].sum()
net_owed = invoices["balance_due_usd"].sum() - float(unapplied["amount"][0])
error_breaks = breaks[breaks["break_type"] != "aged_90_plus"]
found = int(answer_key["found"].sum())
planted = int(answer_key["planted"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total billed", money(total_billed))
col2.metric("Total collected", money(total_collected))
col3.metric("Still owed by customers", money(net_owed))
col4.metric("Reconciliation breaks", f"{len(error_breaks)} ({money(error_breaks['amount_usd'].sum())})",
            help=f"Planted errors found: {found} of {planted}")

st.divider()

# --- Billed vs. collected by month --------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Billed vs. collected by month")
    monthly_long = monthly.melt(
        id_vars="month",
        value_vars=["total_billed_usd", "total_collected_usd"],
        var_name="measure",
        value_name="amount",
    )
    monthly_long["measure"] = monthly_long["measure"].map(
        {"total_billed_usd": "Billed", "total_collected_usd": "Collected"}
    )
    chart = (
        alt.Chart(monthly_long)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("yearmonth(month):O", title=None, axis=alt.Axis(format="%b %Y", labelAngle=0)),
            xOffset=alt.XOffset("measure:N", sort=["Billed", "Collected"], scale=alt.Scale(paddingInner=0.1)),  # small gap between bars
            y=alt.Y("amount:Q", title="Amount ($)", axis=alt.Axis(format="$,.0f")),
            color=alt.Color(
                "measure:N",
                scale=alt.Scale(domain=["Billed", "Collected"], range=[BLUE, ORANGE]),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=[
                alt.Tooltip("yearmonth(month):O", title="Month", format="%B %Y"),
                alt.Tooltip("measure:N", title="Measure"),
                alt.Tooltip("amount:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    st.caption("Invoices go out the month after the service, so collections lag billing by about a month. "
               "The $500 collected in January, before any invoice was sent, is a cutoff error.")

with right:
    st.subheader("Total billed by plan")
    by_plan = (
        invoices.groupby("plan_name", as_index=False)
        .agg(billed=("total_usd", "sum"), customers=("customer_id", "nunique"))
        .sort_values("billed", ascending=False)
    )
    chart = (
        alt.Chart(by_plan)
        .mark_bar(color=BLUE, cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("plan_name:N", title=None, sort="-x"),
            x=alt.X("billed:Q", title="Total billed ($)", axis=alt.Axis(format="$,.0f")),
            tooltip=[
                alt.Tooltip("plan_name:N", title="Plan"),
                alt.Tooltip("customers:Q", title="Customers"),
                alt.Tooltip("billed:Q", title="Billed", format="$,.2f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    st.caption("A few Enterprise customers bring in the largest share of billing (revenue concentration).")

st.divider()

# --- Aging and reconciliation breaks ------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Open balances by aging bucket")
    open_invoices = invoices[invoices["aging_bucket"].isin(AGING_ORDER)]
    aging = (
        open_invoices.groupby("aging_bucket")
        .agg(balance=("balance_due_usd", "sum"), invoices=("invoice_id", "count"))
        # Show every bucket, even empty ones, so a gap is visible instead of hidden.
        .reindex(AGING_ORDER, fill_value=0)
        .rename_axis("aging_bucket")
        .reset_index()
    )
    chart = (
        alt.Chart(aging)
        .mark_bar(color=BLUE, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("aging_bucket:N", title="Days past due", sort=AGING_ORDER, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("balance:Q", title="Balance owed ($)", axis=alt.Axis(format="$,.0f")),
            tooltip=[
                alt.Tooltip("aging_bucket:N", title="Bucket"),
                alt.Tooltip("invoices:Q", title="Invoices"),
                alt.Tooltip("balance:Q", title="Balance", format="$,.2f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    st.caption("Most of the open balance is current (June invoices, due July 31). "
               "Invoices 90+ days past due are candidates for collections or write-off.")

with right:
    st.subheader("Reconciliation breaks by type")
    by_type = (
        breaks.assign(break_name=breaks["break_type"].map(BREAK_NAMES))
        .groupby("break_name", as_index=False)
        .agg(amount=("amount_usd", "sum"), count=("record_id", "count"))
    )
    chart = (
        alt.Chart(by_type)
        .mark_bar(color=BLUE, cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("break_name:N", title=None, sort="-x", axis=alt.Axis(labelLimit=250)),
            x=alt.X("amount:Q", title="Amount ($)", axis=alt.Axis(format="$,.0f")),
            tooltip=[
                alt.Tooltip("break_name:N", title="Break"),
                alt.Tooltip("count:Q", title="Count"),
                alt.Tooltip("amount:Q", title="Amount", format="$,.2f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    st.caption(f"Planted errors found by the reconciliation rules: {found} of {planted}, with no extra breaks.")

st.divider()

# --- Break details, with a filter -----------------------------------------------

st.subheader("Break details")
choices = ["All"] + [BREAK_NAMES[t] for t in BREAK_NAMES if t in set(breaks["break_type"])]
picked = st.selectbox("Break type", choices)

details = breaks.assign(
    break_name=breaks["break_type"].map(BREAK_NAMES),
    # Same order as the reconciliation report: errors first, collections items last.
    sort_order=breaks["break_type"].map({t: i for i, t in enumerate(BREAK_NAMES)}),
).sort_values(["sort_order", "record_id"])
if picked != "All":
    details = details[details["break_name"] == picked]

details = details.assign(
    journal_entry=details.apply(
        lambda row: f"Dr {row['debit_account']} / Cr {row['credit_account']}" if row["debit_account"] else "None yet",
        axis=1,
    )
)
st.dataframe(
    details[["break_name", "record_id", "customer_id", "amount_usd", "details", "suggested_action", "journal_entry"]],
    column_config={
        "break_name": "Break",
        "record_id": "Record",
        "customer_id": "Customer",
        "amount_usd": st.column_config.NumberColumn("Amount", format="$%.2f"),
        "details": "Details",
        "suggested_action": "Suggested action",
        "journal_entry": "Journal entry",
    },
    hide_index=True,
    width="stretch",
)

st.caption("Built by Amrit Sharma. Pipeline: Python generator → DuckDB → dbt → Streamlit. "
           "Approach inspired by Mehdi Ouazza's MotherDuck end-to-end project series.")
