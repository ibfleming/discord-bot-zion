FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libffi-dev \
    python3-dev \
    ffmpeg \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["bash"]
