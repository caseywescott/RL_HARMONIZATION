#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_enhanced_harmonizations():
    """Analyze the enhanced harmonizations with improved melody audibility"""
    print("🎼 ENHANCED MELODY AUDIBILITY ANALYSIS")
    print("=" * 60)
    
    files_to_analyze = [
        ("../midi_files/realms2_idea.midi", "ORIGINAL MELODY"),
        ("../midi_files/realms_fixed_harmonization_v1.mid", "ORIGINAL COCONET V1"),
        ("../midi_files/melody_enhanced_v1.mid", "ENHANCED V1 (2.5x melody, 0.5x harmony)"),
        ("../midi_files/realms_fixed_harmonization_v2.mid", "ORIGINAL COCONET V2"),
        ("../midi_files/melody_enhanced_v2.mid", "ENHANCED V2 (3.0x melody, 0.4x harmony)"),
        ("../midi_files/realms_fixed_harmonization_v3.mid", "ORIGINAL COCONET V3"),
        ("../midi_files/melody_enhanced_v3.mid", "ENHANCED V3 (2.0x melody, 0.6x harmony)")
    ]
    
    results = []
    
    for filepath, description in files_to_analyze:
        print(f"\n🎵 {description}")
        print("-" * 50)
        
        try:
            midi = pretty_midi.PrettyMIDI(filepath)
            
            print(f"📊 Duration: {midi.get_end_time():.2f} seconds")
            print(f"📊 Instruments: {len(midi.instruments)}")
            
            # Analyze velocity distribution
            instrument_velocities = []
            total_notes = 0
            
            for i, instrument in enumerate(midi.instruments):
                if instrument.notes:
                    velocities = [note.velocity for note in instrument.notes]
                    avg_velocity = np.mean(velocities)
                    instrument_velocities.append(avg_velocity)
                    total_notes += len(instrument.notes)
                    
                    print(f"   Instrument {i}: {len(instrument.notes)} notes, avg velocity: {avg_velocity:.1f}")
                    print(f"      Velocity range: {min(velocities)}-{max(velocities)}")
            
            if len(instrument_velocities) >= 2:
                melody_velocity = instrument_velocities[0]  # First instrument
                harmony_velocity = np.mean(instrument_velocities[1:])  # Other instruments
                
                velocity_ratio = melody_velocity / harmony_velocity if harmony_velocity > 0 else 1.0
                
                print(f"\n🎯 MELODY AUDIBILITY ANALYSIS:")
                print(f"   Melody velocity: {melody_velocity:.1f}")
                print(f"   Harmony velocity: {harmony_velocity:.1f}")
                print(f"   Velocity ratio: {velocity_ratio:.2f}x")
                
                if velocity_ratio > 2.0:
                    print(f"   ✅ EXCELLENT: Melody should be very clearly audible!")
                elif velocity_ratio > 1.5:
                    print(f"   ✅ GOOD: Melody should be clearly audible")
                elif velocity_ratio > 1.2:
                    print(f"   ✅ FAIR: Melody should be audible")
                else:
                    print(f"   ❌ POOR: Melody may be drowned out")
                
                results.append((description, velocity_ratio, filepath, total_notes))
            else:
                print(f"   ⚠️  Only one instrument found")
                results.append((description, 1.0, filepath, total_notes))
                
        except Exception as e:
            print(f"   ❌ Error analyzing {filepath}: {e}")
            results.append((description, 0.0, filepath, 0))
    
    # Summary
    print(f"\n📊 ENHANCED MELODY AUDIBILITY SUMMARY")
    print("=" * 60)
    
    # Sort by velocity ratio (best first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    for i, (description, ratio, filepath, notes) in enumerate(results):
        rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f"{rank} {description}")
        print(f"   Velocity ratio: {ratio:.2f}x")
        print(f"   Total notes: {notes}")
        print(f"   File: {filepath}")
    
    # Compare original vs enhanced
    print(f"\n🔄 BEFORE vs AFTER COMPARISON:")
    print("-" * 40)
    
    original_v1 = next((r for r in results if "ORIGINAL COCONET V1" in r[0]), None)
    enhanced_v1 = next((r for r in results if "ENHANCED V1" in r[0]), None)
    
    if original_v1 and enhanced_v1:
        improvement = (enhanced_v1[1] / original_v1[1] - 1) * 100
        print(f"V1 Improvement: {improvement:.1f}% ({original_v1[1]:.2f}x → {enhanced_v1[1]:.2f}x)")
    
    original_v2 = next((r for r in results if "ORIGINAL COCONET V2" in r[0]), None)
    enhanced_v2 = next((r for r in results if "ENHANCED V2" in r[0]), None)
    
    if original_v2 and enhanced_v2:
        improvement = (enhanced_v2[1] / original_v2[1] - 1) * 100
        print(f"V2 Improvement: {improvement:.1f}% ({original_v2[1]:.2f}x → {enhanced_v2[1]:.2f}x)")
    
    original_v3 = next((r for r in results if "ORIGINAL COCONET V3" in r[0]), None)
    enhanced_v3 = next((r for r in results if "ENHANCED V3" in r[0]), None)
    
    if original_v3 and enhanced_v3:
        improvement = (enhanced_v3[1] / original_v3[1] - 1) * 100
        print(f"V3 Improvement: {improvement:.1f}% ({original_v3[1]:.2f}x → {enhanced_v3[1]:.2f}x)")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    enhanced_results = [r for r in results if "ENHANCED" in r[0]]
    if enhanced_results:
        best_enhanced = max(enhanced_results, key=lambda x: x[1])
        print(f"🎯 Best enhanced version: {best_enhanced[0]}")
        print(f"📁 File: {best_enhanced[2]}")
        print(f"📈 Velocity ratio: {best_enhanced[1]:.2f}x")
        
        if best_enhanced[1] > 2.0:
            print(f"✅ This version should have VERY clearly audible melody!")
            print(f"🎵 The melody should stand out significantly from the harmony")
        elif best_enhanced[1] > 1.5:
            print(f"✅ This version should have clearly audible melody")
            print(f"🎵 The melody should be noticeably louder than the harmony")
    
    print(f"\n🎼 HARMONIZATION QUALITY:")
    print("-" * 40)
    
    # Check if we have good harmonizations
    good_harmonizations = [r for r in results if r[1] > 1.5 and "ENHANCED" in r[0]]
    if good_harmonizations:
        print(f"✅ Found {len(good_harmonizations)} harmonizations with good melody audibility:")
        for desc, ratio, filepath, notes in good_harmonizations:
            print(f"   - {desc}: {ratio:.2f}x velocity ratio, {notes} notes")
    else:
        print(f"⚠️  No harmonizations achieved good melody audibility")

if __name__ == "__main__":
    analyze_enhanced_harmonizations() 