# DE Zoomcamp

[NY Taxi Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

## Benchmarking

Data Parquet with 3.5M rows of Yellow Taxi Data

Python with DuckDb(C++ lib) == Rust with DuckDb = `30 seconds` (But rust have huge compilation time)

Python with Polars(Rust lib) = `36 seconds`

Python with Pandas(Python lib) => Garbage => `4.3 minutes` for 1 batch.
So approximately `150 minutes` for 35 batches
