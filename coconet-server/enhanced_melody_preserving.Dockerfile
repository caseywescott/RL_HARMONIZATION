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

# Copy Coconet model
COPY coconet-64layers-128filters /app/coconet-64layers-128filters

# Copy Magenta library
COPY magenta-rl-tuner/magenta /app/magenta

# Fix model checkpoint path in graph.pbtxt
RUN sed -i 's/model_checkpoint_path: "model.ckpt"/model_checkpoint_path: "best_model.ckpt"/g' /app/coconet-64layers-128filters/graph.pbtxt

# Copy the enhanced melody-preserving server
COPY coconet-server/enhanced_melody_preserving_server.py /app/server.py

WORKDIR /app

EXPOSE 8000

CMD ["python", "server.py"] 