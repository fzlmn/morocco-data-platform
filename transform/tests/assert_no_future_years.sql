-- Singular test: an observation dated beyond the current year means either
-- a parsing bug or a source change.

select
    country_code,
    indicator_code,
    year
from {{ ref('fct_indicator_observation') }}
where year > extract(year from current_date) + 1
