# Multi-stage build for optimized image size and build time

# Builder stage: Install dependencies and Python packages
FROM python:3.13.7-slim AS builder

# Install build dependencies for Python packages with C extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for builder
WORKDIR /build

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies system-wide
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage: Minimal image for running the bot
FROM python:3.13.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the bot source code (excluding files in .dockerignore)
COPY . .

# Create a non-root user and switch to it
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

# Entry point
CMD ["python", "src/bot.py"]
