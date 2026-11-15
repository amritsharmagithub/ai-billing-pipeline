-- Report: did the reconciliation find every planted error?
-- Compares the breaks found by the rules with the answer key (raw.planted_errors).
-- One row per planted error type, plus any breaks that don't match a planted error.

with breaks as (

    -- Aged 90+ invoices are a normal business situation, not planted errors, so they are left out.
    select break_type, record_id
    from {{ ref('rpt_reconciliation_breaks') }}
    where break_type <> 'aged_90_plus'

),

answer_key as (

    select
        error_type,
        -- Missing invoices don't exist in the data, so the answer key's invoice ID can't be found.
        -- Match them on subscription and month instead, taken from the answer key's details.
        case
            when error_type = 'unbilled_usage_missing_invoice'
                then regexp_extract(details, 'for (S\d+) for ([A-Za-z]+ \d{4})', 1)
                     || ' ' || regexp_extract(details, 'for (S\d+) for ([A-Za-z]+ \d{4})', 2)
            else record_id
        end as record_id
    from {{ source('raw', 'planted_errors') }}

),

compared as (

    select
        coalesce(a.error_type, b.break_type)   as error_type,
        a.record_id is not null                as was_planted,
        b.record_id is not null                as was_found
    from answer_key as a
    full outer join breaks as b
        on  a.error_type = b.break_type
        and a.record_id  = b.record_id

)

select
    error_type,
    count(*) filter (where was_planted)                        as planted,
    count(*) filter (where was_planted and was_found)          as found,
    count(*) filter (where was_planted and not was_found)      as missed,
    count(*) filter (where was_found and not was_planted)      as extra_breaks
from compared
group by error_type
order by error_type
