select
    s.stock_key,
    to_char(p.trade_date, 'YYYYMMDD')::int as date_key,
    p.ticker,
    p.trade_date,
    p.open_price, p.high_price, p.low_price, p.close_price, p.adj_close_price,
    p.volume, p.dividends, p.stock_splits,
    p.close_price / nullif(
        lag(p.close_price) over (partition by p.ticker order by p.trade_date), 0
    ) - 1 as daily_return
from {{ ref('stg_daily_prices') }} p
join {{ ref('dim_stock') }} s using (ticker)