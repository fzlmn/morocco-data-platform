{{ config(materialized='table') }}

-- The analytical table the dashboard reads.
-- Grain: one row per country and year, indicators pivoted into columns.

with observations as (

    select * from {{ ref('stg_worldbank_indicators') }}

),

pivoted as (

    select
        country_code,
        country_name,
        year,

        max(value) filter (where indicator_code = 'FP.CPI.TOTL.ZG')
            as inflation_pct,
        max(value) filter (where indicator_code = 'NY.GDP.MKTP.KD.ZG')
            as gdp_growth_pct,
        max(value) filter (where indicator_code = 'NY.GDP.PCAP.CD')
            as gdp_per_capita_usd,
        max(value) filter (where indicator_code = 'SL.UEM.TOTL.ZS')
            as unemployment_pct,
        max(value) filter (where indicator_code = 'PA.NUS.FCRF')
            as mad_per_usd

    from observations
    group by country_code, country_name, year

),

derived as (

    select
        *,

        -- How much the dirham moved against the dollar, year on year.
        -- Positive = the dirham weakened (more MAD needed per USD).
        round(
            100.0 * (mad_per_usd - lag(mad_per_usd) over w)
                  / nullif(lag(mad_per_usd) over w, 0)
        , 2) as mad_depreciation_pct,

        -- Inflation smoothed over three years, to separate shocks from trend.
        round(
            avg(inflation_pct) over (
                partition by country_code
                order by year
                rows between 2 preceding and current row
            )
        , 2) as inflation_3y_avg,

        (year / 10) * 10 as decade

    from pivoted
    window w as (partition by country_code order by year)

)

select * from derived
