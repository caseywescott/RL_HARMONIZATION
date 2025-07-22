# N-Part Harmonization with Reinforcement Learning

## Project Objective

This project aims to extend the work from "Tuning Recurrent Networks with Reinforcement Learning" (Magenta, 2016) to create an n-part automatic harmonization model using reinforcement learning. The goal is to develop a system that can generate harmonically coherent multi-part compositions by learning to balance various musical rules through reward-based learning rather than strict rule enforcement.

## Background and Motivation

### Key Papers and References

1. **"Tuning Recurrent Networks with Reinforcement Learning"** (Magenta, 2016)

   - Demonstrates how RL can be used to improve sequence generation
   - Shows that reward-based learning can produce better musical outputs than supervised learning alone

2. **"Style Modeling for N-Part Automatic Harmonization"** (Your Paper)

   - Focuses on n-part harmonization challenges
   - Introduces metrics for evaluating harmonic quality (Figure 2)
   - Provides framework for multi-part composition

3. **Coconet (Counterpoint by Convolution)** - Anna Huang et al.

   - Bach Doodle algorithm implementation
   - Uses convolutional networks for counterpoint generation
   - Available at: g.co/magenta/coconet
   - **Selected as our base model** for its superior harmony generation capabilities

4. **Previous RL Counterpoint Project**
   - Successfully used RL to reward models for following counterpoint rules
   - Demonstrated that RL can blend rules intelligently without strict enforcement
   - Focused on harmonic leaps and other counterpoint principles

## Core Innovation

The key insight is that **reinforcement learning allows the model to learn to blend musical rules together in clever ways without being forced to follow all rules simultaneously**. The rules are enforced through reward signals rather than hard constraints, enabling more natural and musically satisfying outputs.

**Our Approach**: We will wrap the pre-trained Coconet model in an RL environment, allowing us to leverage its sophisticated harmony generation while adding tunable music theory rewards.

## Technical Approach

### 1. Model Architecture

**Base Model: Coconet (Counterpoint by Convolution)**

- **Architecture**: 64-layer CNN with 128 filters
- **Training Data**: JSB Chorales (Bach 4-part harmony)
- **Output**: 4-part polyphonic harmony
- **Advantages**: Pre-trained on high-quality classical harmony, modern CNN architecture

**Architecture Components:**

```
Input: Melody line or chord progression
↓
Coconet Encoder: Process input musical features
↓
Coconet Decoder: Generate 4-part harmonization
↓
RL Agent: Evaluate and reward outputs with tunable weights
↓
Output: Harmonized n-part composition
```

### 2. Reinforcement Learning Framework

**State Space:**

- Current musical context (recent notes, harmonic context)
- Generated notes for each part so far
- Musical features (key, time signature, etc.)
- Coconet's internal representation

**Action Space:**

