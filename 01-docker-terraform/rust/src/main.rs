use anyhow::Result;
use duckdb::{Connection as DuckDbConnection, params as duckdb_params};
use std::env;
use std::time::Instant;

use clap::Command;

fn main() -> Result<()> {
    let matches = cli().get_matches();

    match matches.subcommand() {
        Some(("ingest", _)) => ingest_data(),
        _ => {
            unreachable!("Unknown subcommand");
        }
    }
}

fn cli() -> Command {
    Command::new("de_zoomcamp")
        .about("Rust data engineering app")
        .subcommand_required(true)
        .subcommand(Command::new("ingest").about("Ingest data from source to database"))
}

fn ingest_data() -> Result<()> {
    println!("Ingesting data...");

    let database_url =
        env::var("DATABASE_URL").expect("DATABASE_URL environment variable is not set");

    let data_file = env::var("DATA_FILE").expect("DATA_FILE environment variable is not set");
    let table_name = "yellow_tripdata_rust";

    let start = Instant::now();
    let con = DuckDbConnection::open_in_memory()?;

    con.execute_batch(&format!("ATTACH '{}' AS pg (TYPE postgres)", database_url))?;

    con.execute_batch(&format!("DROP TABLE IF EXISTS pg.{}", table_name))?;

    println!("DuckDB: IMPORTING {} to pg.{} ...", data_file, table_name);
    con.execute(
        &format!(
            "CREATE TABLE pg.{} AS SELECT * FROM read_parquet('{}')",
            table_name, data_file
        ),
        duckdb_params![],
    )?;

    let duration = start.elapsed();
    println!(
        "Done! Execution time: {:.2} seconds",
        duration.as_secs_f64()
    );

    Ok(())
}
