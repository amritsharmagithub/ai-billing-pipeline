-- Staging: subscriptions. One row per customer's plan.
-- Light cleanup only: clear names, plus dollar columns. No business logic, no fixing data.

with source as (

    select * from {{ source('raw', 'subscriptions') }}

),

renamed as (

    select
        subscription_id,
        customer_id,
        plan                                                as plan_name,
        monthly_fee_cents,
        {{ cents_to_dollars('monthly_fee_cents') }}         as monthly_fee_usd,
        included_tokens,
        overage_cents_per_million,
        start_date,
        end_date                                            -- NULL means still active
    from source

)

select * from renamed
