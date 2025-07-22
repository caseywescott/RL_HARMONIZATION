# Configs Directory

This directory contains configuration files, Docker files, and setup scripts.

## 📁 **Contents**

### **Docker Configuration**

- `development-jupyter.Dockerfile` - Development environment with Jupyter (1.3 KB)

### **Configuration Files**

- `requirements.txt` - Python dependencies (403 bytes)

### **Output Files**

- `realms2_4voice_contrary_motion.txt` - 4-voice contrary motion output (1.8 KB)
- `simple_contrary_motion_training_summary.txt` - Training summary (310 bytes)
- `test_harmonization_output.txt` - Test harmonization output (671 bytes)

## 🔧 **Configuration Files**

### **Docker Setup**

- **File**: `development-jupyter.Dockerfile`
- **Size**: 1.3 KB
- **Purpose**: Development environment with Jupyter notebook support
- **Usage**: Build development container for interactive work

### **Python Dependencies**

- **File**: `requirements.txt`
- **Size**: 403 bytes
- **Purpose**: Python package dependencies
- **Usage**: Install required packages with `pip install -r configs/requirements.txt`

## 📊 **Output Files**

### **Harmonization Results**

- **File**: `realms2_4voice_contrary_motion.txt`
- **Size**: 1.8 KB
- **Content**: 4-voice contrary motion harmonization output
- **Format**: Text file with harmonization details

### **Training Summary**

- **File**: `simple_contrary_motion_training_summary.txt`
- **Size**: 310 bytes
- **Content**: Summary of simple contrary motion training
- **Format**: Text file with training metrics

### **Test Output**

- **File**: `test_harmonization_output.txt`
- **Size**: 671 bytes
- **Content**: Test harmonization results
- **Format**: Text file with test results

## 🚀 **Usage**

### **Setting Up Development Environment**

```bash
# Build development container
docker build -f configs/development-jupyter.Dockerfile -t rl-harmonization-dev .

# Run development container
docker run -p 8888:8888 rl-harmonization-dev
```

### **Installing Dependencies**

```bash
# Install Python dependencies
pip install -r configs/requirements.txt

# Or with specific Python version
python3 -m pip install -r configs/requirements.txt
```

### **Viewing Output Files**

```bash
# View harmonization results
cat configs/realms2_4voice_contrary_motion.txt

# View training summary
cat configs/simple_contrary_motion_training_summary.txt

# View test results
cat configs/test_harmonization_output.txt
```

## 📋 **File Categories**

### **Setup Files**

- **Docker**: Development environment configuration
- **Dependencies**: Python package requirements
- **Documentation**: Setup and configuration guides

### **Output Files**

- **Results**: Harmonization output and results
- **Summaries**: Training and testing summaries
- **Logs**: Output logs and debugging information

## 🔄 **Configuration Management**

### **Environment Setup**

1. **Docker**: Use Dockerfile for consistent development environment
2. **Dependencies**: Manage Python packages with requirements.txt
3. **Configuration**: Centralize all configuration files

### **Output Management**

1. **Results**: Store harmonization outputs for analysis
2. **Logs**: Maintain training and testing logs
3. **Summaries**: Keep performance summaries for reference

## 📊 **File Analysis**

### **Configuration Files**

- **Docker**: 1.3 KB - Development environment setup
- **Requirements**: 403 bytes - Python dependencies

### **Output Files**

- **Harmonization**: 1.8 KB - Detailed harmonization results
- **Training**: 310 bytes - Training performance summary
- **Testing**: 671 bytes - Test results and metrics

---

**Total Files**: 5  
**Total Size**: ~4.5 KB  
**Status**: ✅ All configuration files organized and documented
