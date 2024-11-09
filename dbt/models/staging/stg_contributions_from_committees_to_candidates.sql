select *
from
    {{ source('s3_datarecce_todofec', 'raw_contributions_from_committees_to_candidates') }}
