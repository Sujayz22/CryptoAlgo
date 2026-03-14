# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into a prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH="/app"

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Non-root user for safety
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# Default command: run daily scheduler
CMD ["python", "scheduler/run_bot.py"]
