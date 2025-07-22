#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_melody_preservation(filepath, description):
    """Analyze melody preservation in a harmonization file"""
    print(f"\n🎼 {description}")
    print("-" * 50)
    
    try:
        midi = pretty_midi.PrettyMIDI(filepath)
        
        print(f"📊 Duration: {midi.get_end_time():.2f} seconds")
        print(f"📊 Instruments: {len(midi.instruments)}")
        
        # Analyze velocity distribution
        all_velocities = []
        instrument_velocities = []
        
        for i, instrument in enumerate(midi.instruments):
            if instrument.notes:
                velocities = [note.velocity for note in instrument.notes]
                instrument_velocities.append(np.mean(velocities))
                all_velocities.extend(velocities)
                
                print(f"   Instrument {i}: {len(instrument.notes)} notes, avg velocity: {np.mean(velocities):.1f}")
        
        if len(instrument_velocities) >= 2:
            melody_velocity = instrument_velocities[0]  # First instrument
            harmony_velocity = np.mean(instrument_velocities[1:])  # Other instruments
            
            velocity_ratio = melody_velocity / harmony_velocity if harmony_velocity > 0 else 1.0
            
            print(f"🎵 Melody velocity: {melody_velocity:.1f}")
            print(f"🎼 Harmony velocity: {harmony_velocity:.1f}")
            print(f"📈 Velocity ratio: {velocity_ratio:.2f}x")
            
            if velocity_ratio > 1.5:
                print(f"✅ EXCELLENT: Melody should be clearly audible")
            elif velocity_ratio > 1.2:
                print(f"✅ GOOD: Melody should be audible")
            elif velocity_ratio > 1.0:
                print(f"⚠️  FAIR: Melody may be somewhat audible")
            else:
                print(f"❌ POOR: Melody may be drowned out")
        
        return velocity_ratio if len(instrument_velocities) >= 2 else 1.0
        
    except Exception as e:
        print(f"❌ Error analyzing {filepath}: {e}")
        return 0.0

def main():
    print("🎼 MELODY PRESERVATION COMPARISON")
    print("=" * 60)
    
    files_to_analyze = [
        ("realms2_idea.midi", "ORIGINAL MELODY"),
        ("realms_fixed_harmonization_v1.mid", "STANDARD COCONET (temp=0.99)"),
        ("realms_fixed_harmonization_v2.mid", "STANDARD COCONET (temp=0.7)"),
        ("realms_fixed_harmonization_v3.mid", "STANDARD COCONET (temp=1.3)"),
        ("melody_preserved_harmonization.mid", "MELODY-PRESERVED (temp=0.7, strength=2.5)"),
        ("melody_preserved_v2.mid", "MELODY-PRESERVED (temp=0.5, strength=3.0)"),
        ("melody_preserved_v3.mid", "MELODY-PRESERVED (temp=0.3, strength=2.0)")
    ]
    
    results = []
    
    for filepath, description in files_to_analyze:
        try:
            ratio = analyze_melody_preservation(filepath, description)
            results.append((description, ratio, filepath))
        except:
            print(f"❌ Could not analyze {filepath}")
    
    # Summary
    print(f"\n📊 MELODY PRESERVATION SUMMARY")
    print("=" * 60)
    
    # Sort by velocity ratio (best first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    for i, (description, ratio, filepath) in enumerate(results):
        rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f"{rank} {description}: {ratio:.2f}x velocity ratio")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    best_result = results[0] if results else None
    if best_result:
        print(f"🎯 Best melody preservation: {best_result[0]}")
        print(f"📁 File: {best_result[2]}")
        
        if best_result[1] > 1.5:
            print(f"✅ This version should have clearly audible melody!")
        elif best_result[1] > 1.2:
            print(f"✅ This version should have audible melody")
        else:
            print(f"⚠️  Even the best version may have melody audibility issues")
    
    print(f"\n🔧 PARAMETER INSIGHTS:")
    print("-" * 40)
    
    # Analyze temperature effects
    temp_07_results = [r for r in results if "temp=0.7" in r[0]]
    temp_05_results = [r for r in results if "temp=0.5" in r[0]]
    temp_03_results = [r for r in results if "temp=0.3" in r[0]]
    
    if temp_07_results:
        avg_07 = np.mean([r[1] for r in temp_07_results])
        print(f"Temperature 0.7 average: {avg_07:.2f}x")
    if temp_05_results:
        avg_05 = np.mean([r[1] for r in temp_05_results])
        print(f"Temperature 0.5 average: {avg_05:.2f}x")
    if temp_03_results:
        avg_03 = np.mean([r[1] for r in temp_03_results])
        print(f"Temperature 0.3 average: {avg_03:.2f}x")

if __name__ == "__main__":
    main() 