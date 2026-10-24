with source as (
    select * from {{ source('raw', 'weather') }}
),

renamed as (
    select
        weather_date::date              as weather_date,
        temperature_2m_max              as temp_max_c,
        temperature_2m_min              as temp_min_c,
        precipitation_sum               as precipitation_mm,
        snowfall_sum                    as snowfall_cm,
        wind_speed_10m_max              as wind_speed_max_kmh
    from source
)

select * from renamed