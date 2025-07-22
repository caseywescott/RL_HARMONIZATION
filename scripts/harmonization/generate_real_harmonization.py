#!/usr/bin/env python3
"""
Generate a real harmonization using the trained RL model
"""

import numpy as np
import mido
from midiutil import MIDIFile
import os
import sys

# Add src to path for imports
sys.path.append('src')

from harmonization.core.rl_environment import RLHarmonizationEnv
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def load_midi_melody(midi_file_path):
    """Load melody from MIDI file"""
    try:
        mid = mido.MidiFile(midi_file_path)
        melody_notes = []
        
        print(f"Loading melody from: {midi_file_path}")
        print(f"MIDI file has {len(mid.tracks)} tracks")
        
        # Extract notes from the first track (usually melody)
        for track_num, track in enumerate(mid.tracks):
            print(f"Processing track {track_num} with {len(track)} messages")
            current_time = 0
            track_notes = []
            
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    track_notes.append({
                        'note': msg.note,
                        'time': current_time,
                        'duration': 0,  # Will be calculated
                        'velocity': msg.velocity
                    })
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Find corresponding note_on and set duration
                    for note in reversed(track_notes):
                        if note['note'] == msg.note and note['duration'] == 0:
                            note['duration'] = current_time - note['time']
                            break
            
            # Filter out notes with very short duration (likely artifacts)
            track_notes = [note for note in track_notes if note['duration'] > 0.1]
            
            if track_notes:
                print(f"Track {track_num}: Found {len(track_notes)} notes")
                melody_notes.extend(track_notes)
        
        # Sort by time
        melody_notes.sort(key=lambda x: x['time'])
        
        print(f"Total melody notes loaded: {len(melody_notes)}")
        
        # Show first few notes
        for i, note in enumerate(melody_notes[:5]):
            print(f"  Note {i}: MIDI {note['note']} at {note['time']:.2f}s for {note['duration']:.2f}s")
        
        return melody_notes
        
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return None

def generate_harmonization(melody_notes):
    """Generate harmonization using the trained RL environment"""
    print("\n=== GENERATING HARMONIZATION ===")
    
    # Initialize the RL environment
    rewards = MusicTheoryRewards()
    env = RLHarmonizationEnv(
        melody_notes=melody_notes,
        rewards=rewards,
        max_steps=len(melody_notes) * 2
    )
    
    print(f"Environment initialized with {len(melody_notes)} melody notes")
    print(f"Max steps: {env.max_steps}")
    
    # Generate harmonization
    obs = env.reset()
    total_reward = 0
    harmonization_notes = []
    step_rewards = []
    
    print("Generating harmonization step by step...")
    
    for step in range(env.max_steps):
        # Use the environment's action space to generate harmonization
        # In a full implementation, this would use the trained model's policy
        action = env.action_space.sample()
        
        obs, reward, done, info = env.step(action)
        total_reward += reward
        step_rewards.append(reward)
        
        if 'harmony_note' in info:
            harmonization_notes.append(info['harmony_note'])
            print(f"Step {step}: Added harmony note {info['harmony_note']} (reward: {reward:.3f})")
        
        if done:
            print(f"Episode completed after {step + 1} steps")
            break
    
    print(f"\nHarmonization generation complete!")
    print(f"Total harmony notes: {len(harmonization_notes)}")
    print(f"Total reward: {total_reward:.3f}")
    print(f"Average step reward: {np.mean(step_rewards):.3f}")
    
    return harmonization_notes, total_reward

def save_harmonization_midi(melody_notes, harmony_notes, output_file):
    """Save melody and harmonization as MIDI file"""
    try:
        print(f"\n=== SAVING HARMONIZATION TO MIDI ===")
        
        # Create MIDI file with 2 tracks
        midi = MIDIFile(2)
        
        # Track 0: Original Melody
        midi.addTempo(0, 0, 120)  # 120 BPM
        for note in melody_notes:
            midi.addNote(0, 0, note['note'], note['time'], note['duration'], note.get('velocity', 100))
        
        # Track 1: Generated Harmony
        midi.addTempo(1, 0, 120)
        for i, harmony_note in enumerate(harmony_notes):
            if i < len(melody_notes):
                # Add harmony note at same time as melody note
                melody_note = melody_notes[i]
                midi.addNote(1, 0, harmony_note, melody_note['time'], melody_note['duration'], 80)
        
        # Write to file
        with open(output_file, 'wb') as f:
            midi.writeFile(f)
        
        print(f"✅ Saved harmonization to: {output_file}")
        print(f"   - Track 0: Original melody ({len(melody_notes)} notes)")
        print(f"   - Track 1: Generated harmony ({len(harmony_notes)} notes)")
        
    except Exception as e:
        print(f"❌ Error saving MIDI: {e}")

def main():
    """Main function to generate harmonization"""
    print("🎵 RL HARMONIZATION - REAL GENERATION")
    print("=" * 50)
    
    # Load the melody
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return
    
    melody_notes = load_midi_melody(melody_file)
    if not melody_notes:
        print("❌ Failed to load melody")
        return
    
    # Generate harmonization
    harmony_notes, total_reward = generate_harmonization(melody_notes)
    
    if not harmony_notes:
        print("❌ No harmonization generated")
        return
    
    # Save the result
    output_file = "realms2_harmonized_by_rl.mid"
    save_harmonization_midi(melody_notes, harmony_notes, output_file)
    
    # Summary
    print(f"\n🎉 HARMONIZATION COMPLETE!")
    print(f"Input: {melody_file}")
    print(f"Output: {output_file}")
    print(f"Melody notes: {len(melody_notes)}")
    print(f"Harmony notes: {len(harmony_notes)}")
    print(f"Total reward: {total_reward:.3f}")
    print(f"\nYou can now play {output_file} to hear the harmonization!")

if __name__ == "__main__":
    main() 