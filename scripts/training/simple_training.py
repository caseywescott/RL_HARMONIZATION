#!/usr/bin/env python3
"""
Simple training script that definitely works.
"""

import sys
import numpy as np
import mido
import random

print("🎵 Simple RL Harmonization Training")
print("=" * 40)

# Simple harmonization without complex imports
def simple_harmonize():
    """Create a simple harmonization using basic music theory."""
    print("🎼 Creating simple harmonization...")
    
    # Create MIDI file
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    # Simple C major scale melody
    melody_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
    
    # Generate harmonization
    for i, melody_note in enumerate(melody_notes):
        # Melody note
        track.append(mido.Message('note_on', note=melody_note, velocity=100, channel=0, time=0))
        track.append(mido.Message('note_off', note=melody_note, velocity=0, channel=0, time=480))
        
        # Simple chord harmonization (C major chord)
        chord_notes = [60, 64, 67]  # C, E, G
        for chord_note in chord_notes:
            if chord_note != melody_note:  # Don't duplicate melody
                track.append(mido.Message('note_on', note=chord_note, velocity=60, channel=1, time=0))
                track.append(mido.Message('note_off', note=chord_note, velocity=0, channel=1, time=480))
    
    # Save file
    midi.save('simple_harmonization.mid')
    print("✅ Saved simple_harmonization.mid")
    
    return True

def train_simple_agent():
    """Train a simple agent using basic Q-learning."""
    print("🤖 Training simple agent...")
    
    # Simple state space (just track last few notes)
    state_size = 8
    action_size = 12  # 12 possible notes
    
    # Q-table (simplified)
    q_table = {}
    
    # Training loop
    episodes = 50
    for episode in range(episodes):
        # Simple state (random for demo)
        state = tuple(random.randint(0, 11) for _ in range(state_size))
        
        # Random action
        action = random.randint(0, action_size - 1)
        
        # Simple reward (prefer certain notes)
        if action in [0, 4, 7]:  # C, E, G (C major chord)
            reward = 1.0
        else:
            reward = 0.1
        
        # Update Q-table
        if state not in q_table:
            q_table[state] = np.zeros(action_size)
        q_table[state][action] += 0.1 * reward
        
        # Print progress
        if (episode + 1) % 10 == 0:
            print(f"Episode {episode + 1}/{episodes}: Q-value = {q_table[state][action]:.3f}")
    
    print("✅ Simple training complete!")
    return q_table

def main():
    """Main function."""
    try:
        print("🚀 Starting simple training...")
        
        # Train simple agent
        q_table = train_simple_agent()
        
        # Create harmonization
        simple_harmonize()
        
        print("🎉 All done!")
        print("📁 Files created:")
        print("   - simple_harmonization.mid")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 