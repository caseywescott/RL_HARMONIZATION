FROM --platform=linux/arm64 python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    pkg-config \
    libhdf5-dev \
    gcc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir tensorflow && \
    pip install --no-cache-dir pretty-midi note-seq==0.0.3 && \
    pip install --no-cache-dir python-multipart fastapi uvicorn requests && \
    pip install --no-cache-dir numpy && \
    rm -rf /root/.cache/pip/*

# Copy the Coconet model files
COPY coconet-64layers-128filters /app/coconet-64layers-128filters

# Copy the Magenta Coconet sampling scripts
COPY magenta-rl-tuner/magenta/models/coconet /app/magenta_coconet

# Create the correct Coconet server
COPY coconet-server/correct_coconet_server.py /app/server.py

# Create entrypoint script
RUN printf '#!/bin/sh\nexport PYTHONPATH=$PYTHONPATH:/app:/app/magenta_coconet\nexec "$@"\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"] 