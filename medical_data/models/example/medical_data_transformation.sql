{{config(materialized='table')}}

with filter_data as (
    SELECT *
    FROM {{source('public','medical_data_load')}}
    where "Media Path" != 'No media'
)

SELECT * 
FROM filter_data