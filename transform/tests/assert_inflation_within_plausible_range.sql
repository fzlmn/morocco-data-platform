-- Singular test: inflation outside -15%..60% would mean the unit is wrong.
-- The indicator is an annual percentage; an index level would arrive in the
-- hundreds and load without complaint. This catches that silently.

select
    country_code,
    year,
    inflation_pct
from {{ ref('mart_macro_annual') }}
where inflation_pct is not null
  and (inflation_pct < -15 or inflation_pct > 60)
