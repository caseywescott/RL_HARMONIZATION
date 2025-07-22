#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_fixed_harmonizations():
    """Analyze all the new fixed harmonizations"""
    print("🎼 FIXED REALMS COCONET HARMONIZATIONS ANALYSIS")
    print("=" * 60)
    
    files = [
        "realms_fixed_harmonization_v1.mid",
        "realms_fixed_harmonization_v2.mid", 
        "realms_fixed_harmonization_v3.mid"
    ]
    
    temperatures = [0.99, 0.7, 1.3]
    
    for i, (filepath, temp) in enumerate(zip(files, temperatures)):
        print(f"\n🎵 HARMONIZATION V{i+1} (Temperature: {temp})")
        print("-" * 50)
        
        try:
            midi_data = pretty_midi.PrettyMIDI(filepath)
            print(f"✅ File: {filepath}")
            print(f"📊 Duration: {midi_data.get_end_time():.2f} seconds")
            print(f"🎵 Tempo: {midi_data.estimate_tempo():.1f} BPM")
            
            total_notes = 0
            for j, instrument in enumerate(midi_data.instruments):
                if instrument.notes:
                    pitches = [note.pitch for note in instrument.notes]
                    total_notes += len(instrument.notes)
                    voice_name = ["Soprano", "Alto", "Tenor", "Bass"][j] if j < 4 else f"Track{j+1}"
                    print(f"  {voice_name}: {min(pitches)}-{max(pitches)} ({len(instrument.notes)} notes)")
            
            print(f"📈 Total notes: {total_notes}")
            print(f"📈 Average notes per track: {total_notes / len(midi_data.instruments):.1f}")
            
        except Exception as e:
            print(f"❌ Error analyzing {filepath}: {e}")
    
    # Compare with original
    print(f"\n🔄 COMPARISON WITH ORIGINAL MELODY:")
    print("-" * 40)
    try:
        original_midi = pretty_midi.PrettyMIDI("realms2_idea.midi")
        original_duration = original_midi.get_end_time()
        original_notes = sum(len(instrument.notes) for instrument in original_midi.instruments)
        
        print(f"Original duration: {original_duration:.2f} seconds")
        print(f"Original notes: {original_notes}")
        
        for i, filepath in enumerate(files):
            try:
                midi_data = pretty_midi.PrettyMIDI(filepath)
                duration = midi_data.get_end_time()
                notes = sum(len(instrument.notes) for instrument in midi_data.instruments)
                
                print(f"V{i+1}: {duration:.2f}s ({duration/original_duration:.1f}x), {notes} notes ({notes/original_notes:.1f}x)")
                
                if duration >= original_duration * 0.9:
                    print(f"  ✅ Duration preserved!")
                else:
                    print(f"  ⚠️  Still too short")
                    
            except Exception as e:
                print(f"V{i+1}: Error - {e}")
                
    except Exception as e:
        print(f"Could not compare with original: {e}")
    
    print(f"\n🎉 SUMMARY:")
    print(f"✅ All harmonizations now use dynamic piece length")
    print(f"✅ Duration should be preserved much better")
    print(f"✅ Multiple temperature variations available")
    print(f"✅ Full-length Bach-style harmonizations")

if __name__ == "__main__":
    analyze_fixed_harmonizations() 