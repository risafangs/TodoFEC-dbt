# US Campaign Finance

In the front-end world, **TodoMVC** is a well-known example for comparing JavaScript frameworks by implementing the same to-do app in multiple frameworks. This project seeks to bring a similar concept to data processing and analytics.

We aim to create a standardized set of tasks using the **US Election Campaign Finance Dataset**, enabling users to compare different tools and frameworks for data processing and analysis.

If you're interested in contributing, check out the detailed narrative and sign-up section in the [project narrative document](https://docs.google.com/document/d/1K44XHV_NpfUe2R2PVBJNRkT-arZtKp4_SCzer8Nmg-Q/edit?tab=t.0).

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

### Download the dataset

You can download the dataset, which will be saved in `parquet_files`.

``` bash
python script/parse.py
```

### Ingest data to DuckDB

Once the dataset is ready you can ingest them to `us_campaign_finance.duckdb`.

``` bash
python script/ingest.py
```

### Running dbt

Once you've updated any models you can run dbt _within the poetry environment_ by simply calling:

```bash
dbt run
```
