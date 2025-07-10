#!/usr/bin/env python3
"""
Advanced training script with more episodes and continuation support.
Now supports reward curve plotting.
"""

import sys
import numpy as np
import mido
import random
import json
import os
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

print("🎵 Advanced RL Harmonization Training")
print("=" * 40)

class AdvancedHarmonizationAgent:
    """Advanced harmonization agent with Q-learning."""
    
    def __init__(self, state_size: int = 16, action_size: int = 12, learning_rate: float = 0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.q_table = {}
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.95  # Discount factor
        self.training_history = []
        
    def get_state_key(self, state: Tuple) -> str:
        """Convert state to string key."""
        return str(state)
    
    def choose_action(self, state: Tuple) -> int:
        """Choose action using epsilon-greedy policy."""
        state_key = self.get_state_key(state)
        
        # Initialize Q-values for this state if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            # Random action (exploration)
            action = random.randint(0, self.action_size - 1)
        else:
            # Best action (exploitation)
            q_values = self.q_table[state_key]
            action = np.argmax(q_values)
        
        return action
    
    def learn(self, state: Tuple, action: int, reward: float, next_state: Tuple, done: bool):
        """Update Q-values using Q-learning."""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Initialize Q-values if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        
        # Q-learning update
        current_q = self.q_table[state_key][action]
        if done:
            max_next_q = 0
        else:
            max_next_q = np.max(self.q_table[next_state_key])
        
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        data = {
            'q_table': {k: v.tolist() for k, v in self.q_table.items()},
            'epsilon': self.epsilon,
            'training_history': self.training_history,
            'state_size': self.state_size,
            'action_size': self.action_size
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.q_table = {k: np.array(v) for k, v in data['q_table'].items()}
            self.epsilon = data['epsilon']
            self.training_history = data.get('training_history', [])
            self.state_size = data['state_size']
            self.action_size = data['action_size']
            print(f"✅ Model loaded from {filepath}")
            return True
        return False

def calculate_music_reward(action: int, melody_note: int = None) -> float:
    """Calculate reward based on music theory."""
    # C major scale notes (0=C, 2=D, 4=E, 5=F, 7=G, 9=A, 11=B)
    major_scale = [0, 2, 4, 5, 7, 9, 11]
    
    # C major chord notes (C, E, G)
    major_chord = [0, 4, 7]
    
    # Reward for being in major scale
    if action in major_scale:
        reward = 0.5
    else:
        reward = 0.1
    
    # Extra reward for chord tones
    if action in major_chord:
        reward += 0.3
    
    # Reward for consonant intervals with melody
    if melody_note is not None:
        interval = abs(action - melody_note) % 12
        consonant_intervals = [0, 3, 4, 7, 8, 12]  # Unison, minor/major third, perfect fourth/fifth, octave
        if interval in consonant_intervals:
            reward += 0.2
    
    return reward

def train_agent(episodes: int = 10000, continue_training: bool = False, model_path: str = "advanced_harmonization_model.json", reward_history_path: str = "reward_history.npy"):
    """Train the advanced agent."""
    print(f"🤖 Training advanced agent for {episodes} episodes...")
    
    # Initialize agent
    agent = AdvancedHarmonizationAgent(state_size=16, action_size=12)
    
    # Load existing model if continuing training
    if continue_training:
        if agent.load_model(model_path):
            print(f"🔄 Continuing training from episode {len(agent.training_history)}")
        else:
            print("🆕 Starting fresh training")
    
    # Training loop
    episode_rewards = []
    
    for episode in range(episodes):
        # Generate random melody context
        melody_context = [random.randint(0, 11) for _ in range(agent.state_size)]
        state = tuple(melody_context)
        
        episode_reward = 0
        done = False
        step_count = 0
        
        while not done and step_count < 20:  # Max 20 steps per episode
            # Choose action
            action = agent.choose_action(state)
            
            # Calculate reward
            melody_note = melody_context[step_count % len(melody_context)]
            reward = calculate_music_reward(action, melody_note)
            
            # Generate next state
            next_melody_context = melody_context.copy()
            next_melody_context[step_count % len(next_melody_context)] = action
            next_state = tuple(next_melody_context)
            
            # Learn
            agent.learn(state, action, reward, next_state, done)
            
            episode_reward += reward
            state = next_state
            step_count += 1
            
            # End episode if we have enough steps
            if step_count >= 20:
                done = True
        
        episode_rewards.append(episode_reward)
        agent.training_history.append(episode_reward)
        
        # Print progress every 500 episodes
        if (episode + 1) % 500 == 0:
            avg_reward = np.mean(episode_rewards[-500:])
            print(f"Episode {episode + 1}/{episodes}: Avg Reward = {avg_reward:.3f}, Epsilon = {agent.epsilon:.3f}")
        
        # Save model every 1000 episodes
        if (episode + 1) % 1000 == 0:
            agent.save_model(f"{model_path}.checkpoint")
            np.save(reward_history_path, np.array(agent.training_history))
    
    # Save final model and reward history
    agent.save_model(model_path)
    np.save(reward_history_path, np.array(agent.training_history))
    print("✅ Advanced training complete!")
    
    return agent

def generate_harmonization(agent, output_path: str = "advanced_harmonization.mid"):
    """Generate harmonization using the trained agent."""
    print("🎼 Generating harmonization...")
    
    # Create MIDI file
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    # Generate melody and harmony
    melody_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
    state = tuple([note % 12 for note in melody_notes[:8]])  # First 8 notes as state
    
    for i, melody_note in enumerate(melody_notes):
        # Melody note
        track.append(mido.Message('note_on', note=melody_note, velocity=100, channel=0, time=0))
        track.append(mido.Message('note_off', note=melody_note, velocity=0, channel=0, time=480))
        
        # Get harmony from agent
        if i < len(melody_notes) - 1:
            # Use agent to choose harmony
            harmony_action = agent.choose_action(state)
            harmony_note = 60 + harmony_action  # Convert to MIDI pitch (C4 + action)
            
            # Add harmony note
            track.append(mido.Message('note_on', note=harmony_note, velocity=60, channel=1, time=0))
            track.append(mido.Message('note_off', note=harmony_note, velocity=0, channel=1, time=480))
            
            # Update state
            state_list = list(state)
            state_list[i % len(state_list)] = harmony_action
            state = tuple(state_list)
    
    # Save file
    midi.save(output_path)
    print(f"✅ Saved {output_path}")
    
    return True

def plot_reward_curve(reward_history_path: str = "reward_history.npy"):
    """Plot the reward curve from saved reward history."""
    print("📈 Plotting reward curve...")
    rewards = np.load(reward_history_path)
    plt.figure(figsize=(12, 6))
    plt.plot(rewards, label='Episode Reward', alpha=0.5)
    # Moving average
    window = 100
    if len(rewards) > window:
        moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
        plt.plot(range(window-1, len(rewards)), moving_avg, label=f'{window}-episode moving avg', color='red')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.title('RL Harmonization Training Reward Curve')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('reward_curve.png')
    plt.show()
    print("✅ Saved reward_curve.png")

def main():
    """Main function."""
    try:
        print("🚀 Starting advanced training...")
        
        # Check if we should continue training
        model_path = "advanced_harmonization_model.json"
        reward_history_path = "reward_history.npy"
        continue_training = os.path.exists(model_path)
        
        episodes = 10000  # Train for 10,000 episodes
        if continue_training:
            print("📁 Found existing model - continuing training")
        else:
            print("🆕 Starting fresh training")
        
        # Train agent
        agent = train_agent(episodes=episodes, continue_training=continue_training, model_path=model_path, reward_history_path=reward_history_path)
        
        # Generate harmonization
        generate_harmonization(agent)
        
        # Plot reward curve
        plot_reward_curve(reward_history_path)
        
        print("🎉 All done!")
        print("📁 Files created:")
        print(f"   - {model_path}")
        print("   - advanced_harmonization.mid")
        print("   - reward_curve.png")
        
        # Show training stats
        if agent.training_history:
            final_avg = np.mean(agent.training_history[-100:])
            print(f"📊 Final average reward: {final_avg:.3f}")
            print(f"📈 Total episodes trained: {len(agent.training_history)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 