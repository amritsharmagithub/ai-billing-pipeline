-- Control check on invoices: compare each invoice against its source data.
--   1. Usage check:   invoice usage_tokens vs. the sum of usage_events for that month
--   2. Math check:    total_cents vs. subscription_fee_cents + overage_cents
--   3. Missing check: months with usage but no invoice at all (the other direction)
-- Expected on clean data: 0 breaks on all three.

WITH monthly_usage AS (
    -- Source side: total tokens per subscription per month, from the usage events.
    SELECT
        subscription_id,
        CAST(date_trunc('month', usage_date) AS DATE) AS period_start,
        SUM(tokens_used)                              AS usage_tokens_from_events
    FROM raw.usage_events
    GROUP BY 1, 2
),

invoice_vs_usage AS (
    -- Invoice side, matched to the source side on subscription + month.
    SELECT
        i.invoice_id,
        i.usage_tokens                               AS usage_tokens_on_invoice,
        COALESCE(m.usage_tokens_from_events, 0)      AS usage_tokens_from_events,
        i.total_cents,
        i.subscription_fee_cents + i.overage_cents   AS expected_total_cents
    FROM raw.invoices AS i
    LEFT JOIN monthly_usage AS m
        ON  i.subscription_id = m.subscription_id
        AND i.period_start    = m.period_start
),

usage_without_invoice AS (
    -- The other direction: usage months that have no invoice at all.
    SELECT m.subscription_id, m.period_start
    FROM monthly_usage AS m
    LEFT JOIN raw.invoices AS i
        ON  m.subscription_id = i.subscription_id
        AND m.period_start    = i.period_start
    WHERE i.invoice_id IS NULL
)

SELECT
    COUNT(*)                                                                             AS invoices_checked,
    SUM(CASE WHEN usage_tokens_on_invoice <> usage_tokens_from_events THEN 1 ELSE 0 END) AS usage_breaks,
    SUM(CASE WHEN total_cents <> expected_total_cents THEN 1 ELSE 0 END)                 AS math_breaks,
    (SELECT COUNT(*) FROM usage_without_invoice)                                         AS months_with_no_invoice
FROM invoice_vs_usage;
