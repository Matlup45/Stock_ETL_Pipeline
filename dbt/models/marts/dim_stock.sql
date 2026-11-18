select
    md5(ticker) as stock_key,
    ticker,
    company_name,
    sector,
    exchange
from {{ ref('stg_stock_metadata') }}