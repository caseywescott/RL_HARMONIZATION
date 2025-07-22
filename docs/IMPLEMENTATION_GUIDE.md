# N-Part Harmonization Implementation Guide

_Best Practices for Sequential Development with Coconet + RL_

## Project Structure

```
RL_HARMONIZATION/
├── src/harmonization/
│   ├── core/           # Coconet integration and RL wrapper
│   ├── rewards/        # Tunable reward functions
│   ├── evaluation/     # Evaluation metrics
│   └── data/          # Data processing
├── coconet-64layers-128filters/  # Pre-trained Coconet model
├── configs/           # Configuration files and style presets
├── notebooks/         # Jupyter notebooks
├── scripts/          # Training/evaluation scripts
└── tests/            # Test suite
```

## Phase 1: Coconet Integration and RL Wrapper (Weeks 1-3)

### Week 1: Environment Setup and Coconet Integration

**Day 1-2: Project Setup**

```bash
# Create structure and install dependencies
mkdir -p src/harmonization/{core,rewards,evaluation,data}
pip install stable-baselines3 gym optuna tensorflow note-seq
```

**Day 3-4: Coconet Model Loading**

```python
# src/harmonization/core/coconet_loader.py
class CoconetLoader:
    def __init__(self, checkpoint_dir="coconet-64layers-128filters"):
        self.checkpoint_dir = checkpoint_dir
        self.model = self.load_coconet_model()

    def load_coconet_model(self):
        """Load pre-trained Coconet model"""
        # Load the 64-layer, 128-filter Coconet model
        # trained on JSB Chorales
        pass

    def generate_harmony(self, input_sequence, temperature=1.0):
        """Generate 4-part harmony using Coconet"""
        pass
```

**Day 5-7: RL Environment Wrapper**

```python
# src/harmonization/core/rl_wrapper.py
class CoconetRLWrapper:
    def __init__(self, coconet_model, reward_weights):
        self.coconet = coconet_model
        self.reward_weights = reward_weights
        self.state_space = self.define_state_space()
        self.action_space = self.define_action_space()

    def define_state_space(self):
        """Define state space including Coconet's internal representation"""
        pass

    def define_action_space(self):
        """Define action space from Coconet's output distribution"""
        pass
```

### Week 2: Tunable Reward System

**Day 1-2: Base Reward Framework**

```python
# src/harmonization/rewards/base_rewards.py
class TunableRewardSystem:
    def __init__(self, weights=None):
        self.weights = weights or self.get_default_weights()

    def get_default_weights(self):
        return {
            'harmonic_coherence': 0.3,
            'voice_leading': 0.25,
            'counterpoint': 0.25,
            'musical_interest': 0.1,
            'style_consistency': 0.1
        }

    def calculate_total_reward(self, harmony_context, next_chord):
        """Calculate total reward with tunable weights"""
        reward = 0.0
        reward += self.weights['harmonic_coherence'] * self.harmonic_coherence_score(next_chord)
        reward += self.weights['voice_leading'] * self.voice_leading_score(harmony_context, next_chord)
        reward += self.weights['counterpoint'] * self.counterpoint_score(harmony_context, next_chord)
        reward += self.weights['musical_interest'] * self.musical_interest_score(harmony_context, next_chord)
        reward += self.weights['style_consistency'] * self.style_consistency_score(next_chord)
        return reward
```

**Day 3-4: Style Presets**

```python
# src/harmonization/rewards/style_presets.py
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
    },
    'baroque': {
        'harmonic_coherence': 0.25,
        'voice_leading': 0.3,
        'counterpoint': 0.3,
        'musical_interest': 0.1,
        'style_consistency': 0.05
    }
}

class StyleManager:
    def get_weights(self, style_name):
        """Get reward weights for specific style"""
        return STYLE_PRESETS.get(style_name, STYLE_PRESETS['classical'])

    def create_custom_weights(self, **kwargs):
        """Create custom weight combination"""
        base_weights = STYLE_PRESETS['classical'].copy()
        base_weights.update(kwargs)
        return base_weights
```

**Day 5-7: Individual Reward Components**

```python
# src/harmonization/rewards/harmonic_rewards.py
class HarmonicRewards:
    def harmonic_coherence_score(self, chord):
        """Evaluate harmonic coherence (staying in key)"""
        # Check if chord fits current key
        # Evaluate chord quality (major, minor, diminished, augmented)
        # Analyze harmonic progression smoothness
        pass

# src/harmonization/rewards/voice_leading.py
class VoiceLeadingRewards:
    def voice_leading_score(self, harmony_context, next_chord):
        """Evaluate voice leading quality (smooth transitions)"""
        # Analyze step-wise motion
        # Check common tone retention
        # Avoid voice crossing
        pass

# src/harmonization/rewards/counterpoint.py
class CounterpointRewards:
    def counterpoint_score(self, harmony_context, next_chord):
        """Evaluate counterpoint adherence"""
        # Check parallel motion avoidance
        # Analyze harmonic interval quality
        # Evaluate melodic contour variety
        pass
```

### Week 3: RL Environment Development

**Day 1-3: Custom Gym Environment**

