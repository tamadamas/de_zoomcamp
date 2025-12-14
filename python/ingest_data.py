import time
import tracemalloc
from os import getenv

import duckdb
import polars as pl
import pyarrow.parquet as pq
from polars import LazyFrame
from sqlalchemy import create_engine


def trace_func(func):
    def wrapper(*args, **kwargs):
        print(f"--- Starting {func.__name__} ---")
        tracemalloc.start()
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise
        finally:
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()

            print(f"DONE: {func.__name__}")
            print(f"Execution Time: {end_time - start_time:.2f} seconds")
            print(f"Used Memory:    {max(current, peak) / 1024 / 1024:.2f} MB")
            print("-" * 30)

            tracemalloc.stop()

        return result

    return wrapper


def main() -> None:
    database_url = getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    data_file = getenv("DATA_FILE")
    if not data_file:
        raise ValueError("DATA_FILE environment variable is not set")

    zones_data_file = getenv("ZONES_DATA_FILE")
    if not zones_data_file:
        raise ValueError("ZONES_DATA_FILE environment variable is not set")

    ingest_data_polars(
        database_url=database_url,
        table_name="yellow_tripdata",
        data_file=data_file,
    )

    ingest_data_duckdb(
        database_url=database_url,
        table_name="zones",
        data_file=zones_data_file,
    )

    # Use for benchmarking
    # ingest_data_duckdb(
    #     database_url=database_url,
    #     table_name="yt_duckdb",
    #     data_file=data_file,
    # )

    # Use for benchmarking
    # ingest_data_pandas(
    #     database_url=database_url,
    #     table_name="yt_pandas",
    #     data_file=data_file,
    # )


@trace_func
def ingest_data_polars(database_url: str, table_name: str, data_file: str) -> None:
    print(f"Scanning parquet {data_file}")

    lf: LazyFrame = pl.scan_parquet(data_file)

    total_rows = lf.select(pl.len()).collect(engine="streaming").item()
    print(f"Total rows to process: {total_rows}")

    current_row = 0
    batch_size = 100_000
    mode: str = "replace"

    for df in lf.collect_batches(chunk_size=batch_size):
        print(f"Processing batch {current_row}/{total_rows}")

        df.write_database(
            table_name=table_name,
            connection=database_url,
            if_table_exists=mode,
            engine="adbc",
        )

        mode = "append"
        current_row += batch_size


@trace_func
def ingest_data_pandas(database_url: str, table_name: str, data_file: str) -> None:
    print(f"Scanning parquet {data_file}")

    engine = create_engine(database_url)
    parquet_file = pq.ParquetFile(data_file)

    total_rows = parquet_file.metadata.num_rows
    print(f"Total rows to process: {total_rows}")

    current_row = 0
    batch_size = 100_000
    mode: str = "replace"

    for i, batch in enumerate(parquet_file.iter_batches(batch_size=batch_size)):
        print(f"Processing batch {i}: {current_row}/{total_rows}")

        df = batch.to_pandas()
        df.to_sql(
            name=table_name, con=engine, if_exists=mode, index=False, method="multi"
        )

        mode = "append"
        current_row += batch_size


@trace_func
def ingest_data_duckdb(database_url: str, table_name: str, data_file: str) -> None:
    print(f"Scanning {data_file}")

    con = duckdb.connect()

    con.execute(f"ATTACH '{database_url}' AS pg (TYPE POSTGRES, SCHEMA 'public')")
    con.execute(f"DROP TABLE IF EXISTS pg.{table_name}")

    print(f"DuckDB: IMPORTING {data_file} to pg.{table_name}...")
    con.execute(f"CREATE TABLE pg.{table_name} AS SELECT * FROM '{data_file}'")


if __name__ == "__main__":
    main()
