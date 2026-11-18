with base as (
    select
        stock_key, date_key, ticker, trade_date,
        close_price, daily_return,
        row_number() over (partition by ticker order by trade_date) as day_num
    from {{ ref('fact_daily_prices') }}
)

select
    stock_key, date_key, ticker, trade_date, close_price, daily_return,

    -- show the average only once a full 20 / 50 day window exists
    case when day_num >= 20 then
        avg(close_price) over (partition by ticker order by trade_date
                               rows between 19 preceding and current row)
    end as sma_20,

    case when day_num >= 50 then
        avg(close_price) over (partition by ticker order by trade_date
                               rows between 49 preceding and current row)
    end as sma_50,

    case when day_num >= 20 then
        stddev_samp(daily_return) over (partition by ticker order by trade_date
                                        rows between 19 preceding and current row)
    end as volatility_20d
from base