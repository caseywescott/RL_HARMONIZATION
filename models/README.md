# Models Directory

This directory contains all model files, checkpoints, and training data.

## 📁 **Contents**

### **Model Files**

- `advanced_harmonization_model.json` - Advanced harmonization model (21.7 MB)
- `advanced_harmonization_model.json.checkpoint` - Model checkpoint (21.7 MB)
- `simple_contrary_motion_model_metadata.json` - Simple contrary motion model metadata
- `hybrid_model_test_results.json` - Hybrid model test results

### **Training Data**

- `reward_history.npy` - Reward history from training (85.7 KB)
- `simple_contrary_motion_reward_history.npy` - Simple model reward history (80.1 KB)

### **Model Metadata**

- `model_metadata.json` - General model metadata

## 🔧 **Usage**

### **Loading Models**

```python
import json
import numpy as np

# Load model
with open('models/advanced_harmonization_model.json', 'r') as f:
    model = json.load(f)

# Load training history
reward_history = np.load('models/reward_history.npy')
```

### **Model Information**

- **Advanced Model**: 21.7 MB - Full harmonization model with complex rules
- **Simple Model**: Metadata only - Lightweight contrary motion model
- **Training History**: 165.8 KB total - Reward curves and training progress

## 📊 **Model Details**

### **Advanced Harmonization Model**

- **Size**: 21.7 MB
- **Type**: JSON-based model
- **Features**: Complex harmonization rules and patterns
- **Checkpoint**: Available for resuming training

### **Simple Contrary Motion Model**

- **Size**: 325 bytes (metadata only)
- **Type**: Lightweight model
- **Features**: Basic contrary motion optimization
- **Training History**: 80.1 KB of reward data

### **Hybrid Model Results**

- **Size**: 1.0 KB
- **Type**: Test results and performance metrics
- **Content**: Evaluation data from hybrid system testing

## 🚀 **Training Data**

### **Reward Histories**

- **Main Model**: 85.7 KB of reward progression data
- **Simple Model**: 80.1 KB of contrary motion training data
- **Format**: NumPy arrays for easy analysis and plotting

### **Usage Examples**

```python
# Plot reward curves
import matplotlib.pyplot as plt
import numpy as np

rewards = np.load('models/reward_history.npy')
plt.plot(rewards)
plt.title('Training Reward Progression')
plt.show()
```

## 📋 **File Organization**

### **Large Files (>1MB)**

- `advanced_harmonization_model.json` - 21.7 MB
- `advanced_harmonization_model.json.checkpoint` - 21.7 MB

### **Medium Files (1KB-1MB)**

- `reward_history.npy` - 85.7 KB
- `simple_contrary_motion_reward_history.npy` - 80.1 KB

### **Small Files (<1KB)**

- `hybrid_model_test_results.json` - 1.0 KB
- `model_metadata.json` - 594 bytes
- `simple_contrary_motion_model_metadata.json` - 325 bytes

## 🔄 **Model Management**

### **Backup Strategy**

- Keep checkpoints for model recovery
- Version control metadata files
- Archive training histories for analysis

### **Loading Patterns**

- Load large models only when needed
- Use metadata for quick model information
- Access training data for analysis and visualization

---

**Total Files**: 7  
**Total Size**: ~43.4 MB  
**Status**: ✅ All model files organized and documented
