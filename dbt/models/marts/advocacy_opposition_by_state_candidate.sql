select
    cand_name,
    transaction_tp,
    state,
    state in (select abbreviation from {{ ref('swing_states') }}
    ) as is_swing_state,
    count(distinct cmte_id) as cmte_count,
    count(*) as transaction_count,
    sum(transaction_amt) as total_amt
from {{ ref('int_contributions_to_presidential_candidates') }}
where transaction_tp in ('24A', '24E')
group by cand_name, transaction_tp, state
