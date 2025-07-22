FROM --platform=linux/arm64 python:3.8-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    pkg-config \
    libhdf5-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "tensorflow>=2.8.0,<2.11.0" && \
    pip install --no-cache-dir pretty-midi note-seq==0.0.3 && \
    pip install --no-cache-dir python-multipart fastapi uvicorn requests && \
    pip install --no-cache-dir "protobuf>=3.9.2,<3.20" && \
    pip install --no-cache-dir magenta

# Create app directory
WORKDIR /app

# Copy the Coconet model files
COPY coconet-64layers-128filters/ ./coconet-64layers-128filters/

# Copy the Magenta Coconet scripts
COPY magenta-rl-tuner/magenta/models/coconet/ ./magenta_coconet/

# Copy the server
COPY coconet-server/proper_coconet_server.py ./

# Create necessary directories
RUN mkdir -p /tmp

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "proper_coconet_server.py"] 