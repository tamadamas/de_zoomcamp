FROM rust:1.91.1-slim-trixie

RUN useradd -m user

RUN apt update && \
    apt install -y ca-certificates just && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
USER user

COPY . .

RUN cargo build --release

CMD ["bash"]
