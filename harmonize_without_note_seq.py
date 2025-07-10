#!/usr/bin/env python3
"""
MIDI Harmonization Script (without note_seq dependency)

This script loads a MIDI file and creates harmonization using basic music theory,
avoiding the note_seq dependency that has protobuf issues.
"""

import os
import sys
import numpy as np
from midiutil import MIDIFile
import mido

def load_midi_melody(midi_path: str):
    """
    Load a MIDI file and extract the melody using mido.
    
    Args:
        midi_path: Path to the MIDI file
        
    Returns:
        List of (time, pitch, duration) tuples
    """
    print(f"Loading MIDI file: {midi_path}")
    
    mid = mido.MidiFile(midi_path)
    print(f"Loaded MIDI with {len(mid.tracks)} tracks")
    
    # Extract all notes
    notes = []
    current_time = 0
    
    for track in mid.tracks:
        track_time = 0
        for msg in track:
            track_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                # Convert ticks to seconds
                time_seconds = mido.tick2second(track_time, mid.ticks_per_beat, mido.bpm2tempo(120))
                notes.append({
                    'time': time_seconds,
                    'pitch': msg.note,
                    'velocity': msg.velocity,
                    'channel': msg.channel
                })
    
    print(f"Found {len(notes)} notes")
    
    # Extract melody (highest notes at each time point)
    melody_notes = []
    
    # Group notes by time
    time_notes = {}
    for note in notes:
        time_key = round(note['time'], 2)
        if time_key not in time_notes:
            time_notes[time_key] = []
        time_notes[time_key].append(note)
    
    # For each time point, take the highest note as melody
    for time_point in sorted(time_notes.keys()):
        notes_at_time = time_notes[time_point]
        notes_at_time.sort(key=lambda x: x['pitch'], reverse=True)
        melody_notes.append(notes_at_time[0])
    
    print(f"Extracted {len(melody_notes)} melody notes")
    
    return melody_notes, mid.ticks_per_beat

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

def create_harmonized_midi(melody_notes, ticks_per_beat, output_path: str):
    """
    Create a harmonized MIDI file.
    
    Args:
        melody_notes: List of melody note dictionaries
        ticks_per_beat: MIDI ticks per beat
        output_path: Output MIDI file path
    """
    print("Creating harmonized MIDI...")
    
    # Create MIDI file
    midi = MIDIFile(1)  # 1 track
    track = 0
    time_pos = 0
    channel = 0
    volume = 100
    duration = 1  # 1 beat duration
    
    # Set tempo
    midi.addTempo(track, time_pos, 120)
    
    # Add melody notes (track 0)
    for note in melody_notes:
        midi.addNote(track, channel, note['pitch'], 
                    int(note['time'] * 4), duration, volume)
    
    # Add harmony notes (tracks 1-3)
    for i, note in enumerate(melody_notes):
        chord_pitches = get_chord_for_note(note['pitch'])
        
        # Add chord notes (avoiding the melody note)
        for j, pitch in enumerate(chord_pitches):
            if pitch != note['pitch']:  # Don't duplicate melody note
                midi.addNote(track, j + 1, pitch,  # Different channel for each harmony voice
                           int(note['time'] * 4), duration, 60)  # Softer harmony
    
    # Write MIDI file
    with open(output_path, "wb") as output_file:
        midi.writeFile(output_file)
    
    print(f"Saved harmonized MIDI to: {output_path}")

def main():
    """Main function to harmonize the custom melody."""
    
    # Input MIDI file
    midi_path = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    
    if not os.path.exists(midi_path):
        print(f"Error: MIDI file not found at {midi_path}")
        return
    
    try:
        # Load melody
        melody_notes, ticks_per_beat = load_midi_melody(midi_path)
        
        # Create harmonized version
        create_harmonized_midi(
            melody_notes=melody_notes,
            ticks_per_beat=ticks_per_beat,
            output_path="realms2_harmonized.mid"
        )
        
        print("\nHarmonization complete!")
        print("Files created:")
        print("- realms2_harmonized.mid: Harmonized version")
        
    except Exception as e:
        print(f"Error during harmonization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 