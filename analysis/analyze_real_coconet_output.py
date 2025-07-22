#!/usr/bin/env python3

import pretty_midi
import numpy as np
import matplotlib.pyplot as plt

def analyze_midi_file(filepath, title):
    """Analyze a MIDI file and print detailed information"""
    try:
        midi_data = pretty_midi.PrettyMIDI(filepath)
        print(f"\n=== {title} ===")
        print(f"File: {filepath}")
        print(f"Duration: {midi_data.get_end_time():.2f} seconds")
        print(f"Tempo: {midi_data.estimate_tempo():.1f} BPM")
        print(f"Key: {midi_data.key_signature_changes}")
        print(f"Time signature: {midi_data.time_signature_changes}")
        
        total_notes = 0
        for i, instrument in enumerate(midi_data.instruments):
            print(f"\nTrack {i+1}: {instrument.name}")
            print(f"  Program: {instrument.program}")
            print(f"  Notes: {len(instrument.notes)}")
            if instrument.notes:
                pitches = [note.pitch for note in instrument.notes]
                velocities = [note.velocity for note in instrument.notes]
                print(f"  Pitch range: {min(pitches)} - {max(pitches)} ({len(set(pitches))} unique)")
                print(f"  Velocity range: {min(velocities)} - {max(velocities)}")
                print(f"  Average velocity: {np.mean(velocities):.1f}")
                total_notes += len(instrument.notes)
        
        print(f"\nTotal notes across all tracks: {total_notes}")
        return midi_data
        
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return None

def compare_harmonizations():
    """Compare the input melody with the Coconet harmonization"""
    
    # Analyze input melody
    input_midi = analyze_midi_file("../midi_files/realms2_idea.midi", "Input Melody")
    
    # Analyze Coconet harmonization
    coconet_midi = analyze_midi_file("../midi_files/final_real_coconet_harmonization.mid", "Coconet Harmonization")
    
    if input_midi and coconet_midi:
        print("\n=== COMPARISON ===")
        
        # Count notes in each track
        input_notes = sum(len(instrument.notes) for instrument in input_midi.instruments)
        coconet_notes = sum(len(instrument.notes) for instrument in coconet_midi.instruments)
        
        print(f"Input melody notes: {input_notes}")
        print(f"Coconet harmonization notes: {coconet_notes}")
        print(f"Expansion factor: {coconet_notes/input_notes:.1f}x")
        
        # Check if we have 4-part harmonization (SATB)
        if len(coconet_midi.instruments) >= 4:
            print(f"\n✅ 4-part harmonization detected ({len(coconet_midi.instruments)} tracks)")
            
            # Analyze each voice
            voice_names = ["Soprano", "Alto", "Tenor", "Bass"]
            for i in range(min(4, len(coconet_midi.instruments))):
                instrument = coconet_midi.instruments[i]
                if instrument.notes:
                    pitches = [note.pitch for note in instrument.notes]
                    print(f"{voice_names[i]}: {min(pitches)}-{max(pitches)} ({len(pitches)} notes)")
        else:
            print(f"\n⚠️  Expected 4-part harmonization, got {len(coconet_midi.instruments)} tracks")

if __name__ == "__main__":
    compare_harmonizations() 