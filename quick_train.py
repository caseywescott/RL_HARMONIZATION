#!/usr/bin/env python3
"""
Quick training script with verbose output.
"""

import sys
import numpy as np

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def quick_train():
    """Quick training with verbose output."""
    print("🚀 Starting quick training...")
    
    # Create environment
    print("📦 Creating environment...")
    reward_system = MusicTheoryRewards()
    reward_system.set_style_preset('classical')
    
    env = HarmonizationEnvironment(
        coconet_wrapper=None,
        reward_system=reward_system,
        max_steps=8,  # Very short for quick training
        num_voices=3,
        melody_sequence=None
    )
    
    print(f"✅ Environment created: {env.observation_space.shape}")
    
    # Simple Q-learning agent
    print("🤖 Creating simple agent...")
    q_table = {}
    epsilon = 1.0
    learning_rate = 0.1
    
    # Training loop
    print("🎵 Starting training loop...")
    for episode in range(50):  # Very few episodes for quick test
        state = env.reset()
        total_reward = 0
        done = False
        step_count = 0
        
        while not done:
            # Choose action (random for now)
            action = env.action_space.sample()
            
            # Take step
            next_state, reward, done, info = env.step(action)
            total_reward += reward
            step_count += 1
            
            # Simple learning (just track rewards)
            state_key = str(state.flatten().tolist())
            if state_key not in q_table:
                q_table[state_key] = []
            q_table[state_key].append(reward)
            
            state = next_state
        
        # Print progress every 10 episodes
        if (episode + 1) % 10 == 0:
            print(f"Episode {episode + 1}/50: Reward = {total_reward:.2f}, Steps = {step_count}")
    
    print("✅ Quick training complete!")
    
    # Test the trained agent
    print("🧪 Testing trained agent...")
    test_state = env.reset()
    test_done = False
    test_reward = 0
    
    while not test_done:
        test_action = env.action_space.sample()
        test_state, reward, test_done, info = env.step(test_action)
        test_reward += reward
    
    print(f"🎵 Test episode reward: {test_reward:.2f}")
    
    # Save a simple harmonization
    print("💾 Saving harmonization...")
    final_sequence = env.get_final_sequence()
    
    # Save as simple MIDI
    import mido
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    # Add notes
    for note in final_sequence:
        track.append(mido.Message('note_on', 
                                 note=note['pitch'], 
                                 velocity=note['velocity'], 
                                 channel=note['voice'], 
                                 time=0))
        
        duration_ticks = int((note['end_time'] - note['start_time']) * 480)
        track.append(mido.Message('note_off', 
                                 note=note['pitch'], 
                                 velocity=0, 
                                 channel=note['voice'], 
                                 time=duration_ticks))
    
    midi.save('quick_harmonization.mid')
    print("✅ Saved quick_harmonization.mid")
    
    return True

if __name__ == "__main__":
    try:
        quick_train()
        print("🎉 All done!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 