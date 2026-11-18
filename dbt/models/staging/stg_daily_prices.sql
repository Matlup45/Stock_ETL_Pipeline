select
    ticker,
    trade_date,
    open       as open_price,
    high       as high_price,
    low        as low_price,
    close      as close_price,
    adj_close  as adj_close_price,
    volume,
    dividends,
    stock_splits
from {{ source('raw', 'daily_prices') }}
where close is not null