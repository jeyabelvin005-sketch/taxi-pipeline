select
    weather_date,
    temp_max_c,
    temp_min_c,
    precipitation_mm,
    snowfall_cm,
    wind_speed_max_kmh
from {{ ref('stg_weather') }}