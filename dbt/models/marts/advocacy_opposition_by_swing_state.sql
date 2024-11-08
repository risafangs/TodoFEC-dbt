select
    cpc.cand_name,
    cpc.transaction_tp,
    cpc.state,
    count(distinct cpc.cmte_id) as cmte_count,
    count(*) as transaction_count,
    sum(cpc.transaction_amt) as total_amt
from {{ ref('int_contributions_to_presidential_candidates') }} cpc
join {{ ref('swing_states') }} ss
    on cpc.state = ss.abbreviation
where transaction_tp in ('24A', '24E')
group by cpc.cand_name, cpc.transaction_tp, cpc.state
