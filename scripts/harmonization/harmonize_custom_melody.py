#!/usr/bin/env python3
"""
Custom Melody Harmonization Script

This script loads a custom MIDI melody and harmonizes it using the RL system.
"""

import os
import sys
import numpy as np
import note_seq
from note_seq import NoteSequence
from stable_baselines3 import PPO
import tempfile

# Add src to path
sys.path.append('src')

from harmonization.core.coconet_wrapper import CoconetWrapper
from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

def load_midi_melody(midi_path: str) -> NoteSequence:
    """
    Load a MIDI file and extract the melody (first track).
    
    Args:
        midi_path: Path to the MIDI file
        
    Returns:
        NoteSequence containing the melody
    """
    print(f"Loading MIDI file: {midi_path}")
    
    # Load the MIDI file
    sequence = note_seq.midi_file_to_note_sequence(midi_path)
    
    print(f"Loaded sequence with {len(sequence.notes)} notes")
    print(f"Duration: {sequence.total_time:.2f} seconds")
    print(f"Ticks per quarter: {sequence.ticks_per_quarter}")
    
    # Extract melody (first track or highest notes)
    melody_notes = []
    
    # Group notes by time
    time_notes = {}
    for note in sequence.notes:
        start_time = round(note.start_time, 2)  # Round to 2 decimal places
        if start_time not in time_notes:
            time_notes[start_time] = []
        time_notes[start_time].append(note)
    
    # For each time point, take the highest note as melody
    for time_point in sorted(time_notes.keys()):
        notes_at_time = time_notes[time_point]
        # Sort by pitch (highest first)
        notes_at_time.sort(key=lambda x: x.pitch, reverse=True)
        melody_notes.append(notes_at_time[0])
    
    # Create melody sequence
    melody_sequence = NoteSequence()
    melody_sequence.ticks_per_quarter = sequence.ticks_per_quarter
    melody_sequence.tempos.add(qpm=120)  # Default tempo
    
    for note in melody_notes:
        new_note = melody_sequence.notes.add()
        new_note.CopyFrom(note)
        new_note.instrument = 0  # Melody voice
    
    print(f"Extracted melody with {len(melody_sequence.notes)} notes")
    
    return melody_sequence

def harmonize_melody(melody_sequence: NoteSequence, 
                    model_path: str = "trained_harmonization_model",
                    num_voices: int = 3,
                    output_path: str = "harmonized_output.mid") -> NoteSequence:
    """
    Harmonize a melody using the trained RL model.
    
    Args:
        melody_sequence: Input melody as NoteSequence
        model_path: Path to trained model
        num_voices: Number of harmony voices to add
        output_path: Output MIDI file path
        
    Returns:
        Harmonized NoteSequence
    """
    print(f"Harmonizing melody with {num_voices} voices...")
    
    # Initialize components
    coconet_wrapper = CoconetWrapper(
        checkpoint_path="coconet-64layers-128filters/best_model.ckpt"
    )
    
    reward_system = MusicTheoryRewards()
    
    # Create environment
    env = HarmonizationEnvironment(
        coconet_wrapper=coconet_wrapper,
        reward_system=reward_system,
        max_steps=len(melody_sequence.notes),
        num_voices=num_voices
    )
    
    # Load trained model
    try:
        model = PPO.load(model_path)
        print(f"Loaded trained model from {model_path}")
    except FileNotFoundError:
        print(f"Model not found at {model_path}, using random policy")
        model = None
    
    # Create harmonized sequence
    harmonized_sequence = NoteSequence()
    harmonized_sequence.ticks_per_quarter = melody_sequence.ticks_per_quarter
    harmonized_sequence.tempos.add(qpm=120)
    
    # Copy melody notes
    for note in melody_sequence.notes:
        new_note = harmonized_sequence.notes.add()
        new_note.CopyFrom(note)
        new_note.instrument = 0  # Melody voice
    
    # Generate harmony for each melody note
    for i, melody_note in enumerate(melody_sequence.notes):
        # Create observation based on current melody note
        observation = env._get_observation()
        
        # Get action from model or random
        if model is not None:
            action, _ = model.predict(observation, deterministic=True)
        else:
            action = env.action_space.sample()
        
        # Convert action to harmony notes
        harmony_notes = env._action_to_sequence(action)
        
        # Add harmony notes to output sequence
        for note in harmony_notes.notes:
            if note.instrument > 0:  # Harmony voices (not melody)
                new_note = harmonized_sequence.notes.add()
                new_note.CopyFrom(note)
                new_note.start_time = melody_note.start_time
                new_note.end_time = melody_note.end_time
                new_note.instrument = note.instrument
    
    print(f"Generated harmonized sequence with {len(harmonized_sequence.notes)} notes")
    
    # Save to MIDI
    note_seq.note_sequence_to_midi_file(harmonized_sequence, output_path)
    print(f"Saved harmonized output to: {output_path}")
    
    return harmonized_sequence

def main():
    """Main function to harmonize the custom melody."""
    
    # Input MIDI file
    midi_path = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    
    if not os.path.exists(midi_path):
        print(f"Error: MIDI file not found at {midi_path}")
        return
    
    try:
        # Load melody
        melody_sequence = load_midi_melody(midi_path)
        
        # Save melody as separate file for reference
        note_seq.note_sequence_to_midi_file(melody_sequence, "extracted_melody.mid")
        print("Saved extracted melody to: extracted_melody.mid")
        
        # Harmonize melody
        harmonized_sequence = harmonize_melody(
            melody_sequence=melody_sequence,
            model_path="trained_harmonization_model",
            num_voices=3,
            output_path="realms2_harmonized.mid"
        )
        
        print("\nHarmonization complete!")
        print("Files created:")
        print("- extracted_melody.mid: Original melody")
        print("- realms2_harmonized.mid: Harmonized version")
        
    except Exception as e:
        print(f"Error during harmonization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 