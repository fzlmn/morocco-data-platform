{{ config(materialized='table') }}

-- The long fact table.
-- Grain: one row per country, indicator and year.

with observations as (

    select * from {{ ref('stg_worldbank_indicators') }}

)

select
    {{ dbt_utils.generate_surrogate_key(
        ['country_code', 'indicator_code', 'year']) }} as observation_key,

    country_code,
    country_name,
    indicator_code,
    year,
    value,

    -- Year-on-year change within each series.
    value - lag(value) over (
        partition by country_code, indicator_code
        order by year
    ) as change_from_prior_year,

    value is null as is_missing,

    source_last_updated,
    loaded_at

from observations
