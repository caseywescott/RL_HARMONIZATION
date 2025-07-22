# Data Directory

This directory contains input data, output files, and visualizations.

## 📁 **Contents**

### **Input MIDI Files**

- `realms2_idea.midi` - Original Realms melody (382 bytes)
- `coconet_harmonized_realms2_idea.midi` - Coconet harmonized version (1.2 KB)
- `rl_optimized_coconet_harmonized_realms2_idea.midi` - RL optimized version (1.2 KB)

### **Visualizations**

- `reward_curve.png` - Training reward curve visualization (223.5 KB)

## 🎵 **MIDI Files**

### **Input Melody**

- **File**: `realms2_idea.midi`
- **Size**: 382 bytes
- **Description**: Original melody for harmonization testing
- **Usage**: Primary input for harmonization experiments

### **Harmonized Outputs**

- **Coconet Version**: `coconet_harmonized_realms2_idea.midi` (1.2 KB)

  - Neural network harmonization output
  - 4-part harmony structure
  - May not preserve original melody

- **RL Optimized Version**: `rl_optimized_coconet_harmonized_realms2_idea.midi` (1.2 KB)
  - RL-optimized harmonization
  - Guaranteed melody preservation
  - Enhanced voice leading

## 📊 **Visualizations**

### **Training Progress**

- **File**: `reward_curve.png`
- **Size**: 223.5 KB
- **Content**: Training reward progression visualization
- **Format**: PNG image for easy viewing

## 🔧 **Usage**

### **Loading MIDI Files**

```python
import pretty_midi

# Load original melody
original = pretty_midi.PrettyMIDI('data/realms2_idea.midi')

# Load harmonized versions
coconet_version = pretty_midi.PrettyMIDI('data/coconet_harmonized_realms2_idea.midi')
rl_version = pretty_midi.PrettyMIDI('data/rl_optimized_coconet_harmonized_realms2_idea.midi')
```

### **Comparing Harmonizations**

```python
# Compare different harmonization approaches
def compare_harmonizations():
    original = pretty_midi.PrettyMIDI('data/realms2_idea.midi')
    coconet = pretty_midi.PrettyMIDI('data/coconet_harmonized_realms2_idea.midi')
    rl = pretty_midi.PrettyMIDI('data/rl_optimized_coconet_harmonized_realms2_idea.midi')

    print(f"Original: {len(original.instruments[0].notes)} notes")
    print(f"Coconet: {len(coconet.instruments)} instruments")
    print(f"RL Optimized: {len(rl.instruments)} instruments")
```

## 📋 **File Analysis**

### **MIDI Files**

- **Total MIDI Files**: 3
- **Total Size**: 2.8 KB
- **Formats**: .midi files for music processing

### **Visualizations**

- **Total Images**: 1
- **Total Size**: 223.5 KB
- **Format**: PNG for training visualization

## 🎯 **Data Workflow**

### **Input Processing**

1. **Original Melody**: `realms2_idea.midi` serves as input
2. **Coconet Processing**: Neural network generates initial harmonization
3. **RL Optimization**: Reinforcement learning optimizes the output

### **Output Analysis**

1. **File Comparison**: Compare different harmonization approaches
2. **Quality Assessment**: Evaluate melody preservation and voice leading
3. **Performance Metrics**: Analyze file sizes and note distributions

## 🔄 **Data Management**

### **File Organization**

- **Input**: Original melodies and test data
- **Output**: Generated harmonizations and results
- **Visualizations**: Training progress and analysis charts

### **Version Control**

- Track input files for reproducibility
- Archive output files for comparison
- Maintain visualization history

---

**Total Files**: 4  
**Total Size**: ~226.3 KB  
**Status**: ✅ All data files organized and documented
