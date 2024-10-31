# Standardized Data Project Using US Election Campaign Finance Dataset

In the front-end world, **TodoMVC** is a well-known example for comparing JavaScript frameworks by implementing the same to-do app in multiple frameworks. This project seeks to bring a similar concept to data processing and analytics.

We aim to create a standardized set of tasks using the **US Election Campaign Finance Dataset**, enabling users to compare different tools and frameworks for data processing and analysis.

If you're interested in contributing, check out the detailed narrative and sign-up section in the [project narrative document](https://docs.google.com/document/d/1K44XHV_NpfUe2R2PVBJNRkT-arZtKp4_SCzer8Nmg-Q/edit?tab=t.0).

## Why the US Election Campaign Finance Dataset?

1. **Rich Data**: The dataset includes numbers, categories, dates, and text, ideal for testing different data frameworks.
2. **Public and Relevant**: A public dataset with significant real-world importance for understanding money in politics.
3. **Scalable**: Large enough to test performance and scalability.
4. **Complex Tasks**: Suitable for advanced tasks like network analysis, forecasting, and natural language processing.

## Project Objectives

### Proposed Data Tasks

- Load the .fec dataset and make it accessible.
- Basic dimension modeling.
- Basic aggregated results.
- Add a semantic model.
- Visualize results.
- Implement CI/CD.

### Proposed Analytics Tasks

- Identify PACs, their funders, and expenditures in swing states for both sides.
- Analyze campaign expenditures by candidate and locale.
- Track top industries donating to candidates by party.
- Explore amounts raised, expenditures by date, and behavioral patterns of funders.

## Resources & References

- [FEC Data Browse](https://www.fec.gov/data/browse-data/?tab=bulk-data)
- [Mining FEC Data PDF](https://s3.amazonaws.com/ire16/campaign-finance/MiningFECData.pdf)
- [FEC Parser to Arrow & Parquet](https://github.com/NickCrews/feco3)
- [Sample Analytics Project](https://medium.com/@harshithayentra.1997/federal-election-commission-fec-prediction-analysis-27cde08f1531)

## Quickstart

### System Prequisites

Before you begin you'll need the following on your system:

- Python >=3.12 (see [here](https://www.python.org/downloads/))
- Python Poetry >= 1.8 (see [here](https://pypi.org/project/poetry/))
- git (see [here](https://github.com/git-guides/install-git))

### Setup dependencies

Install the python dependencies

``` bash
poetry install
```

### Using the poetry environment

Once installation has completed you can enter the poetry environment.

```bash
poetry shell
```

### Download datasets

You can download the dataset, which will be saved in `datarecce-todofec`.

``` bash
python script/sync_raw_data.py
```

### Running dbt

Once you've updated any models you can run dbt _within the poetry environment_ by simply calling:

```bash
dbt run
```

## How to Contribute

We’d love your help! Here’s how to get started:

1. **Fork the repo** to your GitHub account.
2. **Make your changes** in a new branch.
3. **Open a PR** when you're ready for review.
4. **Share your progress** or ask questions in dbt Slack `#tools-recce`.
