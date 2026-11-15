-- Mart: invoices with what has been paid against them, as of the report date.
-- One row per invoice. Used by the reconciliation report and the aging report.

with invoices as (

    select * from {{ ref('stg_invoices') }}

),

-- Payments that point to an invoice. Unapplied cash (no invoice_id) is left out here,
-- because nobody knows yet which invoice it belongs to. The reconciliation handles it.
payments_per_invoice as (

    select
        invoice_id,
        count(*)            as payment_count,
        sum(amount_usd)     as amount_paid_usd,
        max(payment_date)   as last_payment_date
    from {{ ref('stg_payments') }}
    where invoice_id is not null
    group by invoice_id

),

joined as (

    select
        invoices.invoice_id,
        invoices.customer_id,
        invoices.subscription_id,
        invoices.period_start,
        invoices.invoice_date,
        invoices.due_date,
        invoices.subscription_fee_usd,
        invoices.overage_usd,
        invoices.total_usd,
        coalesce(payments.payment_count, 0)                         as payment_count,
        coalesce(payments.amount_paid_usd, 0)                       as amount_paid_usd,
        invoices.total_usd - coalesce(payments.amount_paid_usd, 0)  as balance_due_usd,
        payments.last_payment_date
    from invoices
    left join payments_per_invoice as payments
        on invoices.invoice_id = payments.invoice_id

),

final as (

    select
        *,

        case
            when amount_paid_usd = 0              then 'unpaid'
            when amount_paid_usd < total_usd      then 'partially_paid'
            when amount_paid_usd = total_usd      then 'paid'
            else                                       'overpaid'
        end as payment_status,

        -- Days past due, as of the report date. Zero if nothing is owed or it isn't due yet.
        case
            when balance_due_usd > 0 and due_date < date '{{ var("report_date") }}'
                then date_diff('day', due_date, date '{{ var("report_date") }}')
            else 0
        end as days_past_due

    from joined

)

select
    *,
    -- Aging: how long an open balance has been overdue (standard accounts receivable buckets).
    case
        when balance_due_usd < 0   then 'credit_balance'   -- customer paid more than owed
        when balance_due_usd = 0   then 'settled'
        when days_past_due = 0     then 'current'          -- owed, but not due yet
        when days_past_due <= 30   then '1-30'
        when days_past_due <= 60   then '31-60'
        when days_past_due <= 90   then '61-90'
        else                            '90+'
    end as aging_bucket
from final