```python
# src/harmonization/environment/harmonization_env.py
class CoconetHarmonizationEnvironment(gym.Env):
    def __init__(self, coconet_model, reward_weights, sequence_length=32):
        self.coconet = coconet_model
        self.reward_system = TunableRewardSystem(reward_weights)
        self.sequence_length = sequence_length
        self.action_space = spaces.MultiDiscrete([38] * 4)  # 4 voices
        self.observation_space = spaces.Box(low=0, high=1, shape=(state_dim,))

    def step(self, action):
        # Apply action to current harmony
        self.current_harmony.append(action)

        # Calculate reward using tunable weights
        reward = self.reward_system.calculate_total_reward(
            self.harmony_context, action
        )

        # Check if episode is done
        done = self.current_step >= self.sequence_length

        return self.get_state(), reward, done, {}

    def reset(self):
        """Reset environment for new episode"""
        self.current_harmony = []
        self.current_step = 0
        return self.get_state()
```

**Day 4-7: Stable Baselines3 Integration**

```python
# src/harmonization/training/stable_baselines_integration.py
class CoconetHarmonizationTraining:
    def __init__(self, coconet_model, reward_weights, config):
        self.env = CoconetHarmonizationEnvironment(coconet_model, reward_weights)
        self.vec_env = DummyVecEnv([lambda: self.env])
        self.model = PPO("MlpPolicy", self.vec_env, **config)

    def train(self, total_timesteps, style_name=None):
        """Train with specific style weights"""
        if style_name:
            style_weights = StyleManager().get_weights(style_name)
            self.env.reward_system.weights = style_weights

        self.model.learn(total_timesteps=total_timesteps)
```

## Phase 2: Training and Optimization (Weeks 4-7)

### Week 4: Initial Training Pipeline

**Day 1-3: Training Pipeline**

```python
# scripts/train_coconet_rl.py
def main():
    # Load Coconet model
    coconet = CoconetLoader("coconet-64layers-128filters")

    # Set up training with classical style
    trainer = CoconetHarmonizationTraining(
        coconet_model=coconet.model,
        reward_weights=STYLE_PRESETS['classical']
    )

    # Train the model
    trainer.train(total_timesteps=1000000, output_dir='models/')
```

**Day 4-7: Multi-Style Training**

```python
# scripts/train_multiple_styles.py
def train_multiple_styles():
    coconet = CoconetLoader("coconet-64layers-128filters")

    for style_name in ['classical', 'jazz', 'pop', 'baroque']:
        print(f"Training {style_name} style...")
        trainer = CoconetHarmonizationTraining(
            coconet_model=coconet.model,
            reward_weights=STYLE_PRESETS[style_name]
        )
        trainer.train(total_timesteps=500000, output_dir=f'models/{style_name}/')
```

### Week 5: Validation and Evaluation

**Day 1-3: Validation Framework**

```python
# src/harmonization/evaluation/validation.py
class CoconetModelValidation:
    def validate_model(self, model, coconet_model, num_episodes=100):
        results = {
            'harmonic_coherence': [],
            'voice_leading': [],
            'counterpoint': [],
            'musical_interest': [],
            'overall_quality': []
        }

        for episode in range(num_episodes):
            # Generate harmony using RL-tuned model
            harmony = self.generate_harmony(model, coconet_model)

            # Evaluate each metric
            for metric_name in results.keys():
                score = self.evaluate_metric(harmony, metric_name)
                results[metric_name].append(score)

        return results
```

**Day 4-7: Style Comparison**

```python
# src/harmonization/evaluation/style_comparison.py
class StyleComparison:
    def compare_styles(self, models_dict, coconet_model):
        """Compare harmonization quality across different styles"""
        comparison_results = {}

        for style_name, model in models_dict.items():
            results = CoconetModelValidation().validate_model(
                model, coconet_model
            )
            comparison_results[style_name] = results

        return comparison_results
```

### Week 6: Hyperparameter Optimization

**Day 1-3: Weight Optimization**

```python
# src/harmonization/optimization/weight_optimization.py
class WeightOptimizer:
    def objective(self, trial):
        """Objective function for weight optimization"""
        weights = {
            'harmonic_coherence': trial.suggest_float('harmonic_coherence', 0.1, 0.5),
            'voice_leading': trial.suggest_float('voice_leading', 0.1, 0.4),
            'counterpoint': trial.suggest_float('counterpoint', 0.05, 0.4),
            'musical_interest': trial.suggest_float('musical_interest', 0.05, 0.4),
            'style_consistency': trial.suggest_float('style_consistency', 0.05, 0.3)
        }

        # Train model with these weights
        trainer = CoconetHarmonizationTraining(coconet_model, weights)
        trainer.train(total_timesteps=100000)

        # Evaluate model
        validation_score = self.evaluate_model(trainer.model)
        return validation_score

    def optimize_weights(self, n_trials=100):
        study = optuna.create_study(direction='maximize')
        study.optimize(self.objective, n_trials=n_trials)
        return study.best_params
```

**Day 4-7: Style-Specific Optimization**

```python
# src/harmonization/optimization/style_optimization.py
class StyleOptimizer:
    def optimize_style_weights(self, style_name, n_trials=50):
        """Optimize weights for specific musical style"""
        base_weights = STYLE_PRESETS[style_name]

        def objective(trial):
            # Perturb base weights
            weights = {}
            for key, base_value in base_weights.items():
                weights[key] = trial.suggest_float(
                    key,
                    max(0.05, base_value - 0.1),
                    min(0.5, base_value + 0.1)
                )

            # Train and evaluate
            trainer = CoconetHarmonizationTraining(coconet_model, weights)
            trainer.train(total_timesteps=200000)
            return self.evaluate_style_performance(trainer.model, style_name)

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials)
        return study.best_params
```
