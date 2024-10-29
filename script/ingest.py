from pathlib import Path
from typing import Union, Optional

import duckdb
import pandas as pd

from config import DUCKDB_PATH, PARQUERT_DIR, METADATA


def ingest_parquet_to_duckdb(
    parquet_file: Union[str, Path], table_name: str, schema: Optional[str] = None
) -> None:
    """
    Ingest a single Parquet file into DuckDB using DuckDB's Python API.
    If table doesn't exist, creates new table.
    If table exists, appends new data with deduplication.

    Args:
        parquet_file (Union[str, Path]): Path to the Parquet file
        table_name (str): Name of the table to create/append to in DuckDB
        schema (Optional[str]): Schema name. If None, uses default schema

    Raises:
        FileNotFoundError: If parquet_file doesn't exist
    """
    # Convert path to Path object
    parquet_file = Path(parquet_file)

    # Validate inputs
    if not parquet_file.exists():
        raise FileNotFoundError(f"File not found: {parquet_file}")

    if not parquet_file.suffix == ".parquet":
        raise ValueError(f"File must be a Parquet file: {parquet_file}")

    # Connect to DuckDB using global path
    conn = duckdb.connect(DUCKDB_PATH)

    # Disable infer
    conn.execute("SET autoinstall_known_extensions = false;")
    conn.execute("SET autoload_known_extensions = false;")
    conn.execute("SET enable_geoparquet_conversion = false;")

    try:
        # Create schema if specified
        if schema:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            full_table_name = f"{schema}.{table_name}"
        else:
            full_table_name = table_name

        # Read Parquet file into DuckDB relation
        new_data = conn.from_parquet(str(parquet_file))

        # Remove duplicates from new data
        new_data = new_data.distinct()

        # Check if table exists
        existing_tables = conn.execute(
            "SELECT table_name FROM information_schema.tables "
            f"WHERE table_name = '{table_name}'"
            + (f" AND table_schema = '{schema}'" if schema else "")
        ).fetchall()
        table_exists = len(existing_tables) > 0

        if not table_exists:
            # Create new table from the relation
            new_data.create(full_table_name)
            print(f"Created new table {full_table_name}")
            rows_added = conn.execute(
                f"SELECT COUNT(*) FROM {full_table_name}"
            ).fetchone()[0]
            print(f"Rows added: {rows_added}")

        else:
            # Get existing data as relation
            existing_data = conn.table(full_table_name)
            rows_before = conn.execute(
                f"SELECT COUNT(*) FROM {full_table_name}"
            ).fetchone()[0]

            # Convert new data to pandas for easier comparison
            new_df = new_data.to_df()
            existing_df = existing_data.to_df()

            # Find unique rows (not in existing data)
            merged_df = pd.concat([existing_df, new_df]).drop_duplicates(keep=False)
            unique_rows = merged_df.iloc[existing_df.shape[0] :]

            if not unique_rows.empty:
                # Register temporary view for the unique rows
                conn.register("unique_rows_view", unique_rows)
                # Append unique rows to existing table
                conn.execute(
                    f"INSERT INTO {full_table_name} SELECT * FROM unique_rows_view"
                )
                # Clean up temporary view
                conn.execute("DROP VIEW IF EXISTS unique_rows_view")

            rows_after = conn.execute(
                f"SELECT COUNT(*) FROM {full_table_name}"
            ).fetchone()[0]
            rows_added = rows_after - rows_before

        # Commit the transaction
        conn.commit()

    finally:
        conn.close()


for metadata in METADATA:
    year = metadata["year"]
    category = metadata["category"]
    parquet_file = f"{PARQUERT_DIR}/{category}_{year}.parquet"
    table_name = f"raw_{category}"
    ingest_parquet_to_duckdb(
        parquet_file=parquet_file, table_name=table_name, schema="raw"
    )
