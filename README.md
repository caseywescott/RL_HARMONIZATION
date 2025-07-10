# 🎵 N-Part Harmonization with Reinforcement Learning

An AI system that generates harmonically coherent multi-part compositions using Coconet and reinforcement learning with tunable music theory rewards.

## 🎯 Project Overview

This project extends the work from ["Tuning Recurrent Networks with Reinforcement Learning"](https://magenta.withgoogle.com/2016/11/09/tuning-recurrent-networks-with-reinforcement-learning) to create an n-part automatic harmonization system. Instead of generating single melodies, this system creates complete harmonizations (typically 2-4 parts) by learning to balance various musical rules through reward-based learning.

### Key Features

- **🎼 Multi-Part Harmonization**: Generate 2-4 part harmonies from melodies or chord progressions
- **🎛️ Tunable Rewards**: Adjust music theory rule weights for different styles (classical, jazz, pop, baroque)
- **🤖 RL Framework**: Uses Stable-Baselines3 with PPO for training
- **🎯 Coconet Integration**: Built on top of the pre-trained Coconet model
- **📊 Style Presets**: Pre-configured reward weights for different musical styles

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd RL_HARMONIZATION

# Install dependencies
make install

# Or manually:
pip3 install -r requirements.txt
```

### Basic Usage

```python
from src.harmonization import HarmonizationEnvironment, MusicTheoryRewards, CoconetWrapper

# Create components
coconet = CoconetWrapper("coconet-64layers-128filters")
rewards = MusicTheoryRewards()
rewards.set_style_preset('classical')  # or 'jazz', 'pop', 'baroque'

# Create environment
env = HarmonizationEnvironment(
    coconet_wrapper=coconet,
    reward_system=rewards,
    max_steps=32,
    num_voices=4
)

# Train an agent
from stable_baselines3 import PPO
agent = PPO("MlpPolicy", env, verbose=1)
agent.learn(total_timesteps=10000)

# Generate harmonization
obs = env.reset()
for step in range(32):
    action, _ = agent.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    if done:
        break

# Get final sequence
final_sequence = env.get_final_sequence()
```

### Training Different Styles

```python
# Train classical style
rewards.set_style_preset('classical')
env = HarmonizationEnvironment(coconet, rewards)
agent = PPO("MlpPolicy", env)
agent.learn(total_timesteps=10000)

# Train jazz style
rewards.set_style_preset('jazz')
env = HarmonizationEnvironment(coconet, rewards)
agent = PPO("MlpPolicy", env)
agent.learn(total_timesteps=10000)
```

## 📁 Project Structure

```
RL_HARMONIZATION/
├── src/harmonization/           # Main package
│   ├── core/                   # Core components
│   │   ├── coconet_wrapper.py  # Coconet model integration
│   │   └── rl_environment.py   # RL environment
│   ├── rewards/                # Reward functions
│   │   └── music_theory_rewards.py  # Tunable music theory rewards
│   └── evaluation/             # Evaluation metrics
├── coconet-64layers-128filters/ # Pre-trained Coconet model
├── train_harmonization.py      # Training script
├── test_implementation.py      # Test script
├── requirements.txt            # Dependencies
├── Makefile                    # Development tasks
└── README.md                   # This file
```

## 🎼 Music Theory Rewards

The system implements 21 different music theory reward functions, each with adjustable weights:

### Core Rewards

- **Avoid Repetition**: Penalizes immediate repetition of pitches/patterns
- **Prefer Arpeggios**: Rewards chord arpeggio patterns
- **Prefer Scale Degrees**: Rewards diatonic scale usage
- **Prefer Tonic**: Rewards emphasis on tonic notes
- **Prefer Leading Tone**: Rewards leading tone resolution

### Harmonic Rewards

- **Prefer Resolution**: Rewards dissonance-to-consonance resolution
- **Prefer Common Chords**: Rewards common chord types (triads, sevenths)
- **Prefer Common Progressions**: Rewards common chord progressions
- **Prefer Voice Leading**: Rewards smooth voice leading
- **Prefer Harmony**: Combined harmonic coherence

### Rhythmic Rewards

- **Prefer Strong Beats**: Rewards emphasis on strong beats
- **Prefer Weak Beats**: Rewards appropriate weak beat treatment
- **Prefer Common Rhythms**: Rewards common rhythmic patterns
- **Prefer Common Durations**: Rewards common note values

### Style Rewards

- **Prefer Common Pitches**: Rewards commonly used pitches
- **Prefer Common Intervals**: Rewards common melodic intervals
- **Prefer Counterpoint**: Rewards good counterpoint rules
- **Prefer Form**: Rewards formal coherence
- **Prefer Style**: Combined style consistency

## 🎛️ Style Presets

### Classical

- Emphasizes: Common chords, progressions, voice leading, harmony, counterpoint
- Weights: Balanced approach to traditional harmony

### Jazz

- Emphasizes: Arpeggios, common pitches, intervals, chords, progressions
- Weights: Focus on chord-based improvisation

### Pop

- Emphasizes: Common pitches, chords, progressions, rhythms
- Weights: Simple, accessible harmony

### Baroque

- Emphasizes: Counterpoint, voice leading, harmony, form
- Weights: Complex polyphonic textures

## 🛠️ Development

### Running Tests

```bash
make test
# or
python3 test_implementation.py
```

### Training Agents

```bash
make train
# or
python3 train_harmonization.py
```

### Code Quality

```bash
make lint      # Run linting
make format    # Format code
make clean     # Clean generated files
```

### Full Setup

```bash
make setup     # Install, format, lint, and test
```

## 📊 Customizing Rewards

### Setting Custom Weights

```python
rewards = MusicTheoryRewards()

# Set custom weights
custom_weights = {
    'prefer_common_chords': 0.5,
    'prefer_arpeggios': 0.3,
    'prefer_voice_leading': 0.2
}
rewards.set_custom_weights(custom_weights)
```

### Creating New Style Presets

```python
# Add to style_presets in MusicTheoryRewards
self.style_presets['romantic'] = {
    'prefer_common_chords': 0.3,
    'prefer_arpeggios': 0.4,
    'prefer_common_intervals': 0.3
}
```

## 🎯 Advanced Usage

### Multi-Style Training

```python
# Train multiple styles and compare
styles = ['classical', 'jazz', 'pop', 'baroque']
agents = {}

for style in styles:
    rewards.set_style_preset(style)
    env = HarmonizationEnvironment(coconet, rewards)
    agent = PPO("MlpPolicy", env)
    agent.learn(total_timesteps=10000)
    agents[style] = agent
```

### Real-Time Harmonization

```python
# Generate harmonization in real-time
def harmonize_melody(melody_sequence, style='classical'):
    rewards.set_style_preset(style)
    env = HarmonizationEnvironment(coconet, rewards)

    # Set melody as primer
    env.current_sequence = melody_sequence

    # Generate harmonization
    obs = env._get_observation()
    for step in range(32):
        action, _ = agent.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        if done:
            break

    return env.get_final_sequence()
```

## 📈 Evaluation Metrics

The system tracks various metrics during training:

- **Total Reward**: Sum of all rewards in episode
- **Average Reward**: Mean reward per step
- **Style Consistency**: How well the output matches the target style
- **Harmonic Coherence**: Quality of harmonic structure
- **Voice Leading**: Smoothness of voice movements

## 🔧 Configuration

### Environment Parameters

- `max_steps`: Maximum steps per episode (default: 32)
- `num_voices`: Number of voices in harmonization (default: 4)
- `temperature`: Sampling temperature for Coconet (default: 1.0)

### Training Parameters

- `total_timesteps`: Total training steps (default: 10000)
- `learning_rate`: PPO learning rate (default: 3e-4)
- `batch_size`: Training batch size (default: 64)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run `make test` to ensure everything works
6. Submit a pull request

## 📚 References

- [Tuning Recurrent Networks with Reinforcement Learning](https://magenta.withgoogle.com/2016/11/09/tuning-recurrent-networks-with-reinforcement-learning)
- [Coconet: A Neural Network for Music Generation](https://arxiv.org/abs/1703.10847)
- [Stable-Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Magenta team for the original RL Tuner work
- The Coconet research team
- The Stable-Baselines3 community

---

**🎵 Happy Harmonizing!**
