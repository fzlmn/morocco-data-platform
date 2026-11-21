{{ config(materialized='table') }}

-- One row per indicator. Grain: indicator_code.

with observations as (

    select * from {{ ref('stg_worldbank_indicators') }}

),

indicators as (

    select
        indicator_code,
        max(indicator_name) as indicator_name,
        min(year)           as first_year,
        max(year)           as last_year,
        count(*)            as observation_count,
        count(value)        as observed_count,
        count(*) - count(value) as missing_count
    from observations
    group by indicator_code

)

select
    indicator_code,
    indicator_name,

    -- Classify so the dashboard knows how to format each series.
    case
        when indicator_code in ('FP.CPI.TOTL.ZG', 'NY.GDP.MKTP.KD.ZG',
                                'SL.UEM.TOTL.ZS')           then 'percent'
        when indicator_code = 'NY.GDP.PCAP.CD'              then 'usd'
        when indicator_code = 'PA.NUS.FCRF'                 then 'exchange_rate'
        else 'other'
    end as unit_type,

    case
        when indicator_code = 'FP.CPI.TOTL.ZG'    then 'Prices'
        when indicator_code = 'PA.NUS.FCRF'       then 'Prices'
        when indicator_code = 'SL.UEM.TOTL.ZS'    then 'Labour'
        else 'Output'
    end as domain,

    first_year,
    last_year,
    observation_count,
    observed_count,
    missing_count,
    round(100.0 * observed_count / nullif(observation_count, 0), 1)
        as coverage_pct

from indicators
