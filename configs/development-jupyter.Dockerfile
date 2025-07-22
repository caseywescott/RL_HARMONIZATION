# Use a specific older Python 3.7 image that supports TF1.15
FROM python:3.7.9-buster

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN set -ex; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    dirmngr \
    ca-certificates \
    wget && \
    rm -rf /var/lib/apt/lists/* && \
    wget -qO - https://ftp-master.debian.org/keys/archive-key-10.asc | apt-key add - && \
    wget -qO - https://ftp-master.debian.org/keys/archive-key-10-security.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libasound2-dev \
    libportmidi-dev \
    libsndfile1 \
    ffmpeg \
    unzip \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install TensorFlow 2.5.0 and dependencies (updated from TF1.15)
RUN pip install --upgrade pip setuptools wheel
RUN pip install numpy==1.19.5
RUN pip install tensorflow==2.5.0
RUN pip install keras==2.4.3
RUN pip install h5py==3.1.0
RUN pip install protobuf==3.20.0
RUN pip install magenta==2.1.4 note-seq==0.0.2

# Create working directory
WORKDIR /app

# Expose Jupyter port
EXPOSE 8888

# Default command is to start Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
