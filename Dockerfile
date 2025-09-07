# Use a slim official Python base image
FROM python:3.13.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies for ffmpeg
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libffi-dev \
    python3-dev \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot source code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Entry point
CMD ["python", "src/bot.py"]