# 🏗️ Repository Organization - Hybrid Harmonization System

## 📁 Directory Structure Overview

```
RL_HARMONIZATION/
├── 📚 docs/                           # Documentation
│   ├── EXAMPLE_MIDI_DEMONSTRATION.md  # Example MIDI analysis
│   └── (other documentation files)
├── 🎵 examples/                       # Example scripts and outputs
│   ├── README.md                      # Examples usage guide
│   ├── generate_example_midi.py       # Generate example MIDI files
│   ├── analyze_example_midis.py       # Analyze generated files
│   ├── basic_usage.py                 # Basic usage examples
│   └── output/                        # Generated example MIDI files
│       ├── example_rl_output.mid      # RL-only harmonization
│       ├── example_coconet_output.mid # Coconet-only harmonization
│       └── example_hybrid_output.mid  # Hybrid harmonization
├── 🐳 coconet-server/                 # Server implementation
│   ├── hybrid_harmonization_server.py # Main hybrid server
│   ├── hybrid_harmonization.Dockerfile # Docker configuration
│   └── (other server implementations)
├── 🤖 saved_models/                   # Trained RL models
│   ├── load_model.py                  # Model loading utilities
│   └── (model files)
├── 📊 multiple_harmonizations/        # Multiple harmonization outputs
│   └── (various harmonization files)
├── 🔧 src/harmonization/              # Core harmonization modules
│   ├── core/                          # Core functionality
│   └── rewards/                       # Reward functions
├── 🎼 magenta-rl-tuner/               # Magenta library integration
├── 📋 Core Files                      # Main project files
│   ├── HYBRID_SYSTEM_SUMMARY.md       # System overview
│   ├── advanced_training.py           # Advanced RL training
│   ├── 4part_contrary_motion_harmonize.py # 4-part harmonization
│   └── (other core files)
└── 🎵 MIDI Files                      # Various MIDI outputs
    ├── realms2_harmonized.mid         # Input melody
    └── (other MIDI files)
```

## 🎯 Organization Principles

### **1. Clear Separation of Concerns**

- **`docs/`**: All documentation and guides
- **`examples/`**: Example scripts and demonstration outputs
- **`coconet-server/`**: Server implementations and Docker configs
- **`saved_models/`**: Trained models and model utilities
- **`src/`**: Core harmonization modules

### **2. Example-Driven Development**

- **`examples/output/`**: Contains all generated example MIDI files
- **`examples/generate_example_midi.py`**: Script to generate examples
- **`examples/analyze_example_midis.py`**: Script to analyze outputs
- **`examples/README.md`**: Comprehensive usage guide

### **3. Documentation-First Approach**

- **`docs/EXAMPLE_MIDI_DEMONSTRATION.md`**: Detailed example analysis
- **`HYBRID_SYSTEM_SUMMARY.md`**: Complete system overview
- **`examples/README.md`**: Examples usage guide

## 🚀 Quick Start Guide

### **1. Generate Example MIDI Files**

```bash
# Start the hybrid harmonization server
docker run -d -p 8000:8000 hybrid-harmonization-server

# Generate example MIDI files
python3 examples/generate_example_midi.py
```

### **2. Analyze Generated Files**

```bash
# Analyze the generated MIDI files
python3 examples/analyze_example_midis.py
```

### **3. View Results**

```bash
# Check the generated files
ls -la examples/output/
```

## 📊 Example Output Files

| Method           | File                                         | Size        | Notes     | Description                   |
| ---------------- | -------------------------------------------- | ----------- | --------- | ----------------------------- |
| **RL-Only**      | `examples/output/example_rl_output.mid`      | 2,817 bytes | 304 notes | Full 4-part RL harmonization  |
| **Coconet-Only** | `examples/output/example_coconet_output.mid` | 405 bytes   | 36 notes  | Neural network harmonization  |
| **Hybrid**       | `examples/output/example_hybrid_output.mid`  | 365 bytes   | 32 notes  | **Coconet → RL optimization** |

## 🔧 Key Scripts and Their Locations

### **Example Generation**

- **`examples/generate_example_midi.py`**: Generate example MIDI files
- **`examples/analyze_example_midis.py`**: Analyze generated files
- **`examples/basic_usage.py`**: Basic usage examples

### **Core Harmonization**

- **`4part_contrary_motion_harmonize.py`**: 4-part harmonization
- **`advanced_training.py`**: Advanced RL training
- **`coconet_harmonization.py`**: Coconet integration

### **Server Implementation**

- **`coconet-server/hybrid_harmonization_server.py`**: Main hybrid server
- **`coconet-server/hybrid_harmonization.Dockerfile`**: Docker configuration

### **Model Management**

- **`saved_models/load_model.py`**: Model loading utilities

## 📚 Documentation Structure

### **System Overview**

- **`HYBRID_SYSTEM_SUMMARY.md`**: Complete system documentation
- **`REPOSITORY_ORGANIZATION.md`**: This file - repository structure

### **Examples and Demonstrations**

- **`docs/EXAMPLE_MIDI_DEMONSTRATION.md`**: Detailed example analysis
- **`examples/README.md`**: Examples usage guide

### **Implementation Guides**

- **`IMPLEMENTATION_GUIDE.md`**: Implementation details
- **`Implementation_Plan.md`**: Development plan

## 🎵 MIDI File Organization

### **Input Files**

- **`realms2_harmonized.mid`**: Primary input melody

### **Example Outputs**

- **`examples/output/`**: All generated example files

### **Multiple Harmonizations**

- **`multiple_harmonizations/`**: Various harmonization attempts

### **Test Files**

- Various test MIDI files throughout the repository

## 🔍 Analysis and Evaluation

### **Analysis Scripts**

- **`examples/analyze_example_midis.py`**: Example file analysis
- **`analyze_*.py`**: Various analysis scripts

### **Evaluation Framework**

- **`evaluation_framework.py`**: Evaluation utilities
- **`comprehensive_evaluation_study.py`**: Comprehensive evaluation

## 🐳 Docker and Deployment

### **Server Containers**

- **`coconet-server/hybrid_harmonization.Dockerfile`**: Main server
- **`coconet-server/*.Dockerfile`**: Various server configurations

### **Model Files**

- **`coconet-64layers-128filters/`**: Coconet model files

## 🎯 Best Practices

### **File Naming**

- Use descriptive names for MIDI files
- Include method and version in filenames
- Organize outputs by type and date

### **Directory Structure**

- Keep examples separate from core code
- Organize documentation by topic
- Maintain clear separation between different components

### **Documentation**

- Update documentation when adding new features
- Include usage examples in README files
- Document file paths and dependencies

## 📈 Performance Metrics

The organized repository demonstrates:

- **Clear Structure**: Logical organization of files and directories
- **Easy Navigation**: Intuitive file and directory names
- **Comprehensive Documentation**: Detailed guides and examples
- **Reproducible Examples**: Working example generation scripts
- **Scalable Architecture**: Modular design for future expansion

## 🎉 Success Metrics

✅ **Repository Organization Complete**

- All files properly organized into logical directories
- Clear separation between examples, documentation, and core code
- Comprehensive documentation for all components
- Working example generation and analysis scripts
- Clean commit history with descriptive messages

---

**Status**: ✅ **FULLY ORGANIZED**  
**Last Updated**: July 22, 2024  
**Organization Version**: 1.0
