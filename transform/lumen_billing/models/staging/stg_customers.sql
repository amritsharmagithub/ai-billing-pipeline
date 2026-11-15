-- Staging: customers. One row per customer company.
-- Light cleanup only: clear column names. No business logic, no fixing data.

with source as (

    select * from {{ source('raw', 'customers') }}

),

renamed as (

    select
        customer_id,
        company_name,
        country      as country_code,
        signup_date
    from source

)

select * from renamed
