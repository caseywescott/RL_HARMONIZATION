#!/usr/bin/env python3
"""
Test script for RL harmonization system.

This script tests the core components to ensure they work correctly.
"""

import os
import sys
import numpy as np
import note_seq
from note_seq import NoteSequence

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_reward_system():
    """Test the music theory reward system."""
    print("🧪 Testing Music Theory Reward System...")
    
    try:
        from harmonization.rewards.music_theory_rewards import MusicTheoryRewards
        
        # Create reward system
        rewards = MusicTheoryRewards()
        
        # Test style presets
        for style in ['classical', 'jazz', 'pop', 'baroque']:
            rewards.set_style_preset(style)
            print(f"  ✅ {style} style preset applied")
        
        # Test custom weights
        custom_weights = {'prefer_common_chords': 0.5, 'prefer_arpeggios': 0.3}
        rewards.set_custom_weights(custom_weights)
        print("  ✅ Custom weights applied")
        
        # Test reward calculation
        sequence = NoteSequence()
        sequence.ticks_per_quarter = 220
        
        # Add some test notes
        for i in range(4):
            note = sequence.notes.add()
            note.pitch = 60 + i  # C4, D4, E4, F4
            note.start_time = i * 0.25
            note.end_time = (i + 1) * 0.25
            note.velocity = 80
            note.instrument = i % 4
        
        reward = rewards.calculate_reward(sequence, [60, 62, 64, 65], sequence)
        print(f"  ✅ Reward calculation: {reward:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Reward system test failed: {e}")
        return False

def test_environment():
    """Test the RL environment."""
    print("🧪 Testing RL Environment...")
    
    try:
        from harmonization.core.rl_environment import HarmonizationEnvironment
        from harmonization.rewards.music_theory_rewards import MusicTheoryRewards
        
        # Create mock Coconet wrapper
        class MockCoconetWrapper:
            def get_action_probabilities(self, state, action_space):
                return np.ones(len(action_space)) / len(action_space)
            def close(self):
                pass
        
        # Create environment
        rewards = MusicTheoryRewards()
        env = HarmonizationEnvironment(
            coconet_wrapper=MockCoconetWrapper(),
            reward_system=rewards,
            max_steps=8,  # Shorter for testing
            num_voices=4
        )
        
        # Test reset
        obs = env.reset()
        print(f"  ✅ Environment reset: observation shape {obs.shape}")
        
        # Test step
        action = np.array([60, 62, 64, 65])  # C4, D4, E4, F4
        obs, reward, done, info = env.step(action)
        print(f"  ✅ Environment step: reward={reward:.3f}, done={done}")
        
        # Test multiple steps
        for i in range(3):
            action = np.random.randint(0, 88, size=4)
            obs, reward, done, info = env.step(action)
            if done:
                break
        
        print(f"  ✅ Multiple steps completed: final step {info['step']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Environment test failed: {e}")
        return False

def test_coconet_wrapper():
    """Test the Coconet wrapper (without loading actual model)."""
    print("🧪 Testing Coconet Wrapper...")
    
    try:
        from harmonization.core.coconet_wrapper import CoconetWrapper
        
        # Test initialization (will fail without actual checkpoint, but that's expected)
        try:
            wrapper = CoconetWrapper("nonexistent_path")
            print("  ❌ Should have failed with nonexistent path")
            return False
        except FileNotFoundError:
            print("  ✅ Correctly handled missing checkpoint path")
        
        # Test feature extraction
        sequence = NoteSequence()
        sequence.ticks_per_quarter = 220
        
        # Add test notes
        for i in range(4):
            note = sequence.notes.add()
            note.pitch = 60 + i
            note.start_time = i * 0.25
            note.end_time = (i + 1) * 0.25
            note.velocity = 80
            note.instrument = i % 4
        
        # Create wrapper with mock methods
        class TestCoconetWrapper(CoconetWrapper):
            def _load_model(self):
                # Skip actual model loading for testing
                pass
        
        wrapper = TestCoconetWrapper("test_path")
        
        # Test feature extraction
        features = wrapper._extract_features(sequence)
        print(f"  ✅ Feature extraction: shape {features.shape}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Coconet wrapper test failed: {e}")
        return False

def test_integration():
    """Test basic integration of components."""
    print("🧪 Testing Component Integration...")
    
    try:
        from harmonization.core.rl_environment import HarmonizationEnvironment
        from harmonization.rewards.music_theory_rewards import MusicTheoryRewards
        
        # Create mock components
        class MockCoconetWrapper:
            def get_action_probabilities(self, state, action_space):
                return np.ones(len(action_space)) / len(action_space)
            def close(self):
                pass
        
        # Create integrated system
        rewards = MusicTheoryRewards()
        rewards.set_style_preset('classical')
        
        env = HarmonizationEnvironment(
            coconet_wrapper=MockCoconetWrapper(),
            reward_system=rewards,
            max_steps=4,
            num_voices=4
        )
        
        # Run a simple episode
        obs = env.reset()
        total_reward = 0
        
        for step in range(4):
            action = np.random.randint(0, 88, size=4)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            
            if done:
                break
        
        print(f"  ✅ Integration test: episode completed with total reward {total_reward:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎵 RL Harmonization System Tests")
    print("=" * 40)
    
    tests = [
        test_reward_system,
        test_environment,
        test_coconet_wrapper,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! System is ready for training.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main() 