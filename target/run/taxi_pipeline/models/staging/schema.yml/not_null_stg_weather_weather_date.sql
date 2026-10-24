
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select weather_date
from "taxi"."analytics_staging"."stg_weather"
where weather_date is null



  
  
      
    ) dbt_internal_test