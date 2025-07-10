#!/usr/bin/env python3
"""
Simple Melody Harmonization Script

This script loads a custom MIDI melody and creates a simple harmonization
using basic music theory rules, without requiring a trained RL model.
"""

import os
import sys
import numpy as np
import note_seq
from note_seq import NoteSequence

def load_midi_melody(midi_path: str) -> NoteSequence:
    """
    Load a MIDI file and extract the melody.
    
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
    
    # Extract melody (highest notes at each time point)
    melody_notes = []
    
    # Group notes by time
    time_notes = {}
    for note in sequence.notes:
        start_time = round(note.start_time, 2)
        if start_time not in time_notes:
            time_notes[start_time] = []
        time_notes[start_time].append(note)
    
    # For each time point, take the highest note as melody
    for time_point in sorted(time_notes.keys()):
        notes_at_time = time_notes[time_point]
        notes_at_time.sort(key=lambda x: x.pitch, reverse=True)
        melody_notes.append(notes_at_time[0])
    
    # Create melody sequence
    melody_sequence = NoteSequence()
    melody_sequence.ticks_per_quarter = sequence.ticks_per_quarter
    melody_sequence.tempos.add(qpm=120)
    
    for note in melody_notes:
        new_note = melody_sequence.notes.add()
        new_note.CopyFrom(note)
        new_note.instrument = 0  # Melody voice
    
    print(f"Extracted melody with {len(melody_sequence.notes)} notes")
    
    return melody_sequence

def get_chord_for_note(melody_note: int) -> list:
    """
    Get a simple chord for a melody note using basic music theory.
    
    Args:
        melody_note: MIDI pitch of the melody note
        
    Returns:
        List of MIDI pitches for the chord
    """
    # Convert to pitch class (0-11)
    pitch_class = melody_note % 12
    
    # Simple major chord: root, major third, perfect fifth
    # For each pitch class, define the major chord
    major_chords = {
        0: [0, 4, 7],    # C major: C, E, G
        1: [1, 5, 8],    # C# major: C#, F, G#
        2: [2, 6, 9],    # D major: D, F#, A
        3: [3, 7, 10],   # Eb major: Eb, G, Bb
        4: [4, 8, 11],   # E major: E, G#, B
        5: [5, 9, 0],    # F major: F, A, C
        6: [6, 10, 1],   # F# major: F#, B, C#
        7: [7, 11, 2],   # G major: G, B, D
        8: [8, 0, 3],    # Ab major: Ab, C, Eb
        9: [9, 1, 4],    # A major: A, C#, E
        10: [10, 2, 5],  # Bb major: Bb, D, F
        11: [11, 3, 6],  # B major: B, Eb, F#
    }
    
    chord_pitch_classes = major_chords[pitch_class]
    
    # Convert to MIDI pitches in a reasonable octave
    octave = melody_note // 12 - 1  # One octave below melody
    chord_pitches = []
    
    for pitch_class in chord_pitch_classes:
        midi_pitch = pitch_class + (octave * 12)
        # Ensure pitches are in reasonable range (21-108)
        while midi_pitch < 21:
            midi_pitch += 12
        while midi_pitch > 108:
            midi_pitch -= 12
        chord_pitches.append(midi_pitch)
    
    return chord_pitches

def harmonize_melody_simple(melody_sequence: NoteSequence, 
                           output_path: str = "simple_harmonized.mid") -> NoteSequence:
    """
    Create a simple harmonization of the melody using basic chord progressions.
    
    Args:
        melody_sequence: Input melody as NoteSequence
        output_path: Output MIDI file path
        
    Returns:
        Harmonized NoteSequence
    """
    print("Creating simple harmonization...")
    
    # Create harmonized sequence
    harmonized_sequence = NoteSequence()
    harmonized_sequence.ticks_per_quarter = melody_sequence.ticks_per_quarter
    harmonized_sequence.tempos.add(qpm=120)
    
    # Copy melody notes
    for note in melody_sequence.notes:
        new_note = harmonized_sequence.notes.add()
        new_note.CopyFrom(note)
        new_note.instrument = 0  # Melody voice
        new_note.velocity = 100  # Stronger melody
    
    # Add harmony for each melody note
    for i, melody_note in enumerate(melody_sequence.notes):
        # Get chord for this melody note
        chord_pitches = get_chord_for_note(melody_note.pitch)
        
        # Add chord notes (avoiding the melody note)
        for j, pitch in enumerate(chord_pitches):
            if pitch != melody_note.pitch:  # Don't duplicate melody note
                harmony_note = harmonized_sequence.notes.add()
                harmony_note.pitch = pitch
                harmony_note.start_time = melody_note.start_time
                harmony_note.end_time = melody_note.end_time
                harmony_note.velocity = 60  # Softer harmony
                harmony_note.instrument = j + 1  # Different instrument for each harmony voice
    
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
        note_seq.note_sequence_to_midi_file(melody_sequence, "realms2_melody.mid")
        print("Saved extracted melody to: realms2_melody.mid")
        
        # Create simple harmonization
        harmonized_sequence = harmonize_melody_simple(
            melody_sequence=melody_sequence,
            output_path="realms2_simple_harmonized.mid"
        )
        
        print("\nSimple harmonization complete!")
        print("Files created:")
        print("- realms2_melody.mid: Extracted melody")
        print("- realms2_simple_harmonized.mid: Simple harmonized version")
        
        # Also create a version with the RL system (if available)
        try:
            print("\nAttempting RL harmonization...")
            from harmonize_custom_melody import harmonize_melody
            
            rl_harmonized = harmonize_melody(
                melody_sequence=melody_sequence,
                model_path="trained_harmonization_model",
                num_voices=3,
                output_path="realms2_rl_harmonized.mid"
            )
            print("- realms2_rl_harmonized.mid: RL harmonized version")
            
        except Exception as e:
            print(f"RL harmonization not available: {e}")
        
    except Exception as e:
        print(f"Error during harmonization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 