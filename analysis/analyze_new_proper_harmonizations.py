#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_new_proper_harmonizations():
    """Analyze the new proper harmonizations with different temperatures"""
    print("🎼 NEW PROPER MELODY PRESERVING HARMONIZATIONS ANALYSIS")
    print("=" * 70)

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
        print(f"   Velocities: {[note['velocity'] for note in original_notes]}")

        # Analyze new harmonizations
        harmonization_files = [
            ("../midi_files/realms_proper_harmonization_v2.mid", 0.8),
            ("../midi_files/realms_proper_harmonization_v3.mid", 1.2),
            ("../midi_files/realms_proper_harmonization_v4.mid", 0.6),
            ("../midi_files/realms_proper_harmonization_v5.mid", 0.4),
            ("../midi_files/realms_proper_harmonization_v6.mid", 1.5)
        ]

        for filepath, temperature in harmonization_files:
            try:
                print(f"\n🎵 ANALYZING: {filepath} (Temperature: {temperature})")
                print("-" * 60)

                harmonized_midi = pretty_midi.PrettyMIDI(filepath)

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
                        else:
                            matches = sum(1 for o, h in zip(original_pitches, instrument_pitches) if o == h)
                            match_percentage = (matches / len(original_pitches)) * 100
                            print(f"      ❌ Partial match: {matches}/{len(original_pitches)} ({match_percentage:.1f}%)")

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
                print(f"   ❌ Error analyzing {filepath}: {e}")

        print(f"\n📋 SUMMARY:")
        print("=" * 70)
        print(f"Generated 5 new harmonizations with temperatures: 0.4, 0.6, 0.8, 1.2, 1.5")
        print(f"Check each file to see which produces the best musical result.")

    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_new_proper_harmonizations() 