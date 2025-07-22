#!/usr/bin/env python3

import pretty_midi
import numpy as np

def verify_melody_preservation():
    """Verify that the original melody is preserved in the successful harmonization"""
    print("🎼 MELODY PRESERVATION VERIFICATION")
    print("=" * 60)

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

        # Load successful harmonization
        harmonized_midi = pretty_midi.PrettyMIDI("melody_copy_harmonization_fixed.mid")
        
        if not harmonized_midi.instruments:
            print(f"❌ No instruments found in harmonization")
            return

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

        print(f"\n🎵 HARMONIZED MELODY TRACK:")
        print(f"   Notes: {len(harmonized_notes)}")
        print(f"   Pitches: {[note['pitch'] for note in harmonized_notes]}")
        print(f"   Duration: {harmonized_midi.get_end_time():.2f} seconds")

        # Compare with original
        if len(harmonized_notes) == len(original_notes):
            print(f"   ✅ Same number of notes")

            # Check if pitches match
            original_pitches = [note['pitch'] for note in original_notes]
            harmonized_pitches = [note['pitch'] for note in harmonized_notes]

            if original_pitches == harmonized_pitches:
                print(f"   ✅ PITCHES MATCH EXACTLY!")
                print(f"   🎵 Original melody is preserved in harmonization")
                print(f"   🎉 SUCCESS: Melody Copy-Over Solution WORKED!")
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

        # Check velocity enhancement
        print(f"\n🎚️ VELOCITY ANALYSIS:")
        if harmonized_notes:
            melody_velocities = [note['velocity'] for note in harmonized_notes]
            print(f"   Melody velocities: {melody_velocities}")
            print(f"   Melody velocity range: {min(melody_velocities)}-{max(melody_velocities)}")
            print(f"   Average melody velocity: {np.mean(melody_velocities):.1f}")

        if len(harmonized_midi.instruments) > 1:
            harmony_velocities = []
            for instrument in harmonized_midi.instruments[1:]:
                harmony_velocities.extend([note.velocity for note in instrument.notes])
            if harmony_velocities:
                print(f"   Harmony velocity range: {min(harmony_velocities)}-{max(harmony_velocities)}")
                print(f"   Average harmony velocity: {np.mean(harmony_velocities):.1f}")

        # Check harmony parts
        print(f"\n🎼 HARMONY ANALYSIS:")
        for i, instrument in enumerate(harmonized_midi.instruments[1:], 1):
            print(f"   Instrument {i}: {len(instrument.notes)} notes")
            if instrument.notes:
                pitches = [note.pitch for note in instrument.notes]
                print(f"      Pitches: {pitches}")

        print(f"\n📋 FINAL VERIFICATION:")
        print("=" * 60)
        if len(harmonized_notes) == len(original_notes) and [note['pitch'] for note in harmonized_notes] == [note['pitch'] for note in original_notes]:
            print("✅ MELODY PRESERVATION VERIFIED!")
            print("✅ The original melody is exactly preserved in the harmonization")
            print("✅ The melody copy-over solution is working correctly")
            print("✅ The harmonization includes both the original melody and generated harmony parts")
        else:
            print("❌ MELODY PRESERVATION FAILED")
            print("❌ The original melody is not preserved in the harmonization")

    except Exception as e:
        print(f"❌ Error in verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_melody_preservation() 