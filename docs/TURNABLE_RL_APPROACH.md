# 🎛️ Tunable RL Harmonization Approach

## 📋 **Overview**

This implementation provides a **tunable reinforcement learning harmonization system** that allows dynamic adjustment of music theory rule weights, similar to the approach shown in Figure 2 of "Style Modeling for N-Part Automatic Harmonization". The system enables real-time control over harmonization characteristics such as contrary motion vs parallel motion, consonance vs dissonance, and voice leading preferences.

## 🎯 **Key Features**

### **Dynamic Weight Adjustment**

- **Real-time tuning** of music theory rule weights
- **Style presets** for classical, jazz, pop, and baroque
- **Custom weight configurations** for specific musical goals
- **Controllable motion types** (contrary, parallel, oblique)

### **Music Theory Rules**

- **Motion Analysis**: Contrary, parallel, and oblique motion detection
- **Harmonic Rules**: Consonance, dissonance, chord progression quality
- **Voice Leading**: Smooth voice movement, voice crossing prevention
- **Advanced Rules**: Suspensions, passing tones, neighbor tones

### **Training Capabilities**

- **Multi-configuration training** with different weight sets
- **Performance comparison** across different rule configurations
- **Motion statistics analysis** for each trained model
- **Visualization** of training results and motion patterns

## 🏗️ **Architecture**

### **Core Components**

```
TunableMusicTheoryRewards
├── Dynamic weight management
├── Rule calculation methods
├── Style presets
└── Total reward computation

TunableRLHarmonizer
├── Q-learning implementation
├── State-action management
├── Weight application
└── Model persistence

TunableRLTrainer
├── Multi-configuration training
├── Performance analysis
├── Result visualization
└── Model comparison
```

### **Training Pipeline**

```
1. Define Rule Configurations
   ├── High contrary motion
   ├── High parallel motion
   ├── Balanced approach
   ├── High consonance
   ├── High dissonance
   ├── Voice leading focused
   └── Chord progression focused

2. Train Each Configuration
   ├── Initialize RL model with weights
   ├── Generate harmonizations
   ├── Calculate rewards
   ├── Update Q-values
   └── Track motion statistics

3. Analyze Results
   ├── Compare performance metrics
   ├── Analyze motion patterns
   ├── Identify best configurations
   └── Generate visualizations
```

## 🎼 **Music Theory Rules Implementation**

### **Motion Types**

#### **Contrary Motion**

```python
def calculate_contrary_motion_reward(self, melody_notes, harmony_notes):
    # Detect when melody and harmony move in opposite directions
    # Reward: contrary_motion_weight * (contrary_motions / total_motions)
```

#### **Parallel Motion**

```python
def calculate_parallel_motion_reward(self, melody_notes, harmony_notes):
    # Detect when melody and harmony move in same direction
    # Usually penalized in classical music
    # Reward: parallel_motion_weight * (parallel_motions / total_motions)
```

#### **Oblique Motion**

```python
# Detect when one voice moves while the other stays stationary
# Moderate reward for variety
```

### **Harmonic Rules**

#### **Consonance/Dissonance**

```python
def calculate_consonance_reward(self, melody_note, harmony_note):
    interval = abs(melody_note - harmony_note) % 12

    # Consonant intervals: unison, thirds, fourths, fifths, sixths
    if interval in [0, 3, 4, 7, 8]:
        return consonance_weight

    # Dissonant intervals: seconds, tritone, sevenths
    elif interval in [1, 2, 5, 6, 9, 10, 11]:
        return dissonance_weight
```

#### **Chord Progression Quality**

```python
def calculate_chord_progression_reward(self, chord_notes):
    # Analyze intervals within chord
    # Count consonant vs dissonant intervals
    # Reward based on overall chord quality
```

### **Voice Leading**

#### **Smooth Voice Movement**

```python
def calculate_voice_leading_reward(self, prev_harmony, current_harmony):
    interval = abs(current_harmony - prev_harmony)

    # Prefer small intervals (stepwise motion)
    if interval <= 2:
        return voice_leading_weight
    elif interval <= 4:
        return voice_leading_weight * 0.7
    # ... decreasing rewards for larger intervals
```

## 🎛️ **Weight Configurations**

### **Style Presets**

#### **Classical Style**

```python
'classical': {
    'contrary_motion': 1.2,      # High preference for contrary motion
    'parallel_motion': 0.2,      # Low tolerance for parallel motion
    'consonance': 1.1,           # Strong preference for consonance
    'voice_leading': 1.0,        # Balanced voice leading
    'chord_progression': 0.9,    # Good chord progressions
    'harmonic_complexity': 0.7   # Moderate complexity
}
```

#### **Jazz Style**

```python
'jazz': {
    'contrary_motion': 0.8,      # Moderate contrary motion
    'parallel_motion': 0.6,      # Higher tolerance for parallel motion
    'consonance': 0.7,           # Lower consonance requirement
    'dissonance': 0.8,           # Higher tolerance for dissonance
    'harmonic_complexity': 1.2,  # High complexity
    'melodic_interest': 1.1      # High melodic interest
}
```

#### **Pop Style**

```python
'pop': {
    'contrary_motion': 0.5,      # Low contrary motion preference
    'parallel_motion': 0.8,      # High tolerance for parallel motion
    'consonance': 1.0,           # Standard consonance
    'chord_progression': 1.1,    # Strong chord progressions
    'harmonic_complexity': 0.4,  # Low complexity
    'melodic_interest': 0.8      # Moderate melodic interest
}
```

