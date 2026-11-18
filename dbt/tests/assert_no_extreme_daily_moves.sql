-- Flags single-day moves above 40%: usually a split problem or bad data
select ticker, trade_date, close_price, daily_return
from {{ ref('fact_daily_prices') }}
where abs(daily_return) > 0.40