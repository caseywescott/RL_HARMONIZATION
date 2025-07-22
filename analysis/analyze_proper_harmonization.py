#!/usr/bin/env python3
"""
Analyze Proper Coconet Harmonization

Compare the new proper harmonization with the working example
"""

import pretty_midi
import numpy as np

def analyze_midi_file(filename, description):
    """Analyze a MIDI file and print its characteristics"""
    print(f"\n🔍 ANALYZING: {description}")
    print("=" * 50)
    
    try:
        midi = pretty_midi.PrettyMIDI(filename)
        print(f"✅ File loaded successfully")
        print(f"📊 Number of instruments: {len(midi.instruments)}")
        print(f"📊 Total duration: {midi.get_end_time():.2f} seconds")
        print(f"📊 Tempo: {midi.estimate_tempo():.1f} BPM")
        
        # Analyze each instrument
        for i, instrument in enumerate(midi.instruments):
            print(f"\n🎵 Instrument {i}: {instrument.name}")
            print(f"   Program: {instrument.program}")
            print(f"   Number of notes: {len(instrument.notes)}")
            
            if instrument.notes:
                pitches = [note.pitch for note in instrument.notes]
                velocities = [note.velocity for note in instrument.notes]
                durations = [note.end - note.start for note in instrument.notes]
                
                print(f"   Pitch range: {min(pitches)} - {max(pitches)}")
                print(f"   Average velocity: {np.mean(velocities):.1f}")
                print(f"   Average duration: {np.mean(durations):.3f} seconds")
                
                # Check for repeated patterns
                unique_pitches = len(set(pitches))
                print(f"   Unique pitches: {unique_pitches}")
                
                if unique_pitches < 5:
                    print(f"   ⚠️  WARNING: Very few unique pitches - may be repetitive!")
                
                # Check timing
                start_times = [note.start for note in instrument.notes]
                if len(start_times) > 1:
                    intervals = np.diff(sorted(start_times))
                    print(f"   Average interval between notes: {np.mean(intervals):.3f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing {filename}: {e}")
        return False

def compare_harmonizations():
    """Compare different harmonization outputs"""
    print("🎵 PROPER HARMONIZATION COMPARISON")
    print("=" * 60)
    
    # Files to compare
    files = [
        ("../midi_files/realms2_idea.midi", "Original Melody"),
        ("../midi_files/coconet_harmonized_realms2.mid", "Working Coconet Harmonization"),
        ("../midi_files/final_proper_harmonization.mid", "Final Proper Coconet Output"),
        ("../midi_files/test_docker_coconet.mid", "Broken Docker Output")
    ]
    
    results = {}
    
    for filename, description in files:
        try:
            if analyze_midi_file(filename, description):
                results[description] = "✅ Success"
            else:
                results[description] = "❌ Failed"
        except Exception as e:
            print(f"❌ Error with {filename}: {e}")
            results[description] = "❌ Error"
    
    print(f"\n📋 SUMMARY:")
    print("=" * 30)
    for description, status in results.items():
        print(f"  {description}: {status}")

if __name__ == "__main__":
    compare_harmonizations() 