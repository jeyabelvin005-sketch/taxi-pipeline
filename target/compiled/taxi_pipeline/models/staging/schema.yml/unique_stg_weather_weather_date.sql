
    
    

select
    weather_date as unique_field,
    count(*) as n_records

from "taxi"."analytics_staging"."stg_weather"
where weather_date is not null
group by weather_date
having count(*) > 1


