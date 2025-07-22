FROM --platform=linux/arm64 python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Set the working directory
WORKDIR /app

# Install system dependencies and clean up in one step to save space
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    pkg-config \
    libhdf5-dev \
    gcc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install TensorFlow for ARM64 Linux
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir tensorflow && \
    pip install --no-cache-dir pretty-midi note-seq==0.0.3 && \
    pip install --no-cache-dir python-multipart fastapi uvicorn requests && \
    rm -rf /root/.cache/pip/*

# Create model checkpoint directory
RUN mkdir -p /app/models/music_transformer

# Create a minimal environment for Score2Perf
RUN echo 'import sys, os\nsys.path.append("/app")\n' > /app/setup_env.py

# Copy our fixed server application
COPY fixed_server.py /app/
COPY coconet_inference.py /app/

# Create entrypoint script that will set up the environment
RUN printf '#!/bin/sh\nexport PYTHONPATH=$PYTHONPATH:/app\nexec "$@"\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Copy any additional files
COPY . .

# Expose port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "fixed_server:app", "--host", "0.0.0.0", "--port", "8000"] 