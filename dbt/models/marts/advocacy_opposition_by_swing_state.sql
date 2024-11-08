select
	cpc.CAND_NAME,
	cpc.TRANSACTION_TP,
	cpc.STATE,
	count(distinct cpc.CMTE_ID) as CMTE_COUNT,
	count(*) as TRANSACTION_COUNT,
	sum(cpc.TRANSACTION_AMT) as TOTAL_AMT
from {{ ref('int_contributions_to_presidential_candidates') }} cpc
join {{ ref('swing_states') }} ss
on cpc.STATE = ss.abbreviation
where TRANSACTION_TP in ('24A', '24E')
group by cpc.CAND_NAME, cpc.TRANSACTION_TP, cpc.STATE
