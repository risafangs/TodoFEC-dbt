select * from {{ source('s3_datarecce_todofec', 'raw_operating_expenditures') }}
