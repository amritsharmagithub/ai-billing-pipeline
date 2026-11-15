-- Staging: usage events. One row per subscription per day.
-- Light cleanup only: clear names. No business logic, no fixing data.

with source as (

    select * from {{ source('raw', 'usage_events') }}

),

renamed as (

    select
        usage_id,
        customer_id,
        subscription_id,
        usage_date,
        model          as model_name,
        tokens_used
    from source

)

select * from renamed
