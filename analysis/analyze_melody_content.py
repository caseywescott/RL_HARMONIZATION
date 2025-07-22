#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_melody_content():
    """Analyze if the original melody content is actually present in harmonizations"""
    print("🎼 MELODY CONTENT ANALYSIS")
    print("=" * 60)
    
    try:
        # Load original melody
        original_midi = pretty_midi.PrettyMIDI("../midi_files/realms2_idea.midi")
        original_notes = []
        
        if original_midi.instruments:
            for note in original_midi.instruments[0].notes:
                original_notes.append({
                    'pitch': note.pitch,
                    'start': note.start,
                    'end': note.end,
                    'velocity': note.velocity
                })
        
        print(f"📊 ORIGINAL MELODY:")
        print(f"   Notes: {len(original_notes)}")
        print(f"   Pitches: {[note['pitch'] for note in original_notes]}")
        print(f"   Duration: {original_midi.get_end_time():.2f} seconds")
        
        # Analyze harmonizations
        harmonization_files = [
            "../midi_files/realms_fixed_harmonization_v1.mid",
            "../midi_files/realms_fixed_harmonization_v2.mid", 
            "../midi_files/realms_fixed_harmonization_v3.mid",
            "../midi_files/melody_preserved_harmonization.mid",
            "../midi_files/melody_preserved_v2.mid",
            "../midi_files/melody_preserved_v3.mid"
        ]
        
        for filepath in harmonization_files:
            try:
                print(f"\n🎵 ANALYZING: {filepath}")
                print("-" * 50)
                
                harmonized_midi = pretty_midi.PrettyMIDI(filepath)
                
                if not harmonized_midi.instruments:
                    print(f"   ❌ No instruments found")
                    continue
                
                # Check first instrument (should be melody)
                melody_track = harmonized_midi.instruments[0]
                harmonized_notes = []
                
                for note in melody_track.notes:
                    harmonized_notes.append({
                        'pitch': note.pitch,
                        'start': note.start,
                        'end': note.end,
                        'velocity': note.velocity
                    })
                
                print(f"   📊 Harmonized melody track:")
                print(f"      Notes: {len(harmonized_notes)}")
                print(f"      Pitches: {[note['pitch'] for note in harmonized_notes]}")
                
                # Compare with original
                if len(harmonized_notes) == len(original_notes):
                    print(f"   ✅ Same number of notes")
                    
                    # Check if pitches match
                    original_pitches = [note['pitch'] for note in original_notes]
                    harmonized_pitches = [note['pitch'] for note in harmonized_notes]
                    
                    if original_pitches == harmonized_pitches:
                        print(f"   ✅ PITCHES MATCH EXACTLY!")
                        print(f"   🎵 Original melody is preserved in harmonization")
                    else:
                        print(f"   ❌ PITCHES DO NOT MATCH")
                        print(f"   Original: {original_pitches}")
                        print(f"   Harmonized: {harmonized_pitches}")
                        
                        # Check how many match
                        matches = sum(1 for o, h in zip(original_pitches, harmonized_pitches) if o == h)
                        match_percentage = (matches / len(original_pitches)) * 100
                        print(f"   Match rate: {matches}/{len(original_pitches)} ({match_percentage:.1f}%)")
                else:
                    print(f"   ❌ Different number of notes")
                    print(f"   Original: {len(original_notes)}, Harmonized: {len(harmonized_notes)}")
                
                # Check all instruments for original melody
                print(f"   🔍 Searching all instruments for original melody...")
                found_in_instruments = []
                
                for i, instrument in enumerate(harmonized_midi.instruments):
                    instrument_notes = []
                    for note in instrument.notes:
                        instrument_notes.append({
                            'pitch': note.pitch,
                            'start': note.start,
                            'end': note.end,
                            'velocity': note.velocity
                        })
                    
                    if len(instrument_notes) == len(original_notes):
                        original_pitches = [note['pitch'] for note in original_notes]
                        instrument_pitches = [note['pitch'] for note in instrument_notes]
                        
                        if original_pitches == instrument_pitches:
                            found_in_instruments.append(i)
                
                if found_in_instruments:
                    print(f"   ✅ Original melody found in instruments: {found_in_instruments}")
                else:
                    print(f"   ❌ Original melody NOT found in any instrument")
                
            except Exception as e:
                print(f"   ❌ Error analyzing {filepath}: {e}")
        
        print(f"\n📋 SUMMARY:")
        print("=" * 60)
        print(f"Original melody has {len(original_notes)} notes with pitches: {[note['pitch'] for note in original_notes]}")
        print(f"Check each harmonization to see if this exact melody is preserved.")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_melody_content() 