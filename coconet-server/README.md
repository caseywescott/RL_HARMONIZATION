# Coconet Server

A Docker-based music generation server using TensorFlow and the Coconet model for ARM64 architecture (Apple Silicon/M1/M2 Macs).

> **Note**: This is part of the larger RL Tuner Dockerfile Project. For complete project documentation and Dockerfile comparisons, see the [main README.md](../README.md).

## Quick Start

```bash
# Build the production server
docker build -f production-arm64.Dockerfile -t coconet-server .

# Run the server
docker run -p 8000:8000 coconet-server
```

## Overview

This project provides a containerized environment for running a music generation server based on the Coconet model. The server is specifically optimized for ARM64 architecture, making it compatible with Apple Silicon Macs (M1, M2, M3) and other ARM64 systems.

## Architecture Compatibility

- **Primary Target**: ARM64 (Apple Silicon)
- **Base Image**: `python:3.8-slim` with ARM64 platform specification
- **TensorFlow**: ARM64-compatible version (tensorflow-cpu-aws)
- **System**: Linux container running on ARM64 architecture

## Dockerfile Analysis

### Base Image

```dockerfile
FROM --platform=linux/arm64 python:3.8-slim
```

- Explicitly targets ARM64 architecture
- Uses Python 3.8 slim image for smaller size
- Ensures compatibility with Apple Silicon Macs

### System Dependencies

```dockerfile
RUN apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    pkg-config \
    libhdf5-dev \
    gcc
```

**Why these dependencies are needed:**

- `git`: For cloning repositories and version control
- `ffmpeg`: Audio/video processing capabilities
- `pkg-config`: Required for building h5py from source
- `libhdf5-dev`: HDF5 development libraries for h5py compilation
- `gcc`: C compiler needed for building scientific Python packages

### Python Dependencies

```dockerfile
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir tensorflow && \
    pip install --no-cache-dir pretty-midi note-seq==0.0.3 && \
    pip install --no-cache-dir python-multipart fastapi uvicorn requests
```

**Key packages:**

- `tensorflow`: Machine learning framework (ARM64 compatible)
- `pretty-midi`: MIDI file processing
- `note-seq==0.0.3`: Music sequence processing (specific version for compatibility)
- `fastapi`: Modern web framework for APIs
- `uvicorn`: ASGI server for FastAPI
- `python-multipart`: File upload handling
- `requests`: HTTP library

## Building the Docker Image

### Prerequisites

- Docker Desktop installed and running
- ARM64-compatible system (Apple Silicon Mac recommended)
- At least 4GB of available RAM for building

### Build Command

```bash
docker build -f production-arm64.Dockerfile -t coconet-server .
```

**Build Time**: Approximately 5-10 minutes on M1/M2 Mac
**Image Size**: ~2-3GB (includes TensorFlow and all dependencies)

### Build Process Details

1. **Base Image Pull**: Downloads ARM64 Python 3.8 slim image
2. **System Dependencies**: Installs required system packages (~1-2 minutes)
3. **Python Dependencies**: Installs TensorFlow and other packages (~3-5 minutes)
   - TensorFlow installation includes ARM64-optimized binaries
   - h5py compilation from source (requires gcc and HDF5)
4. **Application Setup**: Copies server files and sets up environment

## Running the Server

### Basic Run Command

```bash
docker run -p 8000:8000 coconet-server
```

### With Volume Mounting (for model persistence)

```bash
docker run -p 8000:8000 -v $(pwd)/models:/app/models coconet-server
```

### With Custom Configuration

```bash
docker run -p 8000:8000 \
  -e PYTHONPATH=/app \
  -v $(pwd)/models:/app/models \
  coconet-server
```

## Environment Variables

- `PYTHONPATH`: Set to `/app` for proper module imports
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered
- `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`: Uses Python implementation for protobuf

## Port Configuration

- **Container Port**: 8000 (FastAPI server)
- **Host Port**: 8000 (mapped to container)
- **Protocol**: HTTP/HTTPS

## File Structure

```
/app/
├── server.py              # Main FastAPI application
├── setup_env.py           # Environment setup script
├── models/                # Model storage directory
│   └── music_transformer/ # Transformer model files
└── entrypoint.sh          # Container entrypoint script
```

## Troubleshooting

### Common Issues

1. **Build Fails with h5py Error**

   - **Cause**: Missing gcc or HDF5 development libraries
   - **Solution**: Ensure Dockerfile includes `gcc` and `libhdf5-dev`

2. **TensorFlow Import Errors**

   - **Cause**: Architecture mismatch
   - **Solution**: Verify using ARM64 base image and tensorflow package

3. **Port Already in Use**

   - **Cause**: Another service using port 8000
   - **Solution**: Use different port mapping: `-p 8001:8000`

4. **Memory Issues During Build**
   - **Cause**: Insufficient RAM for TensorFlow compilation
   - **Solution**: Increase Docker Desktop memory limit to 8GB+

### Performance Optimization

1. **Build Caching**: Docker layers are cached for faster rebuilds
2. **Multi-stage Builds**: Consider using multi-stage builds for smaller final image
3. **Volume Mounting**: Use volumes for model persistence across container restarts

## Development Workflow

### Local Development

1. Build the image: `docker build -f production-arm64.Dockerfile -t coconet-server .`
2. Run with volume mounting for live code changes
3. Access API at `http://localhost:8000`

### Production Deployment

1. Build optimized image
2. Use proper volume mounting for model persistence
3. Configure reverse proxy (nginx) if needed
4. Set up monitoring and logging

## API Endpoints

The server exposes FastAPI endpoints for music generation. Check the server.py file for specific endpoint documentation.

## Security Considerations

- Container runs as root (consider using non-root user for production)
- No SSL/TLS by default (add reverse proxy for HTTPS)
- Validate all input data in API endpoints
- Use secrets management for sensitive configuration

## Monitoring and Logging

- FastAPI provides automatic API documentation at `/docs`
- Container logs available via `docker logs <container_id>`
- Consider adding structured logging for production use

## Comparison with Development Environment

| Aspect           | Production Server | Development Environment |
| ---------------- | ----------------- | ----------------------- |
| **Purpose**      | API server        | Jupyter notebooks       |
| **Architecture** | ARM64             | x86_64                  |
| **Base Image**   | python:3.8-slim   | python:3.7.9-buster     |
| **TensorFlow**   | Latest ARM64      | 2.5.0                   |
| **Port**         | 8000              | 8888                    |
| **Use Case**     | Production        | Development             |

For more details on the development environment, see the [main project documentation](../README.md).

## Future Improvements

1. **Multi-architecture Support**: Add x86_64 support
2. **GPU Support**: Add CUDA support for NVIDIA GPUs
3. **Optimization**: Use TensorFlow Serving for better performance
4. **Security**: Implement proper user management and authentication
5. **Monitoring**: Add health checks and metrics collection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test on ARM64 architecture
4. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review Docker and FastAPI documentation
3. Open an issue in the repository