- Note selection for each part (from Coconet's output distribution)
- Duration and articulation choices
- Harmonic progression decisions

**Reward Function:**
Based on the metrics from Figure 2 of your paper, the reward function should evaluate:

1. **Harmonic Coherence** (Tunable Weight: 0.2-0.4)

   - Chord quality and progression
   - Voice leading smoothness
   - Harmonic tension and resolution

2. **Counterpoint Rules** (Tunable Weight: 0.1-0.3)

   - Parallel motion avoidance
   - Proper voice spacing
   - Harmonic leaps management

3. **Musical Interest** (Tunable Weight: 0.2-0.4)

   - Melodic interest in each part
   - Rhythmic variety
   - Overall musical flow

4. **Style Consistency** (Tunable Weight: 0.1-0.3)
   - Adherence to target musical style
   - Historical accuracy (if applicable)
   - Genre-specific characteristics

### 3. Training Methodology

**Phase 1: Coconet Integration**

- Load pre-trained Coconet model (64 layers, 128 filters)
- Create RL wrapper around Coconet
- Implement basic reward function

**Phase 2: RL Fine-tuning**

- Use Coconet as starting point
- Apply RL with tunable reward function
- Gradually improve rule blending and musical quality

**Phase 3: Style Adaptation**

- Fine-tune for specific musical styles or composers
- Adapt reward weights for different aesthetic preferences
- Generate style-specific harmonizations

### 4. Tunable Reward Function Design

The reward function is a weighted combination of multiple musical metrics with adjustable weights:

```python
def calculate_harmony_reward(harmony_context, next_chord, weights):
    reward = 0.0

    # Harmonic coherence (staying in key)
    reward += weights['harmonic_coherence'] * check_harmonic_coherence(next_chord)

    # Voice leading (smooth transitions)
    reward += weights['voice_leading'] * check_voice_leading(harmony_context, next_chord)

    # Counterpoint rules
    reward += weights['counterpoint'] * check_counterpoint_rules(harmony_context, next_chord)

    # Musical interest (avoiding repetition)
    reward += weights['musical_interest'] * check_musical_interest(harmony_context, next_chord)

    # Style consistency
    reward += weights['style_consistency'] * check_style_consistency(next_chord)

    return reward

# Predefined style presets
STYLE_PRESETS = {
    'classical': {
        'harmonic_coherence': 0.3,
        'voice_leading': 0.25,
        'counterpoint': 0.25,
        'musical_interest': 0.1,
        'style_consistency': 0.1
    },
    'jazz': {
        'harmonic_coherence': 0.2,
        'voice_leading': 0.15,
        'counterpoint': 0.1,
        'musical_interest': 0.35,
        'style_consistency': 0.2
    },
    'pop': {
        'harmonic_coherence': 0.4,
        'voice_leading': 0.1,
        'counterpoint': 0.05,
        'musical_interest': 0.25,
        'style_consistency': 0.2
    }
}
```

## Implementation Plan

### Phase 1: Foundation (Weeks 1-4)

1. **Coconet Integration**

   - Set up Coconet model with pre-trained weights
   - Create RL environment wrapper
   - Implement basic reward function

2. **Data Preparation**
   - Collect n-part harmonization datasets
   - Preprocess musical data for training
   - Create evaluation metrics based on Figure 2

### Phase 2: RL Integration (Weeks 5-8)

1. **Tunable Reward Function Implementation**

   - Implement metrics from Figure 2
   - Create weighted reward system with adjustable weights
   - Design style presets (classical, jazz, pop)

2. **RL Training Pipeline**
   - Integrate with existing RL frameworks (e.g., Stable Baselines3)
   - Implement custom environment for musical generation
   - Set up training and evaluation loops

### Phase 3: Optimization (Weeks 9-12)

1. **Hyperparameter Tuning**

   - Optimize reward weights for different styles
   - Fine-tune model architecture
   - Balance exploration vs. exploitation

2. **Evaluation and Validation**
   - Compare against baseline models
   - Evaluate musical quality through expert review
   - Measure improvement in rule adherence

## Expected Benefits

1. **Flexible Rule Application**: RL allows the model to learn when to break rules for musical effect
2. **Natural Blending**: Rules are integrated organically rather than enforced rigidly
3. **Style Adaptation**: Easy adaptation to different musical styles and preferences
4. **Quality Improvement**: Better musical outputs through reward-based learning
5. **Scalability**: Framework can be extended to other musical tasks
6. **High-Quality Base**: Coconet's pre-trained harmony knowledge provides excellent foundation

## Technical Challenges and Solutions

### Challenge 1: Reward Function Design

**Solution**: Start with simple metrics and gradually increase complexity. Use expert feedback to validate reward function effectiveness.

### Challenge 2: Coconet-RL Integration

**Solution**: Create wrapper that preserves Coconet's sophisticated harmony generation while adding RL-based optimization.

### Challenge 3: Tunable Weights

**Solution**: Implement style presets and allow real-time weight adjustment for different musical preferences.
