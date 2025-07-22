# 🎵 Examples - Hybrid Harmonization System

This directory contains example scripts and output files demonstrating the hybrid harmonization system.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file
├── generate_example_midi.py     # Script to generate example MIDI files
├── analyze_example_midis.py     # Script to analyze generated MIDI files
└── output/                      # Generated example MIDI files
    ├── example_rl_output.mid    # RL-only harmonization
    ├── example_coconet_output.mid # Coconet-only harmonization
    └── example_hybrid_output.mid  # Hybrid harmonization (recommended)
```

## 🚀 Quick Start

### Generate Example MIDI Files

```bash
# Make sure the hybrid harmonization server is running
docker run -d -p 8000:8000 hybrid-harmonization-server

# Generate example MIDI files using the realms2 melody
python3 examples/generate_example_midi.py
```

### Analyze Generated Files

```bash
# Analyze the generated MIDI files
python3 examples/analyze_example_midis.py
```

## 📊 Example Output Files

| Method           | File                                | Size        | Notes     | Description                   |
| ---------------- | ----------------------------------- | ----------- | --------- | ----------------------------- |
| **RL-Only**      | `output/example_rl_output.mid`      | 2,817 bytes | 304 notes | Full 4-part RL harmonization  |
| **Coconet-Only** | `output/example_coconet_output.mid` | 405 bytes   | 36 notes  | Neural network harmonization  |
| **Hybrid**       | `output/example_hybrid_output.mid`  | 365 bytes   | 32 notes  | **Coconet → RL optimization** |

## 🎼 Harmonization Methods

### **RL-Only Harmonization**

- **Strengths**: Guaranteed melody preservation, full harmonization
- **Best for**: When melody preservation is critical
- **Output**: Complete 4-part chorale style

### **Coconet-Only Harmonization**

- **Strengths**: Neural creativity, concise output
- **Best for**: When you want neural network innovation
- **Output**: Modern, creative harmonization

### **Hybrid Harmonization (Recommended)**

- **Strengths**: Combines best of both worlds, optimized output
- **Best for**: Production use, contrary motion focus
- **Output**: Optimized, music-theory compliant harmonization

## 🔧 Scripts

### `generate_example_midi.py`

Generates example MIDI files using the hybrid harmonization system API.

**Features:**

- Tests all three harmonization methods (RL, Coconet, Hybrid)
- Uses `realms2_harmonized.mid` as input melody
- Saves output files to `examples/output/`
- Provides detailed progress and error reporting

**Usage:**

```bash
python3 examples/generate_example_midi.py
```

### `analyze_example_midis.py`

Analyzes generated MIDI files and provides detailed statistics.

**Features:**

- Detailed analysis of each MIDI file
- Voice distribution analysis
- File size and note count comparisons
- Musical characteristics breakdown

**Usage:**

```bash
python3 examples/analyze_example_midis.py
```

## 📈 Performance Comparison

The example files demonstrate the system's capabilities:

- **RL-Only**: 304 notes, 2,817 bytes - Full harmonization
- **Coconet-Only**: 36 notes, 405 bytes - Neural approach
- **Hybrid**: 32 notes, 365 bytes - Optimized approach

## 🎯 Key Insights

1. **Hybrid approach produces the most efficient output**
2. **All methods successfully create 4-part harmonizations**
3. **Voice ranges are properly distributed across SATB**
4. **File sizes reflect the complexity of each approach**

## 📚 Related Documentation

- [Main System Documentation](../docs/HYBRID_SYSTEM_SUMMARY.md)
- [Example MIDI Demonstration](../docs/EXAMPLE_MIDI_DEMONSTRATION.md)
- [API Documentation](../coconet-server/hybrid_harmonization_server.py)

---

**Status**: ✅ **Ready to use**  
**Last Updated**: July 22, 2024
