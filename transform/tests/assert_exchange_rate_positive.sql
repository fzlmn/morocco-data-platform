-- Singular test: a zero or negative exchange rate is impossible and would
-- break the depreciation calculation, which divides by the prior year.

select
    country_code,
    year,
    mad_per_usd
from {{ ref('mart_macro_annual') }}
where mad_per_usd is not null
  and mad_per_usd <= 0
