FROM python:3.12-slim

# sys basics
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl tzdata \
    && rm -rf /var/lib/apt/lists/*

# avoid .pyc files and ensure unbuffered stdout/stderr for logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy src and needed items
COPY fizzbuzz/ ./fizzbuzz/
COPY static/ ./static/

# args provided at runtime will be appended
ENTRYPOINT ["python", "-m", "fizzbuzz"]
CMD []