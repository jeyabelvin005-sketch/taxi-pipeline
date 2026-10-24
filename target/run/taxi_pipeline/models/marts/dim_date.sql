
  
    

  create  table "taxi"."analytics_marts"."dim_date__dbt_tmp"
  
  
    as
  
  (
    with bounds as (
    select
        min(pickup_at)::date as min_date,
        max(pickup_at)::date as max_date
    from "taxi"."analytics_staging"."stg_yellow_trips"
),

spine as (
    select generate_series(min_date, max_date, interval '1 day')::date as date_day
    from bounds
)

select
    date_day,
    extract(year  from date_day)::int  as year,
    extract(month from date_day)::int  as month,
    extract(day   from date_day)::int  as day,
    extract(dow   from date_day)::int  as day_of_week,
    to_char(date_day, 'Day')           as day_name,
    to_char(date_day, 'YYYY-MM')       as year_month,
    case when extract(dow from date_day) in (0, 6) then true else false end as is_weekend
from spine
  );
  