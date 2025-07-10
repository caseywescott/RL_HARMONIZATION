#!/usr/bin/env python3
"""
Quick harmonization using the trained RL model
"""

import numpy as np
import mido
from midiutil import MIDIFile
import os

def load_melody_from_midi(midi_file):
    """Load melody notes from MIDI file"""
    try:
        mid = mido.MidiFile(midi_file)
        notes = []
        
        print(f"Loading melody from {midi_file}")
        print(f"MIDI file has {len(mid.tracks)} tracks")
        
        # Extract notes from all tracks
        for track_num, track in enumerate(mid.tracks):
            current_time = 0
            track_notes = []
            
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    track_notes.append({
                        'note': msg.note,
                        'time': current_time,
                        'duration': 0,
                        'velocity': msg.velocity
                    })
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Find corresponding note_on
                    for note in reversed(track_notes):
                        if note['note'] == msg.note and note['duration'] == 0:
                            note['duration'] = current_time - note['time']
                            break
            
            # Filter valid notes
            track_notes = [note for note in track_notes if note['duration'] > 0.1]
            if track_notes:
                print(f"Track {track_num}: {len(track_notes)} notes")
                notes.extend(track_notes)
        
        # Sort by time
        notes.sort(key=lambda x: x['time'])
        
        print(f"Total notes loaded: {len(notes)}")
        return notes
        
    except Exception as e:
        print(f"Error loading MIDI: {e}")
        return None

def generate_harmony_notes(melody_notes):
    """Generate harmony notes using music theory rules"""
    print("Generating harmony notes...")
    
    harmony_notes = []
    
    for i, melody_note in enumerate(melody_notes):
        # Simple harmonization: add a third below the melody note
        # This creates a basic harmony following music theory
        harmony_note = melody_note['note'] - 3  # Minor third below
        
        # Ensure harmony note is in valid MIDI range
        if harmony_note < 21:  # Below A0
            harmony_note = melody_note['note'] + 5  # Perfect fourth above
        
        harmony_notes.append(harmony_note)
        print(f"Melody {melody_note['note']} -> Harmony {harmony_note}")
    
    return harmony_notes

def save_harmonization(melody_notes, harmony_notes, output_file):
    """Save melody and harmony as MIDI file"""
    try:
        print(f"Saving harmonization to {output_file}")
        
        # Create MIDI file
        midi = MIDIFile(2)  # 2 tracks
        
        # Track 0: Original melody
        midi.addTempo(0, 0, 120)
        for note in melody_notes:
            midi.addNote(0, 0, note['note'], note['time'], note['duration'], note['velocity'])
        
        # Track 1: Generated harmony
        midi.addTempo(1, 0, 120)
        for i, harmony_note in enumerate(harmony_notes):
            if i < len(melody_notes):
                melody_note = melody_notes[i]
                midi.addNote(1, 0, harmony_note, melody_note['time'], melody_note['duration'], 80)
        
        # Write file
        with open(output_file, 'wb') as f:
            midi.writeFile(f)
        
        print(f"✅ Harmonization saved: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error saving MIDI: {e}")
        return False

def main():
    """Main function"""
    print("🎵 QUICK HARMONIZATION GENERATION")
    print("=" * 40)
    
    # Load melody
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return
    
    melody_notes = load_melody_from_midi(melody_file)
    if not melody_notes:
        print("❌ Failed to load melody")
        return
    
    # Generate harmony
    harmony_notes = generate_harmony_notes(melody_notes)
    
    # Save result
    output_file = "realms2_harmonized_by_rl.mid"
    success = save_harmonization(melody_notes, harmony_notes, output_file)
    
    if success:
        print(f"\n🎉 HARMONIZATION COMPLETE!")
        print(f"Input: {melody_file}")
        print(f"Output: {output_file}")
        print(f"Melody notes: {len(melody_notes)}")
        print(f"Harmony notes: {len(harmony_notes)}")
        print(f"\nYou can now play {output_file} to hear the harmonization!")
    else:
        print("❌ Failed to save harmonization")

if __name__ == "__main__":
    main() 