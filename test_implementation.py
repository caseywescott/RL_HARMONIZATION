#!/usr/bin/env python3
"""
Quick test script to verify the RL environment works.
"""

import sys
import numpy as np

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def test_environment():
    """Test the RL environment."""
    print("🧪 Testing RL Environment...")
    
    # Create reward system
    reward_system = MusicTheoryRewards()
    reward_system.set_style_preset('classical')
    
    # Create environment
    env = HarmonizationEnvironment(
        coconet_wrapper=None,
        reward_system=reward_system,
        max_steps=8,  # Short for testing
        num_voices=3,
        melody_sequence=None
    )
    
    print(f"✅ Environment created successfully")
    print(f"   Observation space: {env.observation_space.shape}")
    print(f"   Action space: {env.action_space}")
    
    # Test reset
    obs = env.reset()
    print(f"✅ Reset successful, observation shape: {obs.shape}")
    
    # Test a few steps
    total_reward = 0
    for step in range(5):
        # Random action
        action = env.action_space.sample()
        
        # Take step
        obs, reward, done, info = env.step(action)
        total_reward += reward
        
        print(f"   Step {step + 1}: reward = {reward:.3f}, done = {done}")
        
        if done:
            break
    
    print(f"✅ Environment test successful!")
    print(f"   Total reward: {total_reward:.3f}")
    print(f"   Final sequence length: {len(env.get_final_sequence())}")
    
    return True

def test_reward_system():
    """Test the reward system."""
    print("\n🎵 Testing Reward System...")
    
    reward_system = MusicTheoryRewards()
    
    # Test different styles
    styles = ['classical', 'jazz', 'pop', 'baroque']
    for style in styles:
        reward_system.set_style_preset(style)
        print(f"   ✅ {style} style preset applied")
    
    # Test reward calculation
    test_sequence = [
        {'pitch': 60, 'start_time': 0.0, 'end_time': 0.25, 'velocity': 80, 'voice': 0},
        {'pitch': 64, 'start_time': 0.0, 'end_time': 0.25, 'velocity': 80, 'voice': 1},
        {'pitch': 67, 'start_time': 0.0, 'end_time': 0.25, 'velocity': 80, 'voice': 2}
    ]
    
    action = np.array([39, 43, 46])  # C major chord
    melody_note = 60  # C
    
    reward = reward_system.calculate_reward_simple(test_sequence, action, melody_note)
    print(f"   ✅ Reward calculation successful: {reward:.3f}")
    
    return True

def main():
    """Main test function."""
    print("🎼 RL Harmonization System Test")
    print("=" * 40)
    
    try:
        # Test reward system
        test_reward_system()
        
        # Test environment
        test_environment()
        
        print("\n🎉 All tests passed! The system is ready for training.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main() 