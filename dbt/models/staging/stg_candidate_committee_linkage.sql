select *
from {{ source('s3_datarecce_todofec', 'raw_candidate_committee_linkage') }}
