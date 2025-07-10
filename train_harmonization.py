#!/usr/bin/env python3
"""
Training script for RL harmonization system.

This script demonstrates how to train harmonization agents using
different style presets and reward configurations.
"""

import os
import sys
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
import note_seq

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from harmonization.core.coconet_wrapper import CoconetWrapper
from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def create_env(checkpoint_path: str, style: str = 'classical'):
    """
    Create a harmonization environment.
    
    Args:
        checkpoint_path: Path to Coconet checkpoint
        style: Musical style preset
        
    Returns:
        HarmonizationEnvironment
    """
    # Initialize Coconet wrapper
    coconet = CoconetWrapper(checkpoint_path)
    
    # Initialize reward system
    rewards = MusicTheoryRewards()
    rewards.set_style_preset(style)
    
    # Create environment
    env = HarmonizationEnvironment(
        coconet_wrapper=coconet,
        reward_system=rewards,
        max_steps=32,
        num_voices=4
    )
    
    return env

def train_agent(env, 
                model_name: str,
                total_timesteps: int = 10000,
                eval_freq: int = 1000):
    """
    Train a harmonization agent.
    
    Args:
        env: Training environment
        model_name: Name for saving the model
        total_timesteps: Total training timesteps
        eval_freq: Evaluation frequency
    """
    # Create vectorized environment
    vec_env = DummyVecEnv([lambda: env])
    
    # Create evaluation environment
    eval_env = DummyVecEnv([lambda: create_env(
        "../coconet-64layers-128filters", 
        env.reward_system.weights.get('style', 'classical')
    )])
    
    # Create evaluation callback
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=f"./models/{model_name}_best",
        log_path=f"./logs/{model_name}",
        eval_freq=eval_freq,
        deterministic=True,
        render=False
    )
    
    # Initialize agent
    agent = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        tensorboard_log=f"./logs/{model_name}"
    )
    
    # Train agent
    print(f"🎵 Training {model_name} agent...")
    agent.learn(
        total_timesteps=total_timesteps,
        callback=eval_callback,
        progress_bar=True
    )
    
    # Save final model
    agent.save(f"./models/{model_name}_final")
    
    return agent

def test_agent(agent, env, num_episodes: int = 5):
    """
    Test a trained agent.
    
    Args:
        agent: Trained agent
        env: Test environment
        num_episodes: Number of test episodes
    """
    print(f"\n🎼 Testing agent for {num_episodes} episodes...")
    
    for episode in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action, _ = agent.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            total_reward += reward
        
        # Get final sequence
        final_sequence = env.get_final_sequence()
        
        print(f"Episode {episode + 1}: Total reward = {total_reward:.2f}")
        print(f"  Sequence length: {len(final_sequence.notes)} notes")
        
        # Save sequence as MIDI
        output_path = f"./outputs/{env.reward_system.weights.get('style', 'classical')}_episode_{episode + 1}.mid"
        note_seq.sequence_proto_to_pretty_midi(final_sequence, output_path)
        print(f"  Saved to: {output_path}")

def main():
    """Main training function."""
    # Create directories
    os.makedirs("./models", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./outputs", exist_ok=True)
    
    # Checkpoint path
    checkpoint_path = "../coconet-64layers-128filters"
    
    # Available styles
    styles = ['classical', 'jazz', 'pop', 'baroque']
    
    print("🎵 RL Harmonization Training")
    print("=" * 50)
    
    for style in styles:
        print(f"\n🎼 Training {style} style harmonization agent...")
        
        # Create environment
        env = create_env(checkpoint_path, style)
        
        # Train agent
        agent = train_agent(
            env=env,
            model_name=f"harmonization_{style}",
            total_timesteps=5000,  # Reduced for demo
            eval_freq=500
        )
        
        # Test agent
        test_env = create_env(checkpoint_path, style)
        test_agent(agent, test_env, num_episodes=2)
        
        # Clean up
        env.coconet_wrapper.close()
        test_env.coconet_wrapper.close()
    
    print("\n✅ Training complete!")
    print("📁 Check ./models/ for trained agents")
    print("📁 Check ./outputs/ for generated sequences")
    print("📁 Check ./logs/ for training logs")

if __name__ == "__main__":
    main() 