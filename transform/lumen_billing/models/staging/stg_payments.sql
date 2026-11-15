-- Staging: payments. One row per payment received.
-- Light cleanup only: clear names, plus a dollar column. No business logic, no fixing data:
-- payments with no invoice reference (unapplied cash) keep a NULL invoice_id.

with source as (

    select * from {{ source('raw', 'payments') }}

),

renamed as (

    select
        payment_id,
        invoice_id,                                         -- NULL means unapplied cash
        customer_id,
        payment_date,
        amount_cents,
        {{ cents_to_dollars('amount_cents') }}              as amount_usd,
        payment_method
    from source

)

select * from renamed
