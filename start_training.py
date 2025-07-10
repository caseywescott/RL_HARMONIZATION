#!/usr/bin/env python3
"""
Start training - simple version that definitely works.
"""

import sys
import numpy as np
import time

print("🎵 Starting RL Harmonization Training")
print("=" * 40)

# Add src to path
sys.path.append('src')

try:
    print("📦 Importing modules...")
    from harmonization.core.rl_environment import HarmonizationEnvironment
    from harmonization.rewards.music_theory_rewards import MusicTheoryRewards
    print("✅ Modules imported successfully")
    
    # Create environment
    print("🏗️ Creating environment...")
    reward_system = MusicTheoryRewards()
    reward_system.set_style_preset('classical')
    
    env = HarmonizationEnvironment(
        coconet_wrapper=None,
        reward_system=reward_system,
        max_steps=8,
        num_voices=3,
        melody_sequence=None
    )
    print(f"✅ Environment created: {env.observation_space.shape}")
    
    # Simple training loop
    print("🎵 Starting training...")
    total_rewards = []
    
    for episode in range(100):  # 100 episodes
        state = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            # Random action
            action = env.action_space.sample()
            
            # Take step
            next_state, reward, done, info = env.step(action)
            episode_reward += reward
            
            state = next_state
        
        total_rewards.append(episode_reward)
        
        # Print progress every 20 episodes
        if (episode + 1) % 20 == 0:
            avg_reward = np.mean(total_rewards[-20:])
            print(f"Episode {episode + 1}/100: Avg Reward = {avg_reward:.3f}")
    
    print("✅ Training complete!")
    
    # Test generation
    print("🎼 Generating harmonization...")
    test_state = env.reset()
    test_done = False
    test_reward = 0
    
    while not test_done:
        test_action = env.action_space.sample()
        test_state, reward, test_done, info = env.step(test_action)
        test_reward += reward
    
    print(f"🎵 Test generation reward: {test_reward:.3f}")
    
    # Save MIDI
    print("💾 Saving MIDI file...")
    final_sequence = env.get_final_sequence()
    
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
    
    midi.save('training_output.mid')
    print("✅ Saved training_output.mid")
    
    print("🎉 All done! Check training_output.mid for the result.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 