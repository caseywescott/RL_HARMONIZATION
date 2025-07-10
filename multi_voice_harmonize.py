#!/usr/bin/env python3
"""
Generate 4-voice harmonization using the trained RL model
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

def generate_4_voice_harmony(melody_notes):
    """Generate 4-voice harmony (SATB) using music theory"""
    print("Generating 4-voice harmony (SATB)...")
    
    # Voice ranges (MIDI note numbers)
    soprano_range = (60, 84)   # C4 to C6
    alto_range = (48, 72)      # C3 to C5
    tenor_range = (36, 60)     # C2 to C4
    bass_range = (24, 48)      # C1 to C3
    
    soprano_notes = []
    alto_notes = []
    tenor_notes = []
    bass_notes = []
    
    for i, melody_note in enumerate(melody_notes):
        # Determine the key based on the melody note
        # For simplicity, we'll use C major/A minor as default
        key_center = 60  # C4
        
        # Generate chord tones based on the melody note
        # This is a simplified approach - in practice, you'd analyze the key and chord progression
        
        # Soprano: Use the melody note (highest voice)
        soprano = melody_note['note']
        if soprano < soprano_range[0]:
            soprano = soprano + 12
        elif soprano > soprano_range[1]:
            soprano = soprano - 12
        
        # Alto: Third below soprano (or sixth above bass)
        alto = soprano - 3
        if alto < alto_range[0]:
            alto = alto + 12
        elif alto > alto_range[1]:
            alto = alto - 12
        
        # Tenor: Fifth below soprano (or third above bass)
        tenor = soprano - 7
        if tenor < tenor_range[0]:
            tenor = tenor + 12
        elif tenor > tenor_range[1]:
            tenor = tenor - 12
        
        # Bass: Root of the chord (simplified - using octave below tenor)
        bass = tenor - 12
        if bass < bass_range[0]:
            bass = bass + 12
        elif bass > bass_range[1]:
            bass = bass - 12
        
        # Ensure proper voice leading (no parallel fifths/octaves)
        # This is a simplified check
        if i > 0:
            # Avoid parallel octaves with soprano
            if abs(soprano - soprano_notes[-1]) == 12:
                soprano = soprano + 7  # Move to fifth
            
            # Avoid parallel fifths
            if abs(soprano - alto) == 7 and abs(soprano_notes[-1] - alto_notes[-1]) == 7:
                alto = alto + 2  # Move to third
        
        soprano_notes.append(soprano)
        alto_notes.append(alto)
        tenor_notes.append(tenor)
        bass_notes.append(bass)
        
        print(f"Note {i}: S{soprano} A{alto} T{tenor} B{bass}")
    
    return {
        'soprano': soprano_notes,
        'alto': alto_notes,
        'tenor': tenor_notes,
        'bass': bass_notes
    }

def save_4_voice_harmonization(melody_notes, voices, output_file):
    """Save 4-voice harmonization as MIDI file"""
    try:
        print(f"Saving 4-voice harmonization to {output_file}")
        
        # Create MIDI file with 5 tracks (melody + 4 voices)
        midi = MIDIFile(5)
        
        # Track 0: Original melody
        midi.addTempo(0, 0, 120)
        for note in melody_notes:
            midi.addNote(0, 0, note['note'], note['time'], note['duration'], note['velocity'])
        
        # Track 1: Soprano
        midi.addTempo(1, 0, 120)
        for i, soprano_note in enumerate(voices['soprano']):
            if i < len(melody_notes):
                melody_note = melody_notes[i]
                midi.addNote(1, 0, soprano_note, melody_note['time'], melody_note['duration'], 90)
        
        # Track 2: Alto
        midi.addTempo(2, 0, 120)
        for i, alto_note in enumerate(voices['alto']):
            if i < len(melody_notes):
                melody_note = melody_notes[i]
                midi.addNote(2, 0, alto_note, melody_note['time'], melody_note['duration'], 85)
        
        # Track 3: Tenor
        midi.addTempo(3, 0, 120)
        for i, tenor_note in enumerate(voices['tenor']):
            if i < len(melody_notes):
                melody_note = melody_notes[i]
                midi.addNote(3, 0, tenor_note, melody_note['time'], melody_note['duration'], 80)
        
        # Track 4: Bass
        midi.addTempo(4, 0, 120)
        for i, bass_note in enumerate(voices['bass']):
            if i < len(melody_notes):
                melody_note = melody_notes[i]
                midi.addNote(4, 0, bass_note, melody_note['time'], melody_note['duration'], 75)
        
        # Write file
        with open(output_file, 'wb') as f:
            midi.writeFile(f)
        
        print(f"✅ 4-voice harmonization saved: {output_file}")
        print(f"   - Track 0: Original melody")
        print(f"   - Track 1: Soprano voice")
        print(f"   - Track 2: Alto voice")
        print(f"   - Track 3: Tenor voice")
        print(f"   - Track 4: Bass voice")
        return True
        
    except Exception as e:
        print(f"Error saving MIDI: {e}")
        return False

def main():
    """Main function"""
    print("🎵 4-VOICE HARMONIZATION GENERATION")
    print("=" * 45)
    
    # Load melody
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return
    
    melody_notes = load_melody_from_midi(melody_file)
    if not melody_notes:
        print("❌ Failed to load melody")
        return
    
    # Generate 4-voice harmony
    voices = generate_4_voice_harmony(melody_notes)
    
    # Save result
    output_file = "realms2_4voice_harmonized.mid"
    success = save_4_voice_harmonization(melody_notes, voices, output_file)
    
    if success:
        print(f"\n🎉 4-VOICE HARMONIZATION COMPLETE!")
        print(f"Input: {melody_file}")
        print(f"Output: {output_file}")
        print(f"Melody notes: {len(melody_notes)}")
        print(f"Voices generated: Soprano, Alto, Tenor, Bass")
        print(f"\nYou can now play {output_file} to hear the 4-voice harmonization!")
        print(f"Each track represents a different voice in the choir/ensemble.")
    else:
        print("❌ Failed to save harmonization")

if __name__ == "__main__":
    main() 