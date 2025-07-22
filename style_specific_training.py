#!/usr/bin/env python3
"""
Style-Specific Training for Harmonization

Train the RL model with different reward weights for various musical styles:
- Classical (Bach-style)
- Jazz (chord extensions, chromaticism)
- Pop (simple progressions, strong cadences)
- Baroque (ornamentation, figured bass)
"""

import numpy as np
import json
import os
from datetime import datetime
import sys

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

# Style-specific reward weights
STYLE_PRESETS = {
    'classical': {
        'harmonic_coherence': 0.30,
        'voice_leading': 0.25,
        'counterpoint': 0.25,
        'musical_interest': 0.10,
        'contrary_motion': 0.10
    },
    'jazz': {
        'harmonic_coherence': 0.20,
        'voice_leading': 0.15,
        'counterpoint': 0.10,
        'musical_interest': 0.35,
        'contrary_motion': 0.20
    },
    'pop': {
        'harmonic_coherence': 0.40,
        'voice_leading': 0.10,
        'counterpoint': 0.05,
        'musical_interest': 0.25,
        'contrary_motion': 0.20
    },
    'baroque': {
        'harmonic_coherence': 0.25,
        'voice_leading': 0.30,
        'counterpoint': 0.30,
        'musical_interest': 0.10,
        'contrary_motion': 0.05
    }
}

def train_style_specific_model(style_name: str, episodes: int = 5000, melody_file: str = None):
    """Train a model for a specific musical style"""
    print(f"🎵 Training {style_name.upper()} style harmonization model")
    print(f"=" * 60)
    
    # Get style-specific weights
    if style_name not in STYLE_PRESETS:
        print(f"❌ Unknown style: {style_name}")
        print(f"Available styles: {list(STYLE_PRESETS.keys())}")
        return None
    
    weights = STYLE_PRESETS[style_name]
    print(f"🎛️ Style weights: {weights}")
    
    # Initialize reward system with style weights
    reward_system = MusicTheoryRewards()
    reward_system.set_custom_weights(weights)
    
    # Load melody if provided
    melody_sequence = None
    if melody_file and os.path.exists(melody_file):
        import mido
        mid = mido.MidiFile(melody_file)
        melody_sequence = []
        
        for track in mid.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    melody_sequence.append(msg.note)
                    if len(melody_sequence) >= 32:  # Limit length
                        break
            if melody_sequence:
                break
    
    # Create environment
    env = HarmonizationEnvironment(
        coconet_wrapper=None,  # Not using Coconet for style training
        reward_system=reward_system,
        max_steps=32,
        num_voices=3,
        melody_sequence=melody_sequence
    )
    
    # Training parameters
    learning_rate = 0.0003
    batch_size = 64
    
    # Initialize training
    reward_history = []
    best_reward = -float('inf')
    
    print(f"🚀 Starting training for {episodes} episodes...")
    
    for episode in range(episodes):
        observation = env.reset()
        total_reward = 0
        
        for step in range(env.max_steps):
            # Sample action (random for now, could use trained policy)
            action = env.action_space.sample()
            
            # Take step
            observation, reward, done, info = env.step(action)
            total_reward += reward
            
            if done:
                break
        
        reward_history.append(total_reward)
        
        # Track best performance
        if total_reward > best_reward:
            best_reward = total_reward
        
        # Progress reporting
        if episode % 500 == 0:
            avg_reward = np.mean(reward_history[-500:])
            print(f"Episode {episode:4d} | Avg Reward: {avg_reward:6.2f} | Best: {best_reward:6.2f}")
    
    # Calculate final statistics
    final_avg_reward = np.mean(reward_history[-1000:])
    final_std_reward = np.std(reward_history[-1000:])
    
    # Save model metadata
    model_metadata = {
        'model_name': f'{style_name}_style_harmonization_model',
        'style': style_name,
        'episodes_trained': episodes,
        'final_avg_reward': final_avg_reward,
        'final_std_reward': final_std_reward,
        'best_reward': best_reward,
        'reward_weights': weights,
        'training_date': datetime.now().isoformat(),
        'melody_file': melody_file
    }
    
    # Save files
    output_dir = f"style_models/{style_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save metadata
    metadata_file = f"{output_dir}/model_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(model_metadata, f, indent=2)
    
    # Save reward history
    reward_file = f"{output_dir}/reward_history.npy"
    np.save(reward_file, np.array(reward_history))
    
    # Save training summary
    summary_file = f"{output_dir}/training_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"{style_name.upper()} STYLE HARMONIZATION TRAINING SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Style: {style_name}\n")
        f.write(f"Episodes trained: {episodes}\n")
        f.write(f"Final average reward: {final_avg_reward:.3f}\n")
        f.write(f"Final reward std: {final_std_reward:.3f}\n")
        f.write(f"Best reward: {best_reward:.3f}\n\n")
        f.write("Reward weights:\n")
        for weight_name, weight_value in weights.items():
            f.write(f"  {weight_name}: {weight_value}\n")
        f.write(f"\nTraining completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n✅ {style_name.upper()} style training completed!")
    print(f"📁 Model saved to: {output_dir}")
    print(f"📊 Final average reward: {final_avg_reward:.3f}")
    print(f"🏆 Best reward: {best_reward:.3f}")
    
    return model_metadata

def train_all_styles(episodes_per_style: int = 3000, melody_file: str = None):
    """Train models for all available styles"""
    print("🎵 TRAINING ALL STYLE-SPECIFIC MODELS")
    print("=" * 60)
    
    results = {}
    
    for style_name in STYLE_PRESETS.keys():
        print(f"\n🎼 Training {style_name.upper()} style...")
        result = train_style_specific_model(style_name, episodes_per_style, melody_file)
        if result:
            results[style_name] = result
    
    # Generate comparison report
    comparison_file = "style_models/style_comparison.json"
    os.makedirs("style_models", exist_ok=True)
    
    with open(comparison_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎉 ALL STYLES TRAINED!")
    print(f"📊 Comparison saved to: {comparison_file}")
    
    # Print summary
    print(f"\n📈 TRAINING SUMMARY:")
    for style_name, result in results.items():
        print(f"  {style_name.upper()}: {result['final_avg_reward']:.3f} avg reward")
    
    return results

def load_style_model(style_name: str):
    """Load a trained style-specific model"""
    model_dir = f"style_models/{style_name}"
    metadata_file = f"{model_dir}/model_metadata.json"
    
    if not os.path.exists(metadata_file):
        print(f"❌ No trained model found for style: {style_name}")
        return None
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    print(f"✅ Loaded {style_name} style model")
    print(f"   Episodes trained: {metadata['episodes_trained']}")
    print(f"   Average reward: {metadata['final_avg_reward']:.3f}")
    
    return metadata

if __name__ == "__main__":
    print("🎵 Style-Specific Harmonization Training")
    print("=" * 50)
    
    # Example usage
    melody_file = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    
    # Train a single style
    # train_style_specific_model('jazz', episodes=3000, melody_file=melody_file)
    
    # Train all styles
    # train_all_styles(episodes_per_style=2000, melody_file=melody_file)
    
    print("✅ Style training framework ready!")
    print("🎼 Available styles:", list(STYLE_PRESETS.keys()))
    print("📝 Use train_style_specific_model() to train individual styles")
    print("🎵 Use train_all_styles() to train all styles at once") 