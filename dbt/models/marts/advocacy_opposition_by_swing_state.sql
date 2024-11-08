select ao.*
from {{ ref('advocacy_opposition_by_state_candidate') }} ao
join {{ ref('swing_states') }} ss
    on ao.state = ss.abbreviation
