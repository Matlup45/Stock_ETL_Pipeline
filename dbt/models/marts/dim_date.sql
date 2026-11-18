with days as (
    select d::date as date_day
    from generate_series('2015-01-01'::date, '2035-12-31'::date, interval '1 day') d
)
select
    to_char(date_day, 'YYYYMMDD')::int       as date_key,
    date_day,
    extract(year from date_day)::int         as year,
    extract(quarter from date_day)::int      as quarter,
    extract(month from date_day)::int        as month,
    trim(to_char(date_day, 'Month'))         as month_name,
    extract(isodow from date_day)::int       as day_of_week,
    extract(isodow from date_day) in (6, 7)  as is_weekend
from days