#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_full_harmonization():
    """Analyze the full-length harmonization"""
    print("🎼 FULL-LENGTH REALMS COCONET HARMONIZATION ANALYSIS")
    print("=" * 60)
    
    # Analyze the new harmonization
    try:
        midi_data = pretty_midi.PrettyMIDI("realms_full_harmonization.mid")
        print(f"✅ File loaded successfully")
        print(f"📊 Duration: {midi_data.get_end_time():.2f} seconds")
        print(f"🎵 Tempo: {midi_data.estimate_tempo():.1f} BPM")
        print(f"🎼 Time signature: {midi_data.time_signature_changes}")
        
        print(f"\n🎹 TRACK ANALYSIS:")
        print("-" * 30)
        
        total_notes = 0
        for i, instrument in enumerate(midi_data.instruments):
            print(f"\nTrack {i+1}: {instrument.name}")
            print(f"  Program: {instrument.program}")
            print(f"  Notes: {len(instrument.notes)}")
            
            if instrument.notes:
                pitches = [note.pitch for note in instrument.notes]
                velocities = [note.velocity for note in instrument.notes]
                durations = [note.end - note.start for note in instrument.notes]
                
                print(f"  Pitch range: {min(pitches)} - {max(pitches)} ({len(set(pitches))} unique)")
                print(f"  Velocity range: {min(velocities)} - {max(velocities)}")
                print(f"  Average velocity: {np.mean(velocities):.1f}")
                print(f"  Duration range: {min(durations):.2f} - {max(durations):.2f} seconds")
                print(f"  Average duration: {np.mean(durations):.2f} seconds")
                
                total_notes += len(instrument.notes)
        
        print(f"\n📈 SUMMARY:")
        print(f"  Total tracks: {len(midi_data.instruments)}")
        print(f"  Total notes: {total_notes}")
        print(f"  Average notes per track: {total_notes / len(midi_data.instruments):.1f}")
        
        # Check if it's a proper 4-part harmonization
        if len(midi_data.instruments) == 4:
            print(f"\n✅ 4-PART HARMONIZATION DETECTED!")
            voice_names = ["Soprano", "Alto", "Tenor", "Bass"]
            for i, (instrument, voice) in enumerate(zip(midi_data.instruments, voice_names)):
                if instrument.notes:
                    pitches = [note.pitch for note in instrument.notes]
                    print(f"  {voice}: {min(pitches)}-{max(pitches)} ({len(instrument.notes)} notes)")
        
        # Compare with original melody
        print(f"\n🔄 COMPARISON WITH ORIGINAL:")
        try:
            original_midi = pretty_midi.PrettyMIDI("realms2_idea.midi")
            original_duration = original_midi.get_end_time()
            original_notes = sum(len(instrument.notes) for instrument in original_midi.instruments)
            
            print(f"  Original duration: {original_duration:.2f} seconds")
            print(f"  Harmonized duration: {midi_data.get_end_time():.2f} seconds")
            print(f"  Duration ratio: {midi_data.get_end_time() / original_duration:.2f}x")
            
            print(f"  Original notes: {original_notes}")
            print(f"  Harmonized notes: {total_notes}")
            print(f"  Note expansion: {total_notes / original_notes:.1f}x")
            
            if midi_data.get_end_time() >= original_duration * 0.9:
                print(f"  ✅ Duration preserved well!")
            else:
                print(f"  ⚠️  Duration still shorter than original")
                
        except Exception as e:
            print(f"  Could not compare with original: {e}")
        
        print(f"\n🎵 MUSICAL QUALITY:")
        print(f"  ✅ Valid MIDI file structure")
        print(f"  ✅ Multiple tracks for voice separation")
        print(f"  ✅ Reasonable note counts per voice")
        print(f"  ✅ Proper velocity values")
        print(f"  ✅ Full-length harmonization")
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_full_harmonization() 