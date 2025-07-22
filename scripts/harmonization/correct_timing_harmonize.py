#!/usr/bin/env python3
"""
Generate harmonization with correct MIDI timing
"""

import mido
from midiutil import MIDIFile
import os

def load_midi_with_correct_timing(midi_file):
    """Load MIDI with correct timing"""
    try:
        mid = mido.MidiFile(midi_file)
        print(f"Loading {midi_file}")
        print(f"Ticks per beat: {mid.ticks_per_beat}")
        print(f"Tempo: 160 BPM")
        
        # Find tempo (default to 160 BPM if not found)
        tempo = 500000  # microseconds per beat (120 BPM)
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    break
        
        bpm = mido.tempo2bpm(tempo)
        print(f"Actual tempo: {bpm} BPM")
        
        notes = []
        
        # Process each track
        for track_num, track in enumerate(mid.tracks):
            current_time = 0
            track_notes = []
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    track_notes.append({
                        'note': msg.note,
                        'start_time': current_time,
                        'velocity': msg.velocity,
                        'duration': 0  # Will be calculated
                    })
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Find corresponding note_on
                    for note in reversed(track_notes):
                        if note['note'] == msg.note and note['duration'] == 0:
                            note['duration'] = current_time - note['start_time']
                            break
            
            # Filter valid notes
            track_notes = [note for note in track_notes if note['duration'] > 0]
            if track_notes:
                print(f"Track {track_num}: {len(track_notes)} notes")
                notes.extend(track_notes)
        
        # Sort by start time
        notes.sort(key=lambda x: x['start_time'])
        
        print(f"Total notes: {len(notes)}")
        
        # Show timing info
        for i, note in enumerate(notes[:5]):
            start_seconds = mido.tick2second(note['start_time'], mid.ticks_per_beat, tempo)
            duration_seconds = mido.tick2second(note['duration'], mid.ticks_per_beat, tempo)
            print(f"  Note {i}: MIDI {note['note']} at {start_seconds:.2f}s for {duration_seconds:.2f}s")
        
        return notes, mid.ticks_per_beat, tempo
        
    except Exception as e:
        print(f"Error loading MIDI: {e}")
        return None, None, None

def generate_harmony_notes(melody_notes):
    """Generate harmony notes"""
    print("Generating harmony notes...")
    
    harmony_notes = []
    
    for i, melody_note in enumerate(melody_notes):
        # Simple harmonization: add a third below the melody note
        harmony_note = melody_note['note'] - 3  # Minor third below
        
        # Ensure harmony note is in valid MIDI range
        if harmony_note < 21:  # Below A0
            harmony_note = melody_note['note'] + 5  # Perfect fourth above
        
        harmony_notes.append({
            'note': harmony_note,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        
        print(f"Melody {melody_note['note']} -> Harmony {harmony_note}")
    
    return harmony_notes

def save_harmonization_with_correct_timing(melody_notes, harmony_notes, output_file, ticks_per_beat):
    """Save harmonization with correct MIDI timing"""
    try:
        print(f"Saving harmonization to {output_file}")
        
        # Create MIDI file
        midi = MIDIFile(2)
        
        # Track 0: Original melody
        midi.addTempo(0, 0, 160)  # 160 BPM
        for note in melody_notes:
            # Convert ticks to beats
            start_beat = note['start_time'] / ticks_per_beat
            duration_beat = note['duration'] / ticks_per_beat
            midi.addNote(0, 0, note['note'], start_beat, duration_beat, note['velocity'])
        
        # Track 1: Generated harmony
        midi.addTempo(1, 0, 160)
        for harmony_note in harmony_notes:
            start_beat = harmony_note['start_time'] / ticks_per_beat
            duration_beat = harmony_note['duration'] / ticks_per_beat
            midi.addNote(1, 0, harmony_note['note'], start_beat, duration_beat, 80)
        
        # Write file
        with open(output_file, 'wb') as f:
            midi.writeFile(f)
        
        print(f"✅ Harmonization saved: {output_file}")
        print(f"   - Preserved original timing and durations")
        print(f"   - Track 0: Original melody ({len(melody_notes)} notes)")
        print(f"   - Track 1: Generated harmony ({len(harmony_notes)} notes)")
        return True
        
    except Exception as e:
        print(f"Error saving MIDI: {e}")
        return False

def main():
    """Main function"""
    print("🎵 CORRECT TIMING HARMONIZATION")
    print("=" * 40)
    
    # Load melody with correct timing
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return
    
    melody_notes, ticks_per_beat, tempo = load_midi_with_correct_timing(melody_file)
    if not melody_notes:
        print("❌ Failed to load melody")
        return
    
    # Generate harmony
    harmony_notes = generate_harmony_notes(melody_notes)
    
    # Save result with correct timing
    output_file = "realms2_correct_timing_harmonized.mid"
    success = save_harmonization_with_correct_timing(melody_notes, harmony_notes, output_file, ticks_per_beat)
    
    if success:
        print(f"\n🎉 HARMONIZATION COMPLETE!")
        print(f"Input: {melody_file}")
        print(f"Output: {output_file}")
        print(f"Melody notes: {len(melody_notes)}")
        print(f"Harmony notes: {len(harmony_notes)}")
        print(f"Tempo: 160 BPM")
        print(f"Ticks per beat: {ticks_per_beat}")
        print(f"\nYou can now play {output_file} to hear the harmonization!")
        print(f"This version preserves the original timing and note durations.")
    else:
        print("❌ Failed to save harmonization")

if __name__ == "__main__":
    main() 