#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_final_harmonizations():
    """Analyze the final harmonizations to check if melody is properly preserved"""
    print("🎼 FINAL HARMONIZATION ANALYSIS")
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

        # Analyze final harmonizations
        harmonization_files = [
            "../midi_files/realms_final_harmonization.mid",
            "../midi_files/realms_final_harmonization_v2.mid"
        ]
        
        for harmonization_file in harmonization_files:
            try:
                print(f"\n🎵 ANALYZING: {harmonization_file}")
                print("-" * 50)

                harmonized_midi = pretty_midi.PrettyMIDI(harmonization_file)

                if not harmonized_midi.instruments:
                    print(f"   ❌ No instruments found")
                    continue

                print(f"   📊 Duration: {harmonized_midi.get_end_time():.2f} seconds")
                print(f"   📊 Tempo: {harmonized_midi.estimate_tempo():.1f} BPM")

                # Check each instrument
                for i, instrument in enumerate(harmonized_midi.instruments):
                    instrument_notes = []
                    for note in instrument.notes:
                        instrument_notes.append({
                            'pitch': note.pitch,
                            'start': note.start,
                            'end': note.end,
                            'velocity': note.velocity
                        })

                    print(f"   Instrument {i}: {len(instrument_notes)} notes")
                    if instrument_notes:
                        print(f"      Pitches: {[note['pitch'] for note in instrument_notes]}")
                        print(f"      Velocities: {[note['velocity'] for note in instrument_notes]}")

                    # Check if this instrument contains the original melody
                    if len(instrument_notes) == len(original_notes):
                        original_pitches = [note['pitch'] for note in original_notes]
                        instrument_pitches = [note['pitch'] for note in instrument_notes]

                        if original_pitches == instrument_pitches:
                            print(f"      ✅ ORIGINAL MELODY FOUND in instrument {i}!")
                            print(f"      🎵 Melody preservation is working!")
                        else:
                            matches = sum(1 for o, h in zip(original_pitches, instrument_pitches) if o == h)
                            match_percentage = (matches / len(original_pitches)) * 100
                            print(f"      ❌ Partial match: {matches}/{len(original_pitches)} ({match_percentage:.1f}%)")
                            print(f"      Original: {original_pitches}")
                            print(f"      Found:    {instrument_pitches}")

                # Check melody audibility (first instrument should be loudest)
                if len(harmonized_midi.instruments) >= 2:
                    melody_avg_vel = np.mean([note.velocity for note in harmonized_midi.instruments[0].notes]) if harmonized_midi.instruments[0].notes else 0
                    harmony_avg_vel = np.mean([note.velocity for note in harmonized_midi.instruments[1].notes]) if harmonized_midi.instruments[1].notes else 0
                    
                    print(f"   🎵 Melody audibility check:")
                    print(f"      Melody avg velocity: {melody_avg_vel:.1f}")
                    print(f"      Harmony avg velocity: {harmony_avg_vel:.1f}")
                    if melody_avg_vel > harmony_avg_vel:
                        print(f"      ✅ Melody should be audible")
                    else:
                        print(f"      ⚠️  Melody may not be prominent")

            except Exception as e:
                print(f"   ❌ Error analyzing {harmonization_file}: {e}")

        print(f"\n📋 SUMMARY:")
        print("=" * 60)
        print(f"Final harmonizations should preserve the original melody.")
        print(f"If melody is found in instrument 0, the final approach is working.")
        print(f"This approach addresses the core Coconet design issue where all parts")
        print(f"are treated as potentially modifiable unless explicitly constrained.")

    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_final_harmonizations() 