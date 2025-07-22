FROM --platform=linux/arm64 python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    pkg-config \
    libhdf5-dev \
    build-essential \
    gcc \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    tensorflow==2.10.0 \
    tensorflow-probability==0.18.0 \
    pretty-midi \
    note-seq==0.0.3 \
    python-multipart \
    fastapi \
    uvicorn \
    requests \
    "protobuf>=3.9.2,<3.20" \
    numpy \
    scipy \
    librosa

# Set working directory
WORKDIR /app

# Copy Coconet model
COPY coconet-64layers-128filters /app/coconet-64layers-128filters

# Copy Magenta library
COPY magenta-rl-tuner/magenta /app/magenta

# Fix model checkpoint path in graph.pbtxt
RUN sed -i 's/model_checkpoint_path: "model.ckpt"/model_checkpoint_path: "best_model.ckpt"/g' /app/coconet-64layers-128filters/graph.pbtxt

# Copy the corrected melody preserving server
COPY coconet-server/corrected_melody_preserving_server.py /app/server.py

# Set environment variables
ENV PYTHONPATH=/app
ENV TF_CPP_MIN_LOG_LEVEL=2

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"] 