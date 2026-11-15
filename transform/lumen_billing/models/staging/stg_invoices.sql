-- Staging: invoices. One row per monthly invoice.
-- Light cleanup only: clear names, plus dollar columns. No business logic, no fixing data:
-- planted errors (for example, wrong totals) stay visible for the tests and the reconciliation.

with source as (

    select * from {{ source('raw', 'invoices') }}

),

renamed as (

    select
        invoice_id,
        customer_id,
        subscription_id,
        period_start,
        period_end,
        invoice_date,
        due_date,
        usage_tokens,
        included_tokens,
        overage_tokens,
        subscription_fee_cents,
        overage_cents,
        total_cents,
        {{ cents_to_dollars('subscription_fee_cents') }}   as subscription_fee_usd,
        {{ cents_to_dollars('overage_cents') }}            as overage_usd,
        {{ cents_to_dollars('total_cents') }}              as total_usd
    from source

)

select * from renamed
