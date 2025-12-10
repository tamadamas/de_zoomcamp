FROM rust:1.91.1-slim-trixie as build

# Caching Rust strategy from https://depot.dev/docs/container-builds/optimal-dockerfiles/rust-dockerfile
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev && \
    rm -rf /var/lib/apt/lists/*

RUN cargo install cargo-chef sccache --locked
ENV RUSTC_WRAPPER=sccache \
    SCCACHE_DIR=/sccache

WORKDIR /app
COPY Cargo.toml Cargo.lock ./

RUN cargo chef prepare --recipe-path recipe.json
RUN --mount=type=cache,target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,target=/usr/local/cargo/git,sharing=locked \
    --mount=type=cache,target=$SCCACHE_DIR,sharing=locked \
    cargo chef cook --release --recipe-path recipe.json

COPY . .

RUN --mount=type=cache,target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,target=/usr/local/cargo/git,sharing=locked \
    --mount=type=cache,target=$SCCACHE_DIR,sharing=locked \
    cargo build --release --bin de_zoomcamp

FROM debian:trixie-slim AS runtime

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /home/appuser -s /bin/bash appuser
COPY --from=build --chown=appuser:appgroup /app/target/release/de_zoomcamp /app/de_zoomcamp
USER appuser

ENTRYPOINT ["/app/de_zoomcamp"]
