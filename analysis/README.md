# Analysis Tools for RL_HARMONIZATION

This directory contains analysis scripts for evaluating and comparing harmonization outputs from the RL_HARMONIZATION system.

## 📊 **Analysis Files Overview**

### **Core Harmonization Analysis**

#### **Final Results Analysis**

- `analyze_final_harmonizations.py` - Analyze final harmonization outputs for melody preservation
- `analyze_final_hybrid.py` - Analyze hybrid system final outputs
- `analyze_proper_solution.py` - Analyze proper harmonization solutions
- `analyze_proper_harmonization.py` - Analyze proper harmonization outputs

#### **System Performance Analysis**

- `analyze_hybrid_harmonization.py` - Analyze hybrid system performance
- `analyze_enhanced_harmonizations.py` - Analyze enhanced harmonization outputs
- `analyze_new_harmonizations.py` - Analyze new harmonization results
- `analyze_new_proper_harmonizations.py` - Analyze new proper harmonizations

#### **Melody Preservation Analysis**

- `analyze_melody_preserved_harmonization.py` - Analyze melody preservation in harmonizations
- `analyze_enhanced_melody_preservation.py` - Analyze enhanced melody preservation
- `analyze_melody_content.py` - Analyze melody content and structure

### **System Integration Analysis**

#### **Coconet Integration**

- `analyze_real_coconet_output.py` - Analyze real Coconet model outputs
- `analyze_docker_output.py` - Analyze Docker container outputs
- `analyze_corrected_harmonization.py` - Analyze corrected harmonization results

#### **Training and Development**

- `analyze_training.py` - Analyze training process and results
- `analyze_realms_harmonization.py` - Analyze Realms melody harmonizations
- `analyze_full_harmonization.py` - Analyze complete harmonization outputs

#### **Comprehensive Analysis**

- `analyze_all_fixed_harmonizations.py` - Comprehensive analysis of all fixed harmonizations
- `analyze_example_midis.py` - Analyze example MIDI files

## 🚀 **Running Analysis Scripts**

### **Individual Analysis**

```bash
# Analyze final harmonizations
python3 analysis/analyze_final_harmonizations.py

# Analyze hybrid system performance
python3 analysis/analyze_hybrid_harmonization.py

# Analyze melody preservation
python3 analysis/analyze_melody_preserved_harmonization.py

# Analyze Docker outputs
python3 analysis/analyze_docker_output.py
```

### **Batch Analysis**

```bash
# Run all analysis scripts
for script in analysis/*.py; do
    if [[ $script != *"__init__.py"* ]]; then
        echo "Running $script..."
        python3 "$script"
        echo "---"
    fi
done
```

## 📋 **Analysis Categories**

### **Quality Assessment**

- **Melody Preservation**: Check if original melody is maintained
- **Harmonic Quality**: Evaluate harmonic coherence and voice leading
- **Musical Structure**: Analyze timing, rhythm, and form
- **Technical Metrics**: File size, note count, pitch distribution

### **System Comparison**

- **Coconet vs RL**: Compare neural network vs reinforcement learning outputs
- **Hybrid Performance**: Evaluate combined system effectiveness
- **Version Comparison**: Compare different system versions
- **Parameter Impact**: Analyze effect of different parameters

### **Performance Metrics**

- **Processing Time**: Measure system performance
- **Output Quality**: Assess musical quality
- **Consistency**: Check output reliability
- **Scalability**: Evaluate system scalability

## 🔧 **Analysis Dependencies**

### **Required Packages**

- `pretty_midi` - MIDI file processing and analysis
- `numpy` - Numerical computations and statistics
- `matplotlib` - Data visualization (optional)
- `pandas` - Data analysis (optional)

### **Input Files**

- MIDI files from `../midi_files/` directory
- Training logs and model outputs
- System configuration files

## 📊 **Analysis Outputs**

### **Text Reports**

- Detailed analysis of harmonization quality
- Comparison metrics between different approaches
- Performance statistics and recommendations

### **Visualizations** (if matplotlib is available)

- Pitch distribution plots
- Timing analysis charts
- Quality comparison graphs

### **Metrics**

- Melody preservation percentage
- Harmonic coherence scores
- Technical quality indicators
- Performance benchmarks

## 🎯 **Key Analysis Features**

### **Melody Preservation Analysis**

- ✅ **Pitch Matching**: Compare original vs harmonized melody pitches
- ✅ **Timing Analysis**: Check rhythm and timing preservation
- ✅ **Audibility Check**: Ensure melody is prominent in output
- ✅ **Structure Validation**: Verify musical form preservation

### **Harmonic Quality Assessment**

- ✅ **Voice Leading**: Analyze smoothness of voice movements
- ✅ **Chord Progressions**: Evaluate harmonic coherence
- ✅ **Contrary Motion**: Check for optimal voice movement
- ✅ **Range Compliance**: Verify voice range constraints

### **System Performance Evaluation**

- ✅ **Processing Speed**: Measure generation time
- ✅ **Output Consistency**: Check reliability across runs
- ✅ **Resource Usage**: Monitor memory and CPU usage
- ✅ **Scalability**: Test with different input sizes

## 🔍 **Analysis Workflow**

### **1. Data Collection**

- Gather harmonization outputs from different methods
- Collect training logs and performance metrics
- Organize files by system version and parameters

### **2. Quality Assessment**

- Run melody preservation analysis
- Evaluate harmonic quality metrics
- Assess musical structure and coherence

### **3. Comparison Analysis**

- Compare different system approaches
- Analyze parameter impact on quality
- Evaluate version improvements

### **4. Performance Evaluation**

- Measure processing speed and efficiency
- Assess resource usage and scalability
- Identify optimization opportunities

### **5. Reporting**

- Generate comprehensive analysis reports
- Create visualizations and summaries
- Provide recommendations for improvement

## 📈 **Analysis Results**

The analysis tools provide insights into:

- **System Effectiveness**: How well each approach performs
- **Quality Metrics**: Musical quality and technical performance
- **Improvement Areas**: Opportunities for system enhancement
- **Best Practices**: Optimal parameters and configurations

## 🔄 **Adding New Analysis**

When adding new analysis scripts:

1. Place them in the `analysis/` directory
2. Use descriptive names starting with `analyze_`
3. Include proper path references to `../midi_files/`
4. Add documentation in this README
5. Follow the existing analysis patterns

---

**Total Analysis Files**: 19  
**Coverage**: Comprehensive system evaluation and quality assessment  
**Status**: ✅ All analysis files organized and paths fixed
