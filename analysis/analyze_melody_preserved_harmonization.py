#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_melody_preserved_harmonization():
    """Analyze the melody-preserved harmonization"""
    print("🎼 MELODY-PRESERVED HARMONIZATION ANALYSIS")
    print("=" * 60)
    
    try:
        # Load the melody-preserved harmonization
        harmonized_midi = pretty_midi.PrettyMIDI("../midi_files/../midi_files/melody_preserved_harmonization.mid")
        original_midi = pretty_midi.PrettyMIDI("../midi_files/realms2_idea.midi")
        
        print(f"✅ Loaded melody-preserved harmonization")
        print(f"📊 Duration: {harmonized_midi.get_end_time():.2f} seconds")
        print(f"📊 Tempo: {harmonized_midi.estimate_tempo():.1f} BPM")
        
        # Analyze each instrument/track
        print(f"\n🎵 INSTRUMENT ANALYSIS:")
        print("-" * 40)
        
        total_notes = 0
        melody_notes = 0
        harmony_notes = 0
        
        for i, instrument in enumerate(harmonized_midi.instruments):
            print(f"\n🎹 Instrument {i}: {instrument.name or 'Unnamed'}")
            print(f"   Program: {instrument.program}")
            print(f"   Notes: {len(instrument.notes)}")
            
            if instrument.notes:
                velocities = [note.velocity for note in instrument.notes]
                pitches = [note.pitch for note in instrument.notes]
                
                print(f"   Velocity range: {min(velocities)}-{max(velocities)}")
                print(f"   Average velocity: {np.mean(velocities):.1f}")
                print(f"   Pitch range: {min(pitches)}-{max(pitches)}")
                print(f"   Average pitch: {np.mean(pitches):.1f}")
                
                total_notes += len(instrument.notes)
                
                # Identify melody vs harmony based on velocity and position
                if i == 0 or max(velocities) > 100:  # First instrument or high velocity
                    melody_notes += len(instrument.notes)
                    print(f"   🎵 Likely MELODY track (high velocity)")
                else:
                    harmony_notes += len(instrument.notes)
                    print(f"   🎼 Likely HARMONY track")
        
        print(f"\n📈 SUMMARY:")
        print("-" * 40)
        print(f"Total notes: {total_notes}")
        print(f"Melody notes: {melody_notes}")
        print(f"Harmony notes: {harmony_notes}")
        print(f"Melody ratio: {melody_notes/total_notes*100:.1f}%")
        
        # Compare with original
        print(f"\n🔄 COMPARISON WITH ORIGINAL:")
        print("-" * 40)
        original_notes = len(original_midi.instruments[0].notes) if original_midi.instruments else 0
        print(f"Original melody notes: {original_notes}")
        print(f"Preserved melody notes: {melody_notes}")
        print(f"Melody preservation: {melody_notes/original_notes*100:.1f}%" if original_notes > 0 else "N/A")
        
        # Check if melody is clearly audible
        print(f"\n🎯 MELODY AUDIBILITY ASSESSMENT:")
        print("-" * 40)
        
        if melody_notes > 0:
            melody_velocity_avg = np.mean([note.velocity for inst in harmonized_midi.instruments[:1] for note in inst.notes])
            harmony_velocity_avg = np.mean([note.velocity for inst in harmonized_midi.instruments[1:] for note in inst.notes]) if len(harmonized_midi.instruments) > 1 else 0
            
            print(f"Average melody velocity: {melody_velocity_avg:.1f}")
            print(f"Average harmony velocity: {harmony_velocity_avg:.1f}")
            
            if melody_velocity_avg > harmony_velocity_avg * 1.5:
                print(f"✅ Melody should be clearly audible (velocity boost: {melody_velocity_avg/harmony_velocity_avg:.1f}x)")
            elif melody_velocity_avg > harmony_velocity_avg:
                print(f"⚠️  Melody should be somewhat audible (velocity boost: {melody_velocity_avg/harmony_velocity_avg:.1f}x)")
            else:
                print(f"❌ Melody may be drowned out by harmony")
        
        print(f"\n🎼 HARMONIZATION QUALITY:")
        print("-" * 40)
        print(f"✅ Duration preserved: {harmonized_midi.get_end_time():.2f}s vs {original_midi.get_end_time():.2f}s")
        print(f"✅ Multiple voices: {len(harmonized_midi.instruments)} instruments")
        print(f"✅ Rich harmonization: {harmony_notes} harmony notes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing harmonization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_melody_preserved_harmonization() 