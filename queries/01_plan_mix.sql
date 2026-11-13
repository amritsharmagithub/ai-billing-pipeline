-- Question: How many customers are on each plan, and how much monthly
-- subscription revenue does each plan bring in?
-- Note: money is stored in cents, so divide by 100.0 to get dollars.

SELECT
    plan,
    COUNT(*)                         AS customers,
    SUM(monthly_fee_cents) / 100.0   AS monthly_fees_usd
FROM raw.subscriptions
GROUP BY plan
ORDER BY monthly_fees_usd DESC;
