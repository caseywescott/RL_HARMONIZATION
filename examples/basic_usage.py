#!/usr/bin/env python3
"""
Basic usage example for RL harmonization system.

This example demonstrates how to:
1. Set up the harmonization environment
2. Train agents with different styles
3. Generate harmonizations
4. Save results as MIDI files
"""

import os
import sys
import numpy as np
import note_seq

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from harmonization.core.coconet_wrapper import CoconetWrapper
from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def create_simple_melody():
    """Create a simple C major melody for testing."""
    sequence = note_seq.NoteSequence()
    sequence.ticks_per_quarter = 220
    
    # Simple C major scale melody
    pitches = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
    for i, pitch in enumerate(pitches):
        note = sequence.notes.add()
        note.pitch = pitch
        note.start_time = i * 0.5  # Half notes
        note.end_time = (i + 1) * 0.5
        note.velocity = 80
        note.instrument = 0  # Melody voice
    
    return sequence

def demonstrate_style_presets():
    """Demonstrate different style presets."""
    print("🎵 Demonstrating Style Presets")
    print("=" * 40)
    
    # Create reward system
    rewards = MusicTheoryRewards()
    
    # Test each style preset
    styles = ['classical', 'jazz', 'pop', 'baroque']
    
    for style in styles:
        print(f"\n🎼 {style.title()} Style:")
        rewards.set_style_preset(style)
        
        # Show some key weights
        key_weights = {k: v for k, v in rewards.weights.items() if v > 0.1}
        for rule, weight in key_weights.items():
            print(f"  {rule}: {weight:.2f}")

def demonstrate_reward_calculation():
    """Demonstrate reward calculation with different sequences."""
    print("\n🎵 Demonstrating Reward Calculation")
    print("=" * 40)
    
    # Create reward system
    rewards = MusicTheoryRewards()
    rewards.set_style_preset('classical')
    
    # Create test sequences
    sequence1 = create_simple_melody()
    
    # Create a more complex sequence
    sequence2 = note_seq.NoteSequence()
    sequence2.ticks_per_quarter = 220
    
    # Add some chord tones
    for i in range(8):
        # C major triad: C, E, G
        for pitch in [60, 64, 67]:  # C4, E4, G4
            note = sequence2.notes.add()
            note.pitch = pitch + i % 12  # Transpose
            note.start_time = i * 0.5
            note.end_time = (i + 1) * 0.5
            note.velocity = 80
            note.instrument = i % 4  # Different voices
    
    # Calculate rewards
    reward1 = rewards.calculate_reward(sequence1, [60, 62, 64, 65], sequence1)
    reward2 = rewards.calculate_reward(sequence2, [60, 64, 67, 72], sequence2)
    
    print(f"Simple melody reward: {reward1:.3f}")
    print(f"Chord sequence reward: {reward2:.3f}")

def demonstrate_environment():
    """Demonstrate the RL environment."""
    print("\n🎵 Demonstrating RL Environment")
    print("=" * 40)
    
    # Create mock Coconet wrapper for demonstration
    class MockCoconetWrapper:
        def get_action_probabilities(self, state, action_space):
            return np.ones(len(action_space)) / len(action_space)
        def close(self):
            pass
    
    # Create environment
    coconet = MockCoconetWrapper()
    rewards = MusicTheoryRewards()
    rewards.set_style_preset('classical')
    
    env = HarmonizationEnvironment(
        coconet_wrapper=coconet,
        reward_system=rewards,
        max_steps=8,  # Shorter for demo
        num_voices=4
    )
    
    # Run a simple episode
    obs = env.reset()
    total_reward = 0
    
    print("Running episode...")
    for step in range(8):
        # Random actions for demonstration
        action = np.random.randint(0, 88, size=4)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        
        print(f"  Step {step + 1}: reward = {reward:.3f}")
        
        if done:
            break
    
    print(f"Episode completed! Total reward: {total_reward:.3f}")
    
    # Get final sequence
    final_sequence = env.get_final_sequence()
    print(f"Generated {len(final_sequence.notes)} notes")

def demonstrate_custom_weights():
    """Demonstrate custom reward weights."""
    print("\n🎵 Demonstrating Custom Weights")
    print("=" * 40)
    
    # Create reward system
    rewards = MusicTheoryRewards()
    
    # Set custom weights for a "romantic" style
    romantic_weights = {
        'prefer_arpeggios': 0.4,
        'prefer_common_intervals': 0.3,
        'prefer_common_chords': 0.2,
        'prefer_voice_leading': 0.1
    }
    
    rewards.set_custom_weights(romantic_weights)
    
    print("Custom 'Romantic' style weights:")
    for rule, weight in romantic_weights.items():
        print(f"  {rule}: {weight:.2f}")
    
    # Test with a sequence
    sequence = create_simple_melody()
    reward = rewards.calculate_reward(sequence, [60, 62, 64, 65], sequence)
    print(f"Reward with custom weights: {reward:.3f}")

def save_example_sequence():
    """Save an example sequence as MIDI."""
    print("\n🎵 Saving Example Sequence")
    print("=" * 40)
    
    # Create output directory
    os.makedirs("outputs", exist_ok=True)
    
    # Create a simple harmonization
    sequence = note_seq.NoteSequence()
    sequence.ticks_per_quarter = 220
    
    # Add a simple 4-part harmonization
    # Soprano (melody)
    for i, pitch in enumerate([60, 62, 64, 65, 67, 69, 71, 72]):
        note = sequence.notes.add()
        note.pitch = pitch
        note.start_time = i * 0.5
        note.end_time = (i + 1) * 0.5
        note.velocity = 80
        note.instrument = 0
    
    # Alto
    for i, pitch in enumerate([55, 57, 60, 62, 64, 65, 67, 69]):
        note = sequence.notes.add()
        note.pitch = pitch
        note.start_time = i * 0.5
        note.end_time = (i + 1) * 0.5
        note.velocity = 70
        note.instrument = 1
    
    # Tenor
    for i, pitch in enumerate([48, 50, 52, 53, 55, 57, 60, 62]):
        note = sequence.notes.add()
        note.pitch = pitch
        note.start_time = i * 0.5
        note.end_time = (i + 1) * 0.5
        note.velocity = 60
        note.instrument = 2
    
    # Bass
    for i, pitch in enumerate([36, 38, 40, 41, 43, 45, 48, 50]):
        note = sequence.notes.add()
        note.pitch = pitch
        note.start_time = i * 0.5
        note.end_time = (i + 1) * 0.5
        note.velocity = 50
        note.instrument = 3
    
    # Save as MIDI
    output_path = "outputs/example_harmonization.mid"
    note_seq.sequence_proto_to_pretty_midi(sequence, output_path)
    print(f"✅ Saved example harmonization to: {output_path}")

def main():
    """Run all demonstrations."""
    print("🎵 RL Harmonization System - Basic Usage Examples")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demonstrate_style_presets()
        demonstrate_reward_calculation()
        demonstrate_environment()
        demonstrate_custom_weights()
        save_example_sequence()
        
        print("\n✅ All demonstrations completed successfully!")
        print("\n📁 Check the 'outputs/' directory for generated MIDI files")
        print("🎼 You can now explore the system with your own melodies and styles!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("Make sure all dependencies are installed: pip3 install -r requirements.txt")

if __name__ == "__main__":
    main() 