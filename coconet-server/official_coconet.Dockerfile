FROM --platform=linux/arm64 python:3.8-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    tensorflow==2.10.0 \
    pretty_midi \
    fastapi \
    uvicorn \
    python-multipart \
    numpy \
    scipy \
    librosa \
    "protobuf>=3.9.2,<3.20"

# Set working directory
WORKDIR /app

# Copy the Coconet model
COPY coconet-64layers-128filters /app/coconet-64layers-128filters

# Copy the official Magenta Coconet scripts
COPY magenta-rl-tuner/magenta/models/coconet /app/magenta_coconet

# Copy the server script
COPY coconet-server/official_coconet_server.py /app/server.py

# Set environment variables
ENV PYTHONPATH=/app/magenta_coconet:$PYTHONPATH

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"] 