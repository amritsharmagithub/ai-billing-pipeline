-- Report: reconciliation breaks.
-- One row per break found by a rule. The rules only use the billing data, never the answer key.
-- Each break has a dollar amount, a suggested action, and a suggested journal entry.

with invoices as (

    select * from {{ ref('fct_invoices') }}

),

payments as (

    select * from {{ ref('stg_payments') }}

),

subscriptions as (

    select * from {{ ref('stg_subscriptions') }}

),

-- Actual usage per subscription per month, from the usage events.
monthly_usage as (

    select
        subscription_id,
        cast(date_trunc('month', usage_date) as date)   as period_start,
        sum(tokens_used)                                 as usage_tokens
    from {{ ref('stg_usage_events') }}
    group by 1, 2

),

-- What each month's invoice should have been, recalculated from actual usage.
-- Same rounding rule as the generator: nearest cent, half a cent rounds up.
expected_invoices as (

    select
        u.subscription_id,
        s.customer_id,
        u.period_start,
        u.usage_tokens,
        s.monthly_fee_cents
            + (greatest(u.usage_tokens - s.included_tokens, 0) * s.overage_cents_per_million + 500000)
              // 1000000                                    as expected_total_cents
    from monthly_usage as u
    inner join subscriptions as s
        on u.subscription_id = s.subscription_id

),

-- 1. Unapplied cash: a payment with no invoice reference.
--    Suggest a match: an open invoice for the same customer with the same balance (oldest first).
unapplied_cash as (

    select
        'unapplied_cash'                                    as break_type,
        p.payment_id                                        as record_id,
        p.customer_id,
        i.invoice_id,
        p.payment_id,
        p.amount_usd,
        case
            when i.invoice_id is not null
                then 'Payment of $' || p.amount_usd || ' has no invoice reference. Matches open invoice '
                     || i.invoice_id || ' (same customer and amount).'
            else 'Payment of $' || p.amount_usd || ' has no invoice reference and no matching open invoice.'
        end                                                 as details,
        case
            when i.invoice_id is not null then 'Apply the payment to ' || i.invoice_id || '.'
            else 'Research with the customer before applying.'
        end                                                 as suggested_action,
        'Unapplied Cash'                                    as debit_account,
        'Accounts Receivable'                               as credit_account
    from payments as p
    left join invoices as i
        on  p.customer_id = i.customer_id
        and p.amount_usd  = i.balance_due_usd
    where p.invoice_id is null
    qualify row_number() over (partition by p.payment_id order by i.invoice_date) = 1

),

-- 2. Duplicate payment: same invoice, amount, and date recorded more than once.
--    The first one (lowest payment ID) is treated as the real payment.
duplicate_payments as (

    select
        'duplicate_payment'                                 as break_type,
        payment_id                                          as record_id,
        customer_id,
        invoice_id,
        payment_id,
        amount_usd,
        'Same invoice, amount, and date as ' || first_payment_id || '.'   as details,
        'Refund the customer, or hold the amount as a credit.'            as suggested_action,
        'Accounts Receivable'                               as debit_account,
        'Cash (if refunded)'                                as credit_account
    from (
        select
            *,
            row_number()     over (partition by invoice_id, amount_usd, payment_date order by payment_id) as copy_number,
            first_value(payment_id) over (partition by invoice_id, amount_usd, payment_date order by payment_id) as first_payment_id
        from payments
        where invoice_id is not null
    )
    where copy_number > 1

),

-- 3. Short payments: invoices paid less than billed. Split by likely cause.
short_payments as (

    select
        case
            when i.balance_due_usd = 25.00 and p.payment_method = 'wire' then 'short_payment_wire_fee'
            else 'short_payment_unexplained'
        end                                                 as break_type,
        p.payment_id                                        as record_id,
        i.customer_id,
        i.invoice_id,
        p.payment_id,
        i.balance_due_usd                                   as amount_usd,
        'Paid $' || i.amount_paid_usd || ' of $' || i.total_usd || ' (' || p.payment_method || ').'  as details,
        case
            when i.balance_due_usd = 25.00 and p.payment_method = 'wire'
                then 'Exactly $25.00 short on a wire: likely a bank fee. Write it off.'
            else 'Contact the customer to collect the difference.'
        end                                                 as suggested_action,
        case
            when i.balance_due_usd = 25.00 and p.payment_method = 'wire' then 'Bank Fee Expense'
            else null
        end                                                 as debit_account,
        case
            when i.balance_due_usd = 25.00 and p.payment_method = 'wire' then 'Accounts Receivable'
            else null
        end                                                 as credit_account
    from invoices as i
    inner join payments as p
        on i.invoice_id = p.invoice_id
    where i.payment_status = 'partially_paid'

),

