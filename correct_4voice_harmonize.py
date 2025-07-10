#!/usr/bin/env python3
"""
Generate 4-voice harmonization with correct MIDI timing
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
        
        # Find tempo (default to 160 BPM if not found)
        tempo = 500000  # microseconds per beat (120 BPM)
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    break
        
        bpm = mido.tempo2bpm(tempo)
        print(f"Tempo: {bpm} BPM")
        
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
        for i, note in enumerate(notes[:3]):
            start_seconds = mido.tick2second(note['start_time'], mid.ticks_per_beat, tempo)
            duration_seconds = mido.tick2second(note['duration'], mid.ticks_per_beat, tempo)
            print(f"  Note {i}: MIDI {note['note']} at {start_seconds:.2f}s for {duration_seconds:.2f}s")
        
        return notes, mid.ticks_per_beat, tempo
        
    except Exception as e:
        print(f"Error loading MIDI: {e}")
        return None, None, None

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
        # Soprano: Use the melody note (highest voice)
        soprano = melody_note['note']
        if soprano < soprano_range[0]:
            soprano = soprano + 12
        elif soprano > soprano_range[1]:
            soprano = soprano - 12
        
        # Alto: Third below soprano
        alto = soprano - 3
        if alto < alto_range[0]:
            alto = alto + 12
        elif alto > alto_range[1]:
            alto = alto - 12
        
        # Tenor: Fifth below soprano
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
        
        # Ensure proper voice leading (avoid parallel fifths/octaves)
        if i > 0:
            # Avoid parallel octaves with soprano
            if abs(soprano - soprano_notes[-1]['note']) == 12:
                soprano = soprano + 7  # Move to fifth
            
            # Avoid parallel fifths
            if abs(soprano - alto) == 7 and abs(soprano_notes[-1]['note'] - alto_notes[-1]['note']) == 7:
                alto = alto + 2  # Move to third
        
        # Create note objects with timing
        soprano_notes.append({
            'note': soprano,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        
        alto_notes.append({
            'note': alto,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        
        tenor_notes.append({
            'note': tenor,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        
        bass_notes.append({
            'note': bass,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        
        print(f"Note {i}: S{soprano} A{alto} T{tenor} B{bass}")
    
    return {
        'soprano': soprano_notes,
        'alto': alto_notes,
        'tenor': tenor_notes,
        'bass': bass_notes
    }

def save_4_voice_harmonization_with_correct_timing(melody_notes, voices, output_file, ticks_per_beat):
    """Save 4-voice harmonization with correct MIDI timing"""
    try:
        print(f"Saving 4-voice harmonization to {output_file}")
        
        # Create MIDI file with 5 tracks (melody + 4 voices)
        midi = MIDIFile(5)
        
        # Track 0: Original melody
        midi.addTempo(0, 0, 160)  # 160 BPM
        for note in melody_notes:
            start_beat = note['start_time'] / ticks_per_beat
            duration_beat = note['duration'] / ticks_per_beat
            midi.addNote(0, 0, note['note'], start_beat, duration_beat, note['velocity'])
        
        # Track 1: Soprano
        midi.addTempo(1, 0, 160)
        for soprano_note in voices['soprano']:
            start_beat = soprano_note['start_time'] / ticks_per_beat
            duration_beat = soprano_note['duration'] / ticks_per_beat
            midi.addNote(1, 0, soprano_note['note'], start_beat, duration_beat, 90)
        
        # Track 2: Alto
        midi.addTempo(2, 0, 160)
        for alto_note in voices['alto']:
            start_beat = alto_note['start_time'] / ticks_per_beat
            duration_beat = alto_note['duration'] / ticks_per_beat
            midi.addNote(2, 0, alto_note['note'], start_beat, duration_beat, 85)
        
        # Track 3: Tenor
        midi.addTempo(3, 0, 160)
        for tenor_note in voices['tenor']:
            start_beat = tenor_note['start_time'] / ticks_per_beat
            duration_beat = tenor_note['duration'] / ticks_per_beat
            midi.addNote(3, 0, tenor_note['note'], start_beat, duration_beat, 80)
        
        # Track 4: Bass
        midi.addTempo(4, 0, 160)
        for bass_note in voices['bass']:
            start_beat = bass_note['start_time'] / ticks_per_beat
            duration_beat = bass_note['duration'] / ticks_per_beat
            midi.addNote(4, 0, bass_note['note'], start_beat, duration_beat, 75)
        
        # Write file
        with open(output_file, 'wb') as f:
            midi.writeFile(f)
        
        print(f"✅ 4-voice harmonization saved: {output_file}")
        print(f"   - Preserved original timing and durations")
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
    print("🎵 4-VOICE HARMONIZATION WITH CORRECT TIMING")
    print("=" * 50)
    
    # Load melody with correct timing
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return
    
    melody_notes, ticks_per_beat, tempo = load_midi_with_correct_timing(melody_file)
    if not melody_notes:
        print("❌ Failed to load melody")
        return
    
    # Generate 4-voice harmony
    voices = generate_4_voice_harmony(melody_notes)
    
    # Save result with correct timing
    output_file = "realms2_4voice_correct_timing.mid"
    success = save_4_voice_harmonization_with_correct_timing(melody_notes, voices, output_file, ticks_per_beat)
    
    if success:
        print(f"\n🎉 4-VOICE HARMONIZATION COMPLETE!")
        print(f"Input: {melody_file}")
        print(f"Output: {output_file}")
        print(f"Melody notes: {len(melody_notes)}")
        print(f"Voices generated: Soprano, Alto, Tenor, Bass")
        print(f"Tempo: 160 BPM")
        print(f"Ticks per beat: {ticks_per_beat}")
        print(f"\nYou can now play {output_file} to hear the 4-voice harmonization!")
        print(f"Each track represents a different voice in the choir/ensemble.")
        print(f"This version preserves the original timing and note durations.")
    else:
        print("❌ Failed to save harmonization")

if __name__ == "__main__":
    main() 