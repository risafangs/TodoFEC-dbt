select * from {{ source('parquet', 'raw_all_candidates') }}
