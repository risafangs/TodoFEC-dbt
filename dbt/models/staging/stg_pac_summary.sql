select * from {{ source('parquet', 'raw_pac_summary') }}
