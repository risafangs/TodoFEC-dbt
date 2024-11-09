with presidential_candidates as (
    select ac.*
    from {{ ref('presidential_candidates') }} pc
    left join {{ ref('stg_all_candidates') }} ac
        on pc.name = ac.cand_name
)


select
    pc.cand_id,
    pc.cand_name,
    pc.cand_pty_affiliation,
    cm.cmte_id,
    cm.cmte_nm,
    cm.cmte_pty_affiliation,
    cc.tran_id,
    cc.transaction_tp,
    cc.state,
    cc.transaction_amt
from presidential_candidates pc
left join {{ ref('stg_contributions_from_committees_to_candidates') }} cc
    on pc.cand_id = cc.cand_id
left join {{ ref('stg_committee_master') }} cm
    on cc.cmte_id = cm.cmte_id
