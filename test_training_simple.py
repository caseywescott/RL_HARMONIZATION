#!/usr/bin/env python3
"""
Simple test to check if training components work
"""

import sys
sys.path.append('src')

try:
    from harmonization.core.rl_environment import RLHarmonizationEnv
    from harmonization.rewards.music_theory_rewards import MusicTheoryRewards
    print("✅ Imports successful")
    
    # Test reward function
    rewards = MusicTheoryRewards()
    reward = rewards.calculate_reward(60, 57)  # C and A
    print(f"✅ Reward calculation: {reward}")
    
    # Test environment creation
    melody_notes = [{'note': 60, 'start_time': 0, 'duration': 480, 'velocity': 100}]
    env = RLHarmonizationEnv(melody_notes=melody_notes, rewards=rewards, max_steps=2)
    print("✅ Environment created")
    
    # Test one step
    obs = env.reset()
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    print(f"✅ Environment step: reward={reward}, done={done}")
    
    print("🎉 All components working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 