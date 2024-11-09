---
title: TodoEFC
---

<ButtonGroup name=transaction_tp title="Expenditure Type:">
    <ButtonGroupItem valueLabel="Advocating" value="24E" default />
    <ButtonGroupItem valueLabel="Opposing" value="24A" />
</ButtonGroup>

<ButtonGroup name=cand_name title="Candidate:">
    <ButtonGroupItem valueLabel="Trump, Doonald J." value="TRUMP, DONALD J."
        default />
    <ButtonGroupItem valueLabel="Harris, Kamala" value="HARRIS, KAMALA" />
</ButtonGroup>

<ButtonGroup name=is_swing_state title="Area:">
    <ButtonGroupItem valueLabel="All States" value=False default />
    <ButtonGroupItem valueLabel="Swing States" value=True />
</ButtonGroup>

<ButtonGroup name=display_value display=tabs>
    <ButtonGroupItem valueLabel="Committee Count" value="cmte_count" default />
    <ButtonGroupItem valueLabel="Transaction Count" value="transaction_count" />
    <ButtonGroupItem valueLabel="Total Transaction Amount" value="total_amt" />
</ButtonGroup>

```sql filter_results
  select *
  from from_duckdb.advocacy_opposition_by_state_candidate
  where TRANSACTION_TP = '${inputs.transaction_tp}'
    and CAND_NAME = '${inputs.cand_name}'
    and is_swing_state = ${inputs.is_swing_state}
```

{#if inputs.cand_name == "TRUMP, DONALD J."}
    <USMap
        data={filter_results}
        state=STATE
        value={inputs.display_value}
        legend=true
        abbreviations=true
        colorScale=red
    />
{:else}
    <USMap
        data={filter_results}
        state=STATE
        value={inputs.display_value}
        legend=true
        abbreviations=true
        colorScale=blue
    />
{/if}

```sql against_data
  select *
  from from_duckdb.advocacy_opposition_by_state_candidate
  where TRANSACTION_TP = '${inputs.transaction_tp}'
    and is_swing_state = ${inputs.is_swing_state}
```

<BarChart
    data={against_data}
    x=STATE
    y={inputs.display_value}
    series=CAND_NAME
    type=grouped
    swapXY=true
    seriesColors={{
        'TRUMP, DONALD J.': '#ef4444',
        'HARRIS, KAMALA': '#3b82f6',
    }}
/>
