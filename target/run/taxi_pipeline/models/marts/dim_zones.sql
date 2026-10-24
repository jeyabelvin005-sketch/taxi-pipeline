
  
    

  create  table "taxi"."analytics_marts"."dim_zones__dbt_tmp"
  
  
    as
  
  (
    with source as (
    select * from "taxi"."analytics"."taxi_zone_lookup"
),

renamed as (
    select
        "LocationID"    as location_id,
        "Borough"       as borough,
        "Zone"          as zone,
        "service_zone"  as service_zone
    from source
)

select * from renamed
  );
  