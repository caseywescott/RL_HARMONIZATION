#!/usr/bin/env python3

import pretty_midi
import numpy as np
import sys
import os

def enhance_melody_audibility(input_file, output_file, melody_strength=2.0, harmony_reduction=0.6):
    """Enhance melody audibility in a harmonized MIDI file"""
    try:
        print(f"🎵 Enhancing melody audibility for: {input_file}")
        print(f"   Melody strength: {melody_strength}")
        print(f"   Harmony reduction: {harmony_reduction}")
        
        # Load the harmonized MIDI
        midi = pretty_midi.PrettyMIDI(input_file)
        
        if not midi.instruments:
            print(f"❌ No instruments found in {input_file}")
            return False
        
        print(f"📊 Found {len(midi.instruments)} instruments")
        
        # Strategy 1: Boost first instrument (melody) and reduce others
        if len(midi.instruments) >= 2:
            # Boost melody (first instrument)
            melody_instrument = midi.instruments[0]
            original_melody_velocity = np.mean([note.velocity for note in melody_instrument.notes]) if melody_instrument.notes else 100
            
            for note in melody_instrument.notes:
                note.velocity = min(127, int(note.velocity * melody_strength))
            
            new_melody_velocity = np.mean([note.velocity for note in melody_instrument.notes]) if melody_instrument.notes else 0
            
            # Reduce harmony instruments
            for instrument in midi.instruments[1:]:
                for note in instrument.notes:
                    note.velocity = max(40, int(note.velocity * harmony_reduction))
            
            print(f"   ✅ Applied velocity boost to melody track: {original_melody_velocity:.1f} → {new_melody_velocity:.1f}")
            print(f"   ✅ Applied velocity reduction to harmony tracks")
        
        # Strategy 2: If all velocities are the same, force differentiation
        all_velocities = []
        for instrument in midi.instruments:
            if instrument.notes:
                all_velocities.extend([note.velocity for note in instrument.notes])
        
        if len(set(all_velocities)) <= 2:  # Very few different velocities
            print(f"   ⚠️  Detected uniform velocities, applying forced differentiation")
            
            # Force melody to be much louder
            if midi.instruments[0].notes:
                for note in midi.instruments[0].notes:
                    note.velocity = 120  # Very loud melody
            
            # Force harmony to be much quieter
            for instrument in midi.instruments[1:]:
                for note in instrument.notes:
                    note.velocity = 60  # Much quieter harmony
        
        # Calculate final velocity ratios
        if len(midi.instruments) >= 2:
            melody_velocity = np.mean([note.velocity for note in midi.instruments[0].notes]) if midi.instruments[0].notes else 0
            harmony_velocity = np.mean([note.velocity for inst in midi.instruments[1:] for note in inst.notes]) if any(len(inst.notes) > 0 for inst in midi.instruments[1:]) else 0
            
            if harmony_velocity > 0:
                velocity_ratio = melody_velocity / harmony_velocity
                print(f"   📈 Final velocity ratio: {velocity_ratio:.2f}x")
                
                if velocity_ratio > 2.0:
                    print(f"   ✅ EXCELLENT: Melody should be very clearly audible!")
                elif velocity_ratio > 1.5:
                    print(f"   ✅ GOOD: Melody should be clearly audible")
                elif velocity_ratio > 1.2:
                    print(f"   ✅ FAIR: Melody should be audible")
                else:
                    print(f"   ⚠️  Melody may still be drowned out")
        
        # Save the enhanced MIDI
        midi.write(output_file)
        print(f"   💾 Enhanced MIDI saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enhancing melody audibility: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python enhance_melody_audibility.py <input_midi> <output_midi> [melody_strength] [harmony_reduction]")
        print("Example: python enhance_melody_audibility.py realms_fixed_harmonization_v1.mid enhanced_v1.mid 2.5 0.5")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    melody_strength = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    harmony_reduction = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    success = enhance_melody_audibility(input_file, output_file, melody_strength, harmony_reduction)
    
    if success:
        print(f"\n🎉 Successfully enhanced melody audibility!")
        print(f"📁 Enhanced file: {output_file}")
    else:
        print(f"\n❌ Failed to enhance melody audibility")

if __name__ == "__main__":
    main() 