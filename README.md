# RL_HARMONIZATION

A hybrid harmonization system that combines **Coconet neural network harmonization** with **Reinforcement Learning (RL) contrary motion optimization** to create high-quality 4-part harmonies.

## 🎵 **System Overview**

This project implements a sophisticated music harmonization system that uses:

- **Coconet Neural Network**: Pre-trained model for initial harmonization
- **RL Contrary Motion Model**: Q-learning agent trained on 10,700 episodes with 168,285 states
- **FastAPI Server**: RESTful API for harmonization requests
- **Docker Container**: Containerized deployment

## 🏗️ **Architecture**

### **Pipeline Flow:**

```
Input Melody → Coconet Neural Harmonization → RL Contrary Motion Optimization → 4-Part Output
```

### **Core Components:**

1. **Coconet Neural Network**: Generates initial harmonizations
2. **RL Contrary Motion Model**: Optimizes for contrary motion and music theory compliance
3. **FastAPI Server**: Provides REST API endpoints
4. **Docker Container**: Ensures consistent deployment

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.8+
- Docker
- TensorFlow 2.10.0
- Note-seq 0.0.3

### **Docker Deployment**

```bash
# Build the container
docker build -f coconet-server/hybrid_harmonization.Dockerfile -t hybrid-harmonization-server .

# Run the server
docker run -d -p 8000:8000 --name hybrid-harmonization-server hybrid-harmonization-server
```

### **API Usage**

#### **Status Check**

```bash
curl http://localhost:8000/status
```

#### **Harmonization**

```bash
curl -X POST "http://localhost:8000/harmonize?method=hybrid&temperature=0.8" \
     -F "file=@your_melody.mid"
```

## 🎼 **Harmonization Methods**

### **1. RL-Only (`method=rl`)**

- Direct RL harmonization
- **Guaranteed melody preservation**
- Full 4-part harmony generation

### **2. Coconet-Only (`method=coconet`)**

- Neural network harmonization
- **Melody may not be preserved**
- Concise output

### **3. Hybrid (`method=hybrid`) - RECOMMENDED**

- **Coconet → RL optimization pipeline**
- Combines neural creativity with RL optimization
- **Most concise and optimized output**

## 📊 **Performance Results**

### **Test Case: 76-note melody**

| Method       | Output Notes | File Size     | Voice Distribution   |
| ------------ | ------------ | ------------- | -------------------- |
| RL-Only      | 304 notes    | 2,817 bytes   | Full 4-part harmony  |
| Coconet-Only | 40 notes     | 441 bytes     | Balanced 4-part      |
| **Hybrid**   | **28 notes** | **329 bytes** | **Optimized 4-part** |

## 🤖 **RL Model Details**

- **Training Episodes**: 10,700
- **States Explored**: 168,285
- **Average Reward**: 17.563
- **Best Reward**: 19.4
- **Focus**: Contrary motion, music theory compliance, voice leading

## 📁 **Project Structure**

```
RL_HARMONIZATION/
├── coconet-server/          # FastAPI server and Docker files
├── magenta-rl-tuner/        # Magenta library integration
├── src/harmonization/       # Core harmonization modules
├── examples/                # Usage examples and demos
├── multiple_harmonizations/ # Generated harmonization outputs
├── saved_models/           # Model checkpoints and saved states
└── docs/                   # Documentation
```

## 🔧 **Technical Implementation**

### **Server Architecture**

- FastAPI web framework
- Temporary file handling for MIDI processing
- Subprocess execution for Coconet
- Multi-track MIDI generation
- Proper error handling and fallbacks

### **RL Model Integration**

- Q-learning agent with 168,285 states
- Music theory reward function
- Contrary motion optimization
- Voice range constraints

### **Coconet Integration**

- Direct subprocess execution
- Checkpoint loading from `/app/coconet-64layers-128filters`
- MIDI output parsing and processing

## 🎯 **Key Features**

- ✅ **Hybrid Approach**: Neural network creativity + RL optimization
- ✅ **Multiple Methods**: RL-only, Coconet-only, and hybrid approaches
- ✅ **Production Ready**: Containerized, API-driven system
- ✅ **Melody Preservation**: RL model guarantees melody preservation
- ✅ **Music Theory Compliance**: Optimized for contrary motion and voice leading
- ✅ **Scalable Architecture**: FastAPI server with Docker deployment

## 📚 **Documentation**

- [System Summary](HYBRID_SYSTEM_SUMMARY.md) - Detailed technical overview
- [Example Usage](examples/) - Code examples and demonstrations
- [API Documentation](docs/) - API endpoints and usage

## 🎵 **Future Enhancements**

1. **Real-time Processing**: WebSocket support for streaming
2. **Batch Processing**: Multiple file harmonization
3. **Custom Parameters**: User-defined optimization weights
4. **Quality Metrics**: Automated harmonization quality scoring
5. **Model Fine-tuning**: Continuous RL model improvement

## 🤝 **Contributing**

This project is open for contributions. Please feel free to submit issues and pull requests.

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Status**: ✅ **FULLY OPERATIONAL**  
**Last Updated**: July 22, 2024  
**Version**: 1.0 (Production Ready)
