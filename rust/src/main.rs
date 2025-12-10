use std::env;

fn main() {
    for arg in env::args() {
        println!("{}", arg);
    }

    let day = env::args().nth(1).expect("Day not provided");
    println!("Job finished successfully for day = {}!", day);
}
