with presidential_candidates as (
    select ac.*
    from {{ ref('presidential_candidates') }} pc
    left join {{ ref('stg_all_candidates') }} ac
        on pc.name = ac.cand_name
)


select
    pc.CAND_ID,
    pc.CAND_NAME,
    pc.CAND_PTY_AFFILIATION,
    cm.CMTE_ID,
    cm.CMTE_NM,
    cm.CMTE_PTY_AFFILIATION,
    cc.TRAN_ID,
    cc.TRANSACTION_TP,
    cc.STATE,
    cc.TRANSACTION_AMT
from presidential_candidates pc
left join {{ ref('stg_contributions_from_committees_to_candidates') }} cc
    on pc.cand_id = cc.cand_id
left join {{ ref('stg_committee_master') }} cm
    on cc.cmte_id = cm.cmte_id