### **Custom Configurations**

#### **High Contrary Motion**

```python
'high_contrary': {
    'contrary_motion': 2.0,      # Very high contrary motion preference
    'parallel_motion': 0.1,      # Very low parallel motion tolerance
    'oblique_motion': 0.8,       # Moderate oblique motion
    'consonance': 1.0,           # Standard consonance
    'voice_leading': 0.9,        # Good voice leading
    'chord_progression': 0.8     # Moderate chord progression focus
}
```

#### **High Parallel Motion**

```python
'high_parallel': {
    'contrary_motion': 0.2,      # Very low contrary motion preference
    'parallel_motion': 1.5,      # Very high parallel motion tolerance
    'oblique_motion': 0.6,       # Moderate oblique motion
    'consonance': 1.0,           # Standard consonance
    'voice_leading': 0.7,        # Moderate voice leading
    'chord_progression': 0.9     # Strong chord progression focus
}
```

## 📊 **Training and Analysis**

### **Training Process**

1. **Configuration Definition**: Define different weight sets for various musical goals
2. **Model Training**: Train separate RL models for each configuration
3. **Performance Tracking**: Monitor rewards, motion statistics, and learning curves
4. **Result Analysis**: Compare performance across configurations
5. **Visualization**: Generate charts and graphs for analysis

### **Analysis Metrics**

#### **Performance Metrics**

- **Average Reward**: Overall harmonization quality
- **Best Reward**: Peak performance achieved
- **Learning Stability**: Consistency of improvement

#### **Motion Statistics**

- **Contrary Motion Ratio**: Percentage of contrary motions
- **Parallel Motion Ratio**: Percentage of parallel motions
- **Oblique Motion Ratio**: Percentage of oblique motions

#### **Quality Metrics**

- **Consonance Rate**: Percentage of consonant intervals
- **Voice Leading Quality**: Average voice movement smoothness
- **Chord Progression Quality**: Overall harmonic coherence

## 🔄 **Comparison with Figure 2 of the Paper**

### **Similarities**

1. **Dynamic Weight Adjustment**: Both approaches allow real-time tuning of music theory rule weights
2. **Multi-Configuration Training**: Training multiple models with different weight sets
3. **Performance Comparison**: Analyzing results across different configurations
4. **Style-Specific Behavior**: Adapting harmonization behavior based on musical style

### **Key Differences**

1. **Implementation**: Our approach uses Q-learning vs. the paper's specific method
2. **Rule Set**: Our implementation includes additional rules beyond the paper's scope
3. **Training Data**: We use diverse melody sets vs. the paper's specific dataset
4. **Analysis**: Our approach includes motion statistics and visualization

### **Advantages of Our Approach**

1. **Real-time Tuning**: Immediate weight adjustment without retraining
2. **Comprehensive Rules**: More extensive music theory rule set
3. **Visual Analysis**: Built-in visualization and analysis tools
4. **Modular Design**: Easy to extend with new rules and configurations

## 🚀 **Usage Examples**

### **Basic Usage**

```python
from tunable_rl_harmonizer import create_tunable_harmonizer

# Create harmonizer
harmonizer = create_tunable_harmonizer()

# Set style
harmonizer.set_style('classical')

# Generate harmonization
melody = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
harmony = harmonizer.generate_harmonization(melody)
```

### **Custom Weights**

```python
# Define custom weights
custom_weights = {
    'contrary_motion': 2.0,
    'parallel_motion': 0.1,
    'consonance': 1.0
}

# Generate harmonization with custom weights
harmony = harmonizer.generate_harmonization(melody, custom_weights=custom_weights)
```

### **Training Multiple Configurations**

```python
from train_tunable_rl_model import TunableRLTrainer

# Create trainer
trainer = TunableRLTrainer()

# Train all configurations
results, models = trainer.train_all_configurations(episodes_per_config=3000)

# Analyze results
trainer.analyze_results(results)
```

## 📈 **Expected Results**

### **High Contrary Motion Configuration**

- **Contrary Motion Ratio**: 70-80%
- **Parallel Motion Ratio**: 10-20%
- **Musical Character**: Classical, contrapuntal style

### **High Parallel Motion Configuration**

- **Contrary Motion Ratio**: 20-30%
- **Parallel Motion Ratio**: 60-70%
- **Musical Character**: Pop, homophonic style

### **Balanced Configuration**

- **Contrary Motion Ratio**: 40-50%
- **Parallel Motion Ratio**: 30-40%
- **Musical Character**: Versatile, adaptable style

## 🎯 **Future Enhancements**

1. **Advanced Rules**: Add more sophisticated music theory rules
2. **Neural Integration**: Combine with neural network approaches
3. **Real-time Performance**: Optimize for live performance use
4. **User Interface**: Create GUI for weight adjustment
5. **MIDI Integration**: Direct MIDI file processing and output

## 📚 **References**

- "Style Modeling for N-Part Automatic Harmonization" - Figure 2 methodology
- Music theory principles for harmonization
- Reinforcement learning in music generation
- Q-learning for sequential decision making

---

**Status**: ✅ **IMPLEMENTED AND TESTED**
**Version**: 1.0
**Last Updated**: July 22, 2024
