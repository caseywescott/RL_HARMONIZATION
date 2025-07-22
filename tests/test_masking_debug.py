#!/usr/bin/env python3

import pretty_midi
import numpy as np

def test_masking_debug():
    """Debug the masking logic to understand why melody isn't preserved"""
    print("🔍 MASKING DEBUG ANALYSIS")
    print("=" * 50)

    try:
        # Load original melody
        original_midi = pretty_midi.PrettyMIDI("realms2_idea.midi")
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

        # Check all harmonization files
        harmonization_files = [
            "realms_proper_harmonization_v2.mid",
            "realms_proper_harmonization_v3.mid", 
            "realms_proper_harmonization_v4.mid",
            "realms_proper_harmonization_v5.mid",
            "realms_proper_harmonization_v6.mid"
        ]

        print(f"\n🔍 SEARCHING FOR ORIGINAL MELODY IN ALL HARMONIZATIONS:")
        print("-" * 50)

        for filepath in harmonization_files:
            try:
                harmonized_midi = pretty_midi.PrettyMIDI(filepath)
                print(f"\n📁 {filepath}:")
                
                # Search all instruments for the original melody
                found_melody = False
                for i, instrument in enumerate(harmonized_midi.instruments):
                    instrument_notes = []
                    for note in instrument.notes:
                        instrument_notes.append({
                            'pitch': note.pitch,
                            'start': note.start,
                            'end': note.end,
                            'velocity': note.velocity
                        })

                    # Check if this instrument has the same number of notes
                    if len(instrument_notes) == len(original_notes):
                        original_pitches = [note['pitch'] for note in original_notes]
                        instrument_pitches = [note['pitch'] for note in instrument_notes]

                        if original_pitches == instrument_pitches:
                            print(f"   ✅ ORIGINAL MELODY FOUND in instrument {i}!")
                            found_melody = True
                        else:
                            # Check for partial matches
                            matches = sum(1 for o, h in zip(original_pitches, instrument_pitches) if o == h)
                            if matches > 0:
                                match_percentage = (matches / len(original_pitches)) * 100
                                print(f"   ⚠️  Partial match in instrument {i}: {matches}/{len(original_pitches)} ({match_percentage:.1f}%)")
                                print(f"      Original: {original_pitches}")
                                print(f"      Found:    {instrument_pitches}")

                if not found_melody:
                    print(f"   ❌ Original melody NOT found in any instrument")

                # Check if any instrument has similar pitch patterns
                print(f"   🔍 Checking for similar pitch patterns...")
                for i, instrument in enumerate(harmonized_midi.instruments):
                    if len(instrument.notes) > 0:
                        pitches = [note.pitch for note in instrument.notes]
                        # Check if any original melody pitches appear in this instrument
                        common_pitches = set(original_pitches) & set(pitches)
                        if len(common_pitches) > 0:
                            print(f"      Instrument {i}: {len(common_pitches)} common pitches: {sorted(common_pitches)}")

            except Exception as e:
                print(f"   ❌ Error analyzing {filepath}: {e}")

        print(f"\n📋 CONCLUSION:")
        print("=" * 50)
        print(f"The original melody is not being preserved in any harmonization.")
        print(f"This suggests the masking logic in our proper solution is still not working correctly.")
        print(f"We may need to investigate the Coconet source code more deeply or try a different approach.")

    except Exception as e:
        print(f"❌ Error in debug analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_masking_debug() 