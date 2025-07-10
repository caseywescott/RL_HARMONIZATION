# RL Tuner Dockerfile Project

This repository contains two different Docker environments for music generation and machine learning, each optimized for different use cases and architectures.

## Project Structure

```
rl_tuner_dockerfile_check/
├── README.md                           # This file - main project documentation
├── development-jupyter.Dockerfile      # Development environment (Jupyter + Magenta)
└── coconet-server/
    ├── README.md                      # Coconet server specific documentation
    ├── production-arm64.Dockerfile    # Production server (FastAPI + ARM64)
    ├── requirements.txt               # Python dependencies
    └── server.py                      # FastAPI application
```

## Quick Start Guide

### For Apple Silicon Macs (M1/M2/M3) - **RECOMMENDED**

```bash
cd coconet-server
docker build -f production-arm64.Dockerfile -t coconet-server .
docker run -p 8000:8000 coconet-server
```

### For x86_64 Development

```bash
docker build -f development-jupyter.Dockerfile -t rl-tuner-dev .
docker run -p 8888:8888 rl-tuner-dev
```

## Dockerfile Comparison

### 1. Development Environment (`development-jupyter.Dockerfile`)

**Purpose**: Jupyter notebook environment for research and experimentation

**Key Characteristics:**

- **Architecture**: x86_64 (Intel/AMD)
- **Base Image**: `python:3.7.9-buster`
- **TensorFlow**: 2.5.0 (older, stable version)
- **Includes**: Magenta 2.1.4, Jupyter Notebook
- **Port**: 8888 (Jupyter interface)
- **Use Case**: Development, research, experimentation

**Best For:**

- Researchers and developers who need interactive notebooks
- Experimentation with Magenta models
- Development work on x86_64 systems
- Educational purposes

**Build Command:**

```bash
docker build -f development-jupyter.Dockerfile -t rl-tuner-dev .
```

**Run Command:**

```bash
docker run -p 8888:8888 rl-tuner-dev
```

### 2. Production Server (`coconet-server/production-arm64.Dockerfile`)

**Purpose**: Production-ready FastAPI server for music generation

**Key Characteristics:**

- **Architecture**: ARM64 (Apple Silicon optimized)
- **Base Image**: `python:3.8-slim` with ARM64 platform
- **TensorFlow**: Latest ARM64-compatible version
- **Includes**: FastAPI, uvicorn, modern dependencies
- **Port**: 8000 (API server)
- **Use Case**: Production deployment, API services

**Best For:**

- Production deployments
- Apple Silicon Macs (M1, M2, M3)
- ARM64 cloud instances
- API-based music generation services

**Build Command:**

```bash
cd coconet-server
docker build -f production-arm64.Dockerfile -t coconet-server .
```

**Run Command:**

```bash
docker run -p 8000:8000 coconet-server
```

## Architecture Compatibility

| Dockerfile                       | x86_64 | ARM64 | Apple Silicon |
| -------------------------------- | ------ | ----- | ------------- |
| `development-jupyter.Dockerfile` | ✅     | ❌    | ❌            |
| `production-arm64.Dockerfile`    | ❌     | ✅    | ✅            |

## Use Case Decision Guide

### Choose `development-jupyter.Dockerfile` if:

- You need Jupyter notebooks for development
- You're working on an Intel/AMD system
- You need Magenta library access
- You're doing research or experimentation
- You want an interactive development environment

### Choose `production-arm64.Dockerfile` if:

- You're using an Apple Silicon Mac (M1/M2/M3)
- You need a production API server
- You want modern TensorFlow versions
- You're deploying to ARM64 cloud instances
- You need FastAPI-based services

## Migration Paths

### From Development to Production:

1. Develop using the development Dockerfile (Jupyter environment)
2. Test your models and algorithms
3. Deploy using the production Dockerfile (FastAPI)

### From x86_64 to ARM64:

- Use the production Dockerfile for ARM64 compatibility
- Consider updating the development Dockerfile to ARM64 if you need Jupyter on Apple Silicon

## Performance Considerations

### Development Environment:

- **Build Time**: ~5-10 minutes
- **Image Size**: ~3-4GB
- **Memory Usage**: Moderate (Jupyter + TensorFlow)
- **Best For**: Interactive development

### Production Server:

- **Build Time**: ~5-10 minutes
- **Image Size**: ~2-3GB
- **Memory Usage**: Optimized for production
- **Best For**: High-performance API serving

## Security Considerations

### Development Environment:

- Runs Jupyter with root access
- Exposed notebook interface
- Suitable for development only

### Production Server:

- FastAPI with proper request handling
- Better security practices
- Suitable for production deployment

## Troubleshooting

### Common Issues:

1. **Architecture Mismatch**

   - **Error**: "exec /bin/sh: exec format error"
   - **Solution**: Use the correct Dockerfile for your architecture

2. **Port Conflicts**

   - **Error**: "port already in use"
   - **Solution**: Use different port mappings or stop conflicting services

3. **Memory Issues**
   - **Error**: Build fails or container crashes
   - **Solution**: Increase Docker memory limits (8GB+ recommended)

### Platform-Specific Issues:

**Apple Silicon (M1/M2/M3):**

- Always use the `production-arm64.Dockerfile`
- Ensure Docker Desktop is configured for ARM64
- May need to increase memory limits

**Intel/AMD Systems:**

- Use the `development-jupyter.Dockerfile` for development
- Consider the production Dockerfile for production (if ARM64 compatible)

## Future Improvements

1. **Unified Multi-Architecture Support**

   - Create a single Dockerfile that works on both architectures
   - Use multi-stage builds for optimization

2. **Enhanced Security**

   - Non-root user execution
   - Proper secrets management
   - SSL/TLS support

3. **Performance Optimization**
   - GPU support for both architectures
   - TensorFlow Serving integration
   - Caching optimizations

## Contributing

When contributing to this project:

1. **Test on Both Architectures**: Ensure compatibility with both x86_64 and ARM64
2. **Update Documentation**: Keep this README and individual Dockerfile documentation current
3. **Version Compatibility**: Test with different TensorFlow and dependency versions
4. **Performance Testing**: Benchmark changes on target architectures

## Support

For issues and questions:

1. **Check Architecture**: Ensure you're using the correct Dockerfile for your system
2. **Review Documentation**: Check the specific README files in each directory
3. **Troubleshooting**: See the troubleshooting sections in individual README files
4. **Open Issues**: Create detailed issue reports with your system specifications

## License

[Add your license information here]
