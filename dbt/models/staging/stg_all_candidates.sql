select * from {{ source('s3_datarecce_todofec', 'raw_all_candidates') }}
