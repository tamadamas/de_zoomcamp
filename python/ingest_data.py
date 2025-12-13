import time
from os import getenv

import polars as pl
from polars import LazyFrame


def main() -> None:
    database_url = getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    lf: LazyFrame = pl.scan_parquet("../data/yellow_tripdata_2025-01.parquet")
    print(lf.head())

    count = lf.select(pl.len()).collect(engine="streaming").item()
    current_count = 0
    batch_size = 100_000

    # Replace table for the first time and then append
    mode: str = "replace"

    for df in lf.collect_batches(chunk_size=batch_size):
        print(f"Processing batch {current_count}/{count}")

        df.write_database(
            table_name="yellow_tripdata",
            connection=database_url,
            if_table_exists=mode,
            engine="adbc",
        )

        mode = "append"
        current_count += batch_size


if __name__ == "__main__":
    t1 = time.time()

    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        t2 = time.time()
        print(f"Completed: Execution time: {t2 - t1:.2f} seconds")
