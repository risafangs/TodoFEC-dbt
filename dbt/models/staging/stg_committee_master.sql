select * from {{ source('s3_datarecce_todofec', 'raw_committee_master') }}
