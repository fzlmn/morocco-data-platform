{{ config(materialized='view') }}

-- Cleaning only: rename, cast, trim. No business logic, no joins.

with source as (

    select * from {{ source('raw', 'worldbank_indicators') }}

),

cleaned as (

    select
        upper(trim(country_code))      as country_code,
        trim(country_name)             as country_name,
        upper(trim(indicator_code))    as indicator_code,
        trim(indicator_name)           as indicator_name,
        year::int                      as year,
        value::numeric                 as value,
        nullif(trim(coalesce(unit, '')), '')       as unit,
        nullif(trim(coalesce(obs_status, '')), '') as obs_status,
        source_last_updated,
        loaded_at
    from source
    where country_code is not null
      and indicator_code is not null
      and year is not null

)

select * from cleaned
