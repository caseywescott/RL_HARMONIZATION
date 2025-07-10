#!/usr/bin/env python3
"""
Simplified contrary motion training that doesn't rely on complex imports
"""

import numpy as np
import os
from datetime import datetime

def simple_contrary_motion_reward(melody_note, harmony_note, prev_melody_note, prev_harmony_note):
    """Simple contrary motion reward calculation"""
    if prev_melody_note is None or prev_harmony_note is None:
        return 0.0
    
    melody_direction = melody_note - prev_melody_note
    harmony_direction = harmony_note - prev_harmony_note
    
    # Contrary motion: melody and harmony move in opposite directions
    if melody_direction > 0 and harmony_direction < 0:
        return 2.0
    elif melody_direction < 0 and harmony_direction > 0:
        return 2.0
    elif melody_direction == 0 and harmony_direction != 0:
        return 1.0  # Partial reward for static melody
    else:
        return 0.0  # No contrary motion

def simple_music_theory_reward(melody_note, harmony_note):
    """Simple music theory reward"""
    # Basic consonance reward
    interval = abs(melody_note - harmony_note) % 12
    if interval in [0, 3, 4, 7, 8]:  # Unison, minor/major third, perfect fourth/fifth, minor sixth
        return 1.0
    else:
        return 0.5

def train_simple_contrary_motion(episodes=10000):
    """Simple training simulation"""
    print("🎵 SIMPLE CONTRARY MOTION TRAINING")
    print("=" * 50)
    print(f"Episodes: {episodes}")
    print(f"Training started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Training melody (C major scale)
    melody_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C, D, E, F, G, A, B, C
    
    episode_rewards = []
    best_reward = float('-inf')
    
    print(f"Training melody: {len(melody_notes)} notes")
    print(f"Starting training...")
    print("Progress: ", end="", flush=True)
    
    for episode in range(episodes):
        episode_reward = 0
        prev_melody_note = None
        prev_harmony_note = None
        
        # Run episode
        for melody_note in melody_notes:
            # Simple harmony generation (random but weighted)
            harmony_options = [melody_note - 3, melody_note - 7, melody_note + 5]  # Third, fifth, fourth
            harmony_note = np.random.choice(harmony_options)
            
            # Calculate rewards
            music_reward = simple_music_theory_reward(melody_note, harmony_note)
            contrary_reward = simple_contrary_motion_reward(melody_note, harmony_note, prev_melody_note, prev_harmony_note)
            total_reward = music_reward + contrary_reward
            
            episode_reward += total_reward
            prev_melody_note = melody_note
            prev_harmony_note = harmony_note
        
        episode_rewards.append(episode_reward)
        
        # Track best performance
        if episode_reward > best_reward:
            best_reward = episode_reward
        
        # Progress indicator
        if (episode + 1) % 1000 == 0:
            recent_avg = np.mean(episode_rewards[-1000:])
            print(f"\nEpisode {episode + 1}: Avg reward = {recent_avg:.3f}, Best = {best_reward:.3f}")
            print("Progress: ", end="", flush=True)
        elif (episode + 1) % 100 == 0:
            print(".", end="", flush=True)
    
    print(f"\n\n🎉 TRAINING COMPLETE!")
    print(f"Episodes completed: {episodes}")
    print(f"Final average reward: {np.mean(episode_rewards):.3f}")
    print(f"Best episode reward: {best_reward:.3f}")
    print(f"Training finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save results
    save_simple_training_results(episode_rewards, best_reward, episodes)
    
    return episode_rewards, best_reward

def save_simple_training_results(episode_rewards, best_reward, episodes):
    """Save training results"""
    print(f"\n💾 SAVING TRAINING RESULTS...")
    
    # Save reward history
    reward_file = "simple_contrary_motion_reward_history.npy"
    np.save(reward_file, np.array(episode_rewards))
    print(f"✅ Saved reward history: {reward_file}")
    
    # Save training summary
    summary_file = "simple_contrary_motion_training_summary.txt"
    with open(summary_file, "w") as f:
        f.write("SIMPLE CONTRARY MOTION TRAINING SUMMARY\n")
        f.write("=" * 40 + "\n")
        f.write(f"Training date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Episodes: {episodes}\n")
        f.write(f"Final average reward: {np.mean(episode_rewards):.3f}\n")
        f.write(f"Best episode reward: {best_reward:.3f}\n")
        f.write(f"Reward function: Simple music theory + Contrary motion\n")
        f.write(f"Training melody: C major scale (8 notes)\n")
        f.write(f"Max steps per episode: 8\n")
    
    print(f"✅ Saved training summary: {summary_file}")
    
    # Create model metadata
    metadata = {
        "model_name": "Simple_Contrary_Motion_Model",
        "version": "1.0",
        "training_date": datetime.now().isoformat(),
        "episodes_trained": episodes,
        "average_reward": float(np.mean(episode_rewards)),
        "best_reward": float(best_reward),
        "reward_function": "Simple music theory + Contrary motion",
        "description": "Simple contrary motion harmonization model"
    }
    
    import json
    with open("simple_contrary_motion_model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Saved model metadata: simple_contrary_motion_model_metadata.json")
    
    print(f"\n📊 TRAINING STATISTICS:")
    print(f"  - Episodes: {episodes}")
    print(f"  - Average reward: {np.mean(episode_rewards):.3f}")
    print(f"  - Best reward: {best_reward:.3f}")
    print(f"  - Final 1000 episodes avg: {np.mean(episode_rewards[-1000:]):.3f}")

def main():
    """Main function"""
    print("🎵 SIMPLE CONTRARY MOTION TRAINING")
    print("=" * 50)
    
    try:
        episode_rewards, best_reward = train_simple_contrary_motion(episodes=10000)
        
        print(f"\n🎉 SUCCESS! Simple contrary motion model trained.")
        print(f"Files created:")
        print(f"  - simple_contrary_motion_reward_history.npy")
        print(f"  - simple_contrary_motion_training_summary.txt")
        print(f"  - simple_contrary_motion_model_metadata.json")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main() 