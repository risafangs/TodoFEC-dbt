# TodoFEC-dbt

This project aligns with the [**TodoFEC**](https://github.com/DataRecce/TodoFEC) initiative to create a standardized set of data tasks for comparing data processing frameworks. Our focus is on developing dbt models that transform and analyze the U.S. Election Campaign Finance dataset to provide insights into campaign contributions, expenditure patterns, and donor networks.

## Quickstart

- Explore data by Query FEC Data on S3 with DuckDB
- Once you decide what changes you want to make, you can download the dataset and make dbt model changes.

### Query FEC Data on S3 with DuckDB

The [FEC data](https://www.fec.gov/data/browse-data/?tab=bulk-data) for this project is available as Parquet files in an [**S3 bucket**](https://us-east-1.console.aws.amazon.com/s3/buckets/datarecce-todofec?bucketType=general&region=us-east-1&tab=objects#), allowing direct querying without downloading. You can use DuckDB to query the data directly.

1. Install duckdb

``` bash
   pip install duckdb
```

2. Open duckdb

``` bash
   duckdb
```

3. Run a Query: Use the following command to query the Parquet file directly from S3

``` bash
  select count(*) from read_parquet('s3://datarecce-todofec/pac_summary_2024.parquet');
```

Here are the S3 URIs of available dataset:

```
s3://datarecce-todofec/all_candidates_2024.parquet
s3://datarecce-todofec/pac_summary_2024.parquet
s3://datarecce-todofec/house_senate_2024.parquet
s3://datarecce-todofec/committee_master_2024.parquet
s3://datarecce-todofec/operating_expenditures_2024.parquet
s3://datarecce-todofec/transactions_between_committees_2024.parquet
s3://datarecce-todofec/contributions_from_committees_to_candidates_2024.parquet
s3://datarecce-todofec/candidate_master_2024.parquet
s3://datarecce-todofec/candidate_committee_linkage_2024.parquet
```

### Get Ready to Make dbt Model Changes

#### Fork This Repository

To make and track your changes, first fork this repository to your own GitHub account. This will create a personal copy that you can modify.

1. Fork the Repository: Click "Fork" at the top of this GitHub page.
2. Clone Your Fork:

``` bash
  git clone https://github.com/your-username/TodoFEC-dbt.git
  cd TodoFEC
```

#### System Prequisites

Before you begin you'll need the following on your system:

- Python >=3.12 (see [here](https://www.python.org/downloads/))
- Python Poetry >= 1.8 (see [here](https://pypi.org/project/poetry/))
- git (see [here](https://github.com/git-guides/install-git))

#### Setup dependencies

Install the python dependencies

``` bash
poetry install
```

#### Using the poetry environment

Once installation has completed you can enter the poetry environment.

```bash
poetry shell
```

Check out more form types [here](https://www.fec.gov/data/browse-data/?tab=bulk-data)

### Running dbt

Once you've updated any models you can run dbt _within the poetry environment_ by simply calling:

```bash
dbt run
```