-- 4. Missing invoice: usage in a month with no invoice at all (unbilled revenue).
missing_invoices as (

    select
        'unbilled_usage_missing_invoice'                    as break_type,
        e.subscription_id || ' ' || strftime(e.period_start, '%B %Y')   as record_id,
        e.customer_id,
        cast(null as varchar)                               as invoice_id,
        cast(null as varchar)                               as payment_id,
        {{ cents_to_dollars('e.expected_total_cents') }}   as amount_usd,
        'No invoice for ' || e.subscription_id || ' for ' || strftime(e.period_start, '%B %Y')
            || ', but ' || format('{:,}', e.usage_tokens) || ' tokens were used.'  as details,
        'Create and send the missing invoice.'              as suggested_action,
        'Accounts Receivable'                               as debit_account,
        'Revenue'                                           as credit_account
    from expected_invoices as e
    left join {{ ref('stg_invoices') }} as i
        on  e.subscription_id = i.subscription_id
        and e.period_start    = i.period_start
    where i.invoice_id is null

),

-- 5. Understated usage: the invoice shows less usage than the usage events.
understated_usage as (

    select
        'unbilled_usage_understated'                        as break_type,
        i.invoice_id                                        as record_id,
        i.customer_id,
        i.invoice_id,
        cast(null as varchar)                               as payment_id,
        {{ cents_to_dollars('e.expected_total_cents - i.total_cents') }}  as amount_usd,
        'Invoice shows ' || format('{:,}', i.usage_tokens) || ' tokens, but usage events show '
            || format('{:,}', e.usage_tokens) || '.'      as details,
        'Bill the difference.'                              as suggested_action,
        'Accounts Receivable'                               as debit_account,
        'Revenue'                                           as credit_account
    from {{ ref('stg_invoices') }} as i
    inner join expected_invoices as e
        on  i.subscription_id = e.subscription_id
        and i.period_start    = e.period_start
    where i.usage_tokens <> e.usage_tokens

),

-- 6. Invoice math error: the total doesn't equal fee + overage.
invoice_math_errors as (

    select
        'invoice_math_error'                                as break_type,
        invoice_id                                          as record_id,
        customer_id,
        invoice_id,
        cast(null as varchar)                               as payment_id,
        {{ cents_to_dollars('subscription_fee_cents + overage_cents - total_cents') }}  as amount_usd,
        'Total is $' || total_usd || ', but fee + overage is $'
            || (subscription_fee_usd + overage_usd) || '.'  as details,
        'Correct the invoice and bill the difference.'      as suggested_action,
        'Accounts Receivable'                               as debit_account,
        'Revenue'                                           as credit_account
    from {{ ref('stg_invoices') }}
    where total_cents <> subscription_fee_cents + overage_cents

),

-- 7. Cutoff error: a payment dated before its invoice existed (posted to the wrong month).
cutoff_errors as (

    select
        'cutoff_error'                                      as break_type,
        p.payment_id                                        as record_id,
        p.customer_id,
        p.invoice_id,
        p.payment_id,
        p.amount_usd,
        'Payment dated ' || p.payment_date || ', before its invoice date of ' || i.invoice_date || '.'  as details,
        'Check the received date against the bank statement and correct the posting date.'  as suggested_action,
        'Cash (correct month)'                              as debit_account,
        'Cash (month it was posted to)'                     as credit_account
    from payments as p
    inner join invoices as i
        on p.invoice_id = i.invoice_id
    where p.payment_date < i.invoice_date

),

-- 8. Aged 90+ days: still unpaid after 90 days. Not a data error, but it needs a decision.
--    Left out: invoices matched by unapplied cash (they have actually been paid), and
--    short-paid invoices (already listed above), so each problem is counted once.
aged_90_plus as (

    select
        'aged_90_plus'                                      as break_type,
        i.invoice_id                                        as record_id,
        i.customer_id,
        i.invoice_id,
        cast(null as varchar)                               as payment_id,
        i.balance_due_usd                                   as amount_usd,
        i.days_past_due || ' days past due.'                as details,
        'Collections follow-up, or review for write-off.'   as suggested_action,
        'Bad Debt Expense (if written off)'                 as debit_account,
        'Accounts Receivable'                               as credit_account
    from invoices as i
    where i.aging_bucket = '90+'
      and i.invoice_id not in (select invoice_id from unapplied_cash where invoice_id is not null)
      and i.invoice_id not in (select invoice_id from short_payments)

),

all_breaks as (

    select * from unapplied_cash
    union all select * from duplicate_payments
    union all select * from short_payments
    union all select * from missing_invoices
    union all select * from understated_usage
    union all select * from invoice_math_errors
    union all select * from cutoff_errors
    union all select * from aged_90_plus

)

select
    break_type,
    record_id,
    customer_id,
    invoice_id,
    payment_id,
    amount_usd,
    details,
    suggested_action,
    debit_account,
    credit_account
from all_breaks
order by break_type, record_id
