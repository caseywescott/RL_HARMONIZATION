# RL_HARMONIZATION

A hybrid harmonization system that combines **Coconet neural network harmonization** with **Reinforcement Learning (RL) contrary motion optimization** to create high-quality 4-part harmonies.

## 🎵 **Quick Start**

### **System Overview**

This project implements a sophisticated music harmonization system that uses:

- **Coconet Neural Network**: Pre-trained model for initial harmonization
- **RL Contrary Motion Model**: Q-learning agent trained on 10,700 episodes with 168,285 states
- **FastAPI Server**: RESTful API for harmonization requests
- **Docker Container**: Containerized deployment

### **Pipeline Flow:**

```
Input Melody → Coconet Neural Harmonization → RL Contrary Motion Optimization → 4-Part Output
```

## 🚀 **Quick Deployment**

### **Docker Deployment**

```bash
# Build the container
docker build -f coconet-server/hybrid_harmonization.Dockerfile -t hybrid-harmonization-server .

# Run the server
docker run -d -p 8000:8000 --name hybrid-harmonization-server hybrid-harmonization-server
```

### **API Usage**

```bash
# Status check
curl http://localhost:8000/status

# Harmonization
curl -X POST "http://localhost:8000/harmonize?method=hybrid&temperature=0.8" \
     -F "file=@your_melody.mid"
```

## 📚 **Documentation**

📖 **Complete documentation is available in the [`docs/`](docs/) folder:**

- **[📋 Documentation Index](docs/INDEX.md)** - Organized overview of all documentation
- **[🎯 System Summary](docs/HYBRID_SYSTEM_SUMMARY.md)** - Complete hybrid system overview
- **[🚀 Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)** - Step-by-step setup instructions
- **[📊 Results & Analysis](docs/HYBRID_SYSTEM_TEST_RESULTS.md)** - System performance results

### **Quick Navigation**

- **New Users**: Start with [docs/README.md](docs/README.md)
- **Developers**: Check [docs/REPOSITORY_ORGANIZATION.md](docs/REPOSITORY_ORGANIZATION.md)
- **Researchers**: Review [docs/RL_VS_COCONET_TRAINING_ANALYSIS.md](docs/RL_VS_COCONET_TRAINING_ANALYSIS.md)

## 🏗️ **Project Structure**

```
RL_HARMONIZATION/
├── docs/                    # 📚 Complete documentation
├── tests/                   # 🧪 Test suite
├── analysis/                # 📊 Analysis tools
├── midi_files/             # 🎵 Generated MIDI files
├── coconet-server/         # 🐳 Server implementation
├── src/harmonization/      # 🤖 Core harmonization modules
├── examples/               # 📝 Usage examples
└── magenta-rl-tuner/       # 🎼 Magenta library integration
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

## 🎯 **Key Features**

- ✅ **Hybrid Approach**: Neural network creativity + RL optimization
- ✅ **Multiple Methods**: RL-only, Coconet-only, and hybrid approaches
- ✅ **Production Ready**: Containerized, API-driven system
- ✅ **Melody Preservation**: RL model guarantees melody preservation
- ✅ **Music Theory Compliance**: Optimized for contrary motion and voice leading
- ✅ **Scalable Architecture**: FastAPI server with Docker deployment

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
**Last Updated**: July 23, 2024  
**Version**: 1.0 (Production Ready)

📖 **For complete documentation, visit the [`docs/`](docs/) folder!**
