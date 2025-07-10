#!/usr/bin/env python3
"""
Simple RL Training Script for Harmonization

This script trains a simple harmonization agent without heavy dependencies.
"""

import os
import sys
import numpy as np
import mido
import random
import json
from typing import List, Dict, Tuple

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

class SimpleRLAgent:
    """
    Simple RL agent for harmonization.
    """
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Simple Q-table (state -> action -> value)
        self.q_table = {}
        
        # Training parameters
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.95  # Discount factor
        
    def get_state_key(self, state: np.ndarray) -> str:
        """Convert state array to string key for Q-table."""
        return str(state.flatten().tolist())
    
    def choose_action(self, state: np.ndarray) -> np.ndarray:
        """Choose action using epsilon-greedy policy."""
        state_key = self.get_state_key(state)
        
        # Initialize Q-values for this state if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            # Random action
            action = np.random.randint(0, 88, size=3)  # 3 voices, 88 pitches each
        else:
            # Best action
            q_values = self.q_table[state_key]
            action = np.argmax(q_values)
            # Convert to multi-voice action
            action = np.array([action % 88, (action // 88) % 88, (action // (88*88)) % 88])
        
        return action
    
    def learn(self, state: np.ndarray, action: np.ndarray, reward: float, 
              next_state: np.ndarray, done: bool):
        """Update Q-values using Q-learning."""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Initialize Q-values if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        
        # Convert multi-voice action to single index
        action_idx = action[0] + action[1] * 88 + action[2] * 88 * 88
        
        # Q-learning update
        current_q = self.q_table[state_key][action_idx]
        if done:
            max_next_q = 0
        else:
            max_next_q = np.max(self.q_table[next_state_key])
        
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_key][action_idx] = new_q
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save(self, filepath: str):
        """Save the trained agent."""
        data = {
            'q_table': {k: v.tolist() for k, v in self.q_table.items()},
            'epsilon': self.epsilon,
            'state_size': self.state_size,
            'action_size': self.action_size
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, filepath: str):
        """Load a trained agent."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.q_table = {k: np.array(v) for k, v in data['q_table'].items()}
        self.epsilon = data['epsilon']
        self.state_size = data['state_size']
        self.action_size = data['action_size']

def create_env(melody_sequence=None, style='classical'):
    """Create a harmonization environment."""
    reward_system = MusicTheoryRewards()
    reward_system.set_style_preset(style)
    
    env = HarmonizationEnvironment(
        coconet_wrapper=None,
        reward_system=reward_system,
        max_steps=16,  # Shorter for faster training
        num_voices=3,
        melody_sequence=melody_sequence
    )
    
    return env

def train_agent(env, episodes=1000, model_path="simple_harmonization_model.json"):
    """Train the simple RL agent."""
    print(f"🚀 Starting simple RL training for {episodes} episodes...")
    
    # Initialize agent
    state_size = env.observation_space.shape[0] * env.observation_space.shape[1] * env.observation_space.shape[2]
    action_size = 88 * 88 * 88  # 3 voices, 88 pitches each
    agent = SimpleRLAgent(state_size, action_size)
    
    # Training loop
    episode_rewards = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            # Choose action
            action = agent.choose_action(state)
            
            # Take action
            next_state, reward, done, info = env.step(action)
            
            # Learn
            agent.learn(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
        
        episode_rewards.append(total_reward)
        
        # Print progress
        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            print(f"Episode {episode + 1}/{episodes}, Avg Reward: {avg_reward:.2f}, Epsilon: {agent.epsilon:.3f}")
    
    # Save trained agent
    agent.save(model_path)
    print(f"✅ Training complete! Model saved to {model_path}")
    
    return agent

def test_agent(agent, env, output_path="simple_harmonization_output.mid"):
    """Test the trained agent."""
    print("🧪 Testing trained agent...")
    
    # Set epsilon to 0 for deterministic behavior
    original_epsilon = agent.epsilon
    agent.epsilon = 0.0
    
    # Generate harmonization
    state = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        action = agent.choose_action(state)
        state, reward, done, info = env.step(action)
        total_reward += reward
    
    # Get final sequence
    final_sequence = env.get_final_sequence()
    
    # Save as MIDI
    save_sequence_as_midi(final_sequence, output_path)
    
    print(f"🎵 Generated harmonization saved to {output_path}")
    print(f"📊 Episode reward: {total_reward:.2f}")
    
    # Restore epsilon
    agent.epsilon = original_epsilon
    
    return final_sequence

def save_sequence_as_midi(sequence, output_path):
    """Save a sequence as MIDI file."""
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
        duration_ticks = int((note['end_time'] - note['start_time']) * 480)
        track.append(mido.Message('note_off', 
                                 note=note['pitch'], 
                                 velocity=0, 
                                 channel=note['voice'], 
                                 time=duration_ticks))
    
    midi.save(output_path)

def load_melody_from_midi(midi_path):
    """Load melody from MIDI file."""
    try:
        mid = mido.MidiFile(midi_path)
        melody_notes = []
        
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    melody_notes.append(msg.note)
        
        return melody_notes[:16]  # Limit to 16 notes
        
    except Exception as e:
        print(f"❌ Error loading MIDI: {e}")
        return None

def main():
    """Main training function."""
    print("🎼 Simple RL Harmonization Training")
    print("=" * 40)
    
    # Create training directory
    os.makedirs("simple_training_logs", exist_ok=True)
    
    # Train with random melodies
    print("🎼 Training with random melodies...")
    env = create_env(style='classical')
    agent = train_agent(env, episodes=500, model_path="simple_harmonization_model.json")
    
    # Train with custom melody if available
    melody_path = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    if os.path.exists(melody_path):
        print("🎼 Training with custom melody...")
        melody_sequence = load_melody_from_midi(melody_path)
        if melody_sequence:
            env_with_melody = create_env(melody_sequence=melody_sequence, style='classical')
            agent_with_melody = train_agent(env_with_melody, episodes=300, 
                                          model_path="simple_harmonization_model_melody.json")
    
    # Test the trained agent
    print("🧪 Testing trained agent...")
    test_env = create_env(style='classical')
    test_agent(agent, test_env, "simple_harmonization_output.mid")
    
    print("🎉 Training and testing complete!")

if __name__ == "__main__":
    main() 