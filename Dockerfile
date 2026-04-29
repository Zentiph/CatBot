FROM rust:alpine AS builder

RUN apk add --no-cache \
    pkgconfig \
    openssl-dev openssl-libs-static \
    sqlite-dev sqlite-static \
    cmake clang clang-dev \
    musl-dev

ENV OPENSSL_STATIC=1
ENV SQLITE3_STATIC=1

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release

FROM alpine:3.23

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=builder /app/target/release/fizzbuzz ./fizzbuzz
COPY public/ ./public/

ENTRYPOINT ["./fizzbuzz"]
CMD []
