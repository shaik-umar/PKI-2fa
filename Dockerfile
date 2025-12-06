# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Critical: Set Timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install system tools (Cron and Timezone data)
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy Application Code
COPY . .

# Create Volume Mount Points (for persistence)
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Setup Cron Job
# We copy the cron file to the system cron directory
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# Expose API Port
EXPOSE 8001

# Start Command: Runs BOTH Cron and FastAPI
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8001