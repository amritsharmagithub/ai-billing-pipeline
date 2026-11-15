-- Mart: billing and cash collection by month.
-- One row per month. Shows two views side by side:
--   billed:    invoices by the month the service was used (when revenue is earned)
--   collected: payments by the month the cash arrived (when cash comes in)

with billed as (

    select
        period_start                            as month,
        count(*)                                as invoices,
        count(distinct customer_id)             as billed_customers,
        sum(subscription_fee_usd)               as subscription_revenue_usd,
        sum(overage_usd)                        as overage_revenue_usd,
        sum(total_usd)                          as total_billed_usd
    from {{ ref('stg_invoices') }}
    group by period_start

),

collected as (

    -- Includes unapplied cash: the money arrived, even if it isn't matched to an invoice yet.
    select
        cast(date_trunc('month', payment_date) as date)   as month,
        count(*)                                           as payments,
        sum(amount_usd)                                    as total_collected_usd
    from {{ ref('stg_payments') }}
    group by 1

)

select
    coalesce(billed.month, collected.month)                 as month,
    coalesce(billed.invoices, 0)                            as invoices,
    coalesce(billed.billed_customers, 0)                    as billed_customers,
    coalesce(billed.subscription_revenue_usd, 0)            as subscription_revenue_usd,
    coalesce(billed.overage_revenue_usd, 0)                 as overage_revenue_usd,
    coalesce(billed.total_billed_usd, 0)                    as total_billed_usd,
    coalesce(collected.payments, 0)                         as payments,
    coalesce(collected.total_collected_usd, 0)              as total_collected_usd
from billed
full outer join collected
    on billed.month = collected.month
order by month
