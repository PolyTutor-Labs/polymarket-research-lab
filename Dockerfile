FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install -e .

# Copy rest of project
COPY . .

# Research image should not run as root.
RUN adduser --disabled-password --gecos "" --uid 1000 watchdog \
    && chown -R watchdog:watchdog /app
USER watchdog

CMD ["watchdog", "run-btc-scalp"]
