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
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "tensorflow==2.10.0" && \
    pip install --no-cache-dir pretty-midi note-seq==0.0.3 && \
    pip install --no-cache-dir python-multipart fastapi uvicorn requests && \
    pip install --no-cache-dir "protobuf>=3.9.2,<3.20" && \
    pip install --no-cache-dir numpy scipy librosa

# Install Magenta from source with modified requirements
RUN git clone https://github.com/magenta/magenta.git /tmp/magenta && \
    cd /tmp/magenta && \
    # Modify setup.py to accept tensorflow>=2.8.0 instead of ==2.9.1
    sed -i 's/tensorflow==2.9.1/tensorflow>=2.8.0/' setup.py && \
    pip install -e . && \
    rm -rf /tmp/magenta

# Create app directory
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