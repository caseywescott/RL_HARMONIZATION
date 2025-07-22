#!/usr/bin/env python3
"""
RL Training Script for Harmonization

This script trains a reinforcement learning agent for harmonization
using the fixed environment without note_seq dependencies.
"""

import os
import sys
import numpy as np
import mido
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
import optuna
from optuna.samplers import TPESampler

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def create_env(melody_sequence=None, style='classical'):
    """
    Create a harmonization environment.
    
    Args:
        melody_sequence: Optional melody sequence to harmonize
        style: Musical style preset
        
    Returns:
        HarmonizationEnvironment
    """
    # Initialize reward system
    reward_system = MusicTheoryRewards()
    reward_system.set_style_preset(style)
    
    # Create environment
    env = HarmonizationEnvironment(
        coconet_wrapper=None,  # Not using Coconet for now
        reward_system=reward_system,
        max_steps=32,
        num_voices=3,
        melody_sequence=melody_sequence
    )
    
    return env

def train_agent(env, 
                total_timesteps=100000, 
                model_path="trained_harmonization_model",
                log_dir="training_logs"):
    """
    Train the RL agent.
    
    Args:
        env: Training environment
        total_timesteps: Total training timesteps
        model_path: Path to save the trained model
        log_dir: Directory for training logs
    """
    print(f"🚀 Starting RL training for {total_timesteps} timesteps...")
    
    # Create vectorized environment
    vec_env = DummyVecEnv([lambda: env])
    
    # Create evaluation environment
    eval_env = create_env(style='classical')
    eval_vec_env = DummyVecEnv([lambda: eval_env])
    
    # Create callbacks
    eval_callback = EvalCallback(
        eval_vec_env,
        best_model_save_path=f"{log_dir}/best_model",
        log_path=log_dir,
        eval_freq=max(total_timesteps // 10, 1),
        deterministic=True,
        render=False
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=max(total_timesteps // 20, 1),
        save_path=log_dir,
        name_prefix="harmonization_model"
    )
    
    # Initialize PPO agent
    model = PPO(
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
        ent_coef=0.01,
        tensorboard_log=log_dir
    )
    
    # Train the agent
    print("🎵 Training harmonization agent...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=[eval_callback, checkpoint_callback],
        progress_bar=True
    )
    
    # Save the final model
    model.save(model_path)
    print(f"✅ Training complete! Model saved to {model_path}")
    
    return model

def hyperparameter_optimization(n_trials=50):
    """
    Optimize hyperparameters using Optuna.
    
    Args:
        n_trials: Number of optimization trials
    """
    print(f"🔍 Starting hyperparameter optimization with {n_trials} trials...")
    
    def objective(trial):
        # Define hyperparameter search space
        learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True)
        n_steps = trial.suggest_categorical("n_steps", [1024, 2048, 4096])
        batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])
        n_epochs = trial.suggest_int("n_epochs", 5, 15)
        gamma = trial.suggest_float("gamma", 0.9, 0.999)
        ent_coef = trial.suggest_float("ent_coef", 0.001, 0.1, log=True)
        
        # Create environment
        env = create_env(style='classical')
        vec_env = DummyVecEnv([lambda: env])
        
        # Create model with trial parameters
        model = PPO(
            "MlpPolicy",
            vec_env,
            verbose=0,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=gamma,
            ent_coef=ent_coef
        )
        
        # Train for a shorter period for optimization
        model.learn(total_timesteps=10000, progress_bar=False)
        
        # Evaluate the model
        eval_env = create_env(style='classical')
        eval_vec_env = DummyVecEnv([lambda: eval_env])
        
        mean_reward = 0
        n_eval_episodes = 10
        
        for _ in range(n_eval_episodes):
            obs = eval_vec_env.reset()
            done = False
            episode_reward = 0
            
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _ = eval_vec_env.step(action)
                episode_reward += reward
            
            mean_reward += episode_reward
        
        mean_reward /= n_eval_episodes
        
        return mean_reward
    
    # Create study
    study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(seed=42)
    )
    
    # Run optimization
    study.optimize(objective, n_trials=n_trials)
    
    print(f"🏆 Best trial: {study.best_trial.value}")
    print(f"🎯 Best parameters: {study.best_trial.params}")
    
    return study.best_trial.params

def test_trained_model(model_path="trained_harmonization_model", 
                      melody_sequence=None,
                      output_path="test_harmonization.mid"):
    """
    Test a trained model by generating harmonization.
    
    Args:
        model_path: Path to trained model
        melody_sequence: Melody to harmonize
        output_path: Output MIDI file path
    """
    print(f"🧪 Testing trained model from {model_path}...")
    
    try:
        # Load trained model
        model = PPO.load(model_path)
        print("✅ Model loaded successfully")
        
        # Create test environment
        env = create_env(melody_sequence=melody_sequence, style='classical')
        
        # Generate harmonization
        obs = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward
        
        # Get final sequence
        final_sequence = env.get_final_sequence()
        
        # Save as MIDI
        save_sequence_as_midi(final_sequence, output_path)
        
        print(f"🎵 Generated harmonization saved to {output_path}")
        print(f"📊 Episode reward: {episode_reward:.2f}")
        
        return final_sequence
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return None

def save_sequence_as_midi(sequence, output_path):
    """
    Save a sequence as MIDI file.
    
    Args:
        sequence: List of note dictionaries
        output_path: Output MIDI file path
    """
    # Create MIDI file
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    # Add notes
    for note in sequence:
        # Note on
        track.append(mido.Message('note_on', 
                                 note=note['pitch'], 
                                 velocity=note['velocity'], 
                                 channel=note['voice'], 
                                 time=0))
        
        # Note off
        duration_ticks = int((note['end_time'] - note['start_time']) * 480)  # 480 ticks per quarter
        track.append(mido.Message('note_off', 
                                 note=note['pitch'], 
                                 velocity=0, 
                                 channel=note['voice'], 
                                 time=duration_ticks))
    
    # Save file
    midi.save(output_path)

def load_melody_from_midi(midi_path):
    """
    Load melody from MIDI file.
    
    Args:
        midi_path: Path to MIDI file
        
    Returns:
        List of MIDI pitches
    """
    try:
        mid = mido.MidiFile(midi_path)
        melody_notes = []
        
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    melody_notes.append(msg.note)
        
        return melody_notes[:32]  # Limit to 32 notes
        
    except Exception as e:
        print(f"❌ Error loading MIDI: {e}")
        return None

def main():
    """Main training function."""
    
    # Create training directory
    os.makedirs("training_logs", exist_ok=True)
    
    # Option 1: Train with random melodies
    print("🎼 Training with random melodies...")
    env = create_env(style='classical')
    model = train_agent(env, total_timesteps=50000)
    
    # Option 2: Train with specific melody (if available)
    melody_path = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    if os.path.exists(melody_path):
        print("🎼 Training with custom melody...")
        melody_sequence = load_melody_from_midi(melody_path)
        if melody_sequence:
            env_with_melody = create_env(melody_sequence=melody_sequence, style='classical')
            model_with_melody = train_agent(env_with_melody, total_timesteps=30000, 
                                          model_path="trained_harmonization_model_melody")
    
    # Test the trained model
    print("🧪 Testing trained model...")
    test_trained_model(model_path="trained_harmonization_model")
    
    print("🎉 Training and testing complete!")

if __name__ == "__main__":
    main() 