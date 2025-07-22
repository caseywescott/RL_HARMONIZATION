#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_new_harmonizations():
    """Analyze the new harmonizations from both melody preservation solutions"""
    print("🎼 NEW MELODY PRESERVATION HARMONIZATIONS ANALYSIS")
    print("=" * 60)

    files = [
        "melody_copy_harmonization_fixed.mid",
        "fixed_masking_harmonization_fixed.mid"
    ]

    solution_names = [
        "Melody Copy-Over Solution",
        "Fixed Masking Solution"
    ]

    for i, (filepath, solution_name) in enumerate(zip(files, solution_names)):
        print(f"\n🎵 {solution_name.upper()}")
        print("-" * 50)

        try:
            midi_data = pretty_midi.PrettyMIDI(filepath)
            print(f"✅ File: {filepath}")
            print(f"📊 Duration: {midi_data.get_end_time():.2f} seconds")
            print(f"📊 Tempo: {midi_data.estimate_tempo():.1f} BPM")

            total_notes = 0
            for inst_idx, instrument in enumerate(midi_data.instruments):
                print(f"   Instrument {inst_idx}: {len(instrument.notes)} notes")
                total_notes += len(instrument.notes)
            print(f"   Total notes: {total_notes}")

            # Check if original melody is preserved
            if midi_data.instruments:
                melody_track = midi_data.instruments[0]
                print(f"   Melody track velocity range: {min([n.velocity for n in melody_track.notes])}-{max([n.velocity for n in melody_track.notes])}")
                
                if len(midi_data.instruments) > 1:
                    harmony_tracks = midi_data.instruments[1:]
                    harmony_velocities = []
                    for track in harmony_tracks:
                        harmony_velocities.extend([n.velocity for n in track.notes])
                    if harmony_velocities:
                        print(f"   Harmony tracks velocity range: {min(harmony_velocities)}-{max(harmony_velocities)}")

        except Exception as e:
            print(f"❌ Error analyzing {filepath}: {e}")

    print(f"\n📋 SUMMARY:")
    print("=" * 60)
    print("Both solutions were tested:")
    print("1. Melody Copy-Over: Explicitly copies original melody into harmonized output")
    print("2. Fixed Masking: Attempts to fix Coconet's internal masking logic")
    print("\nCheck the output files to see which solution worked successfully.")

if __name__ == "__main__":
    analyze_new_harmonizations() 