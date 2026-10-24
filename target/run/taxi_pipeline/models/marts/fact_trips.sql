
  
    

  create  table "taxi"."analytics_marts"."fact_trips__dbt_tmp"
  
  
    as
  
  (
    with trips as (
    select * from "taxi"."analytics_staging"."stg_yellow_trips"
),

zones as (
    select location_id, borough, zone, service_zone from "taxi"."analytics_marts"."dim_zones"
),

weather as (
    select * from "taxi"."analytics_marts"."dim_weather"
)

select
    t.pickup_at,
    t.dropoff_at,
    t.pickup_at::date                               as pickup_date,
    t.vendor_id,
    t.pickup_location_id,
    t.dropoff_location_id,
    pz.borough                                      as pickup_borough,
    pz.zone                                         as pickup_zone,
    dz.borough                                      as dropoff_borough,
    dz.zone                                         as dropoff_zone,
    t.passenger_count,
    t.trip_distance,
    t.rate_code_id,
    t.payment_type,
    t.fare_amount,
    t.extra,
    t.mta_tax,
    t.tip_amount,
    t.tolls_amount,
    t.improvement_surcharge,
    t.total_amount,
    t.congestion_surcharge,
    t.airport_fee,
    w.temp_max_c,
    w.temp_min_c,
    w.precipitation_mm,
    w.snowfall_cm,
    w.wind_speed_max_kmh,
    case when w.precipitation_mm > 0 then true else false end as is_rainy,
    case when w.snowfall_cm > 0 then true else false end as is_snowy,
    t.source_month
from trips t
left join zones pz on t.pickup_location_id  = pz.location_id
left join zones dz on t.dropoff_location_id = dz.location_id
left join weather w on t.pickup_at::date = w.weather_date
  );
  