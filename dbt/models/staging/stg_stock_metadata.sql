select ticker, name as company_name, sector, exchange
from {{ source('raw', 'stock_metadata') }}