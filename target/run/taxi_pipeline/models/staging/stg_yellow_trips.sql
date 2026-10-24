
  create view "taxi"."analytics_staging"."stg_yellow_trips__dbt_tmp"
    
    
  as (
    with source as (
    select * from "taxi"."raw"."yellow_trips"
),

renamed as (
    select
        vendorid                        as vendor_id,
        tpep_pickup_datetime            as pickup_at,
        tpep_dropoff_datetime           as dropoff_at,
        passenger_count,
        trip_distance,
        ratecodeid                      as rate_code_id,
        store_and_fwd_flag,
        pulocationid                    as pickup_location_id,
        dolocationid                    as dropoff_location_id,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        airport_fee,
        source_month
    from source
    where tpep_pickup_datetime >= (source_month || '-01')::date
      and tpep_pickup_datetime <  ((source_month || '-01')::date + interval '1 month')
)

select * from renamed
  );