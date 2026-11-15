-- Control: the reconciliation must find every planted error, with no extra breaks.
-- The test fails if any row is returned.

select *
from {{ ref('rpt_reconciliation_vs_answer_key') }}
where missed > 0
   or extra_breaks > 0
