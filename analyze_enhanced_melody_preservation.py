#!/usr/bin/env python3

import pretty_midi
import numpy as np

def analyze_enhanced_melody_preservation():
    """Analyze the enhanced melody-preserved harmonizations"""
    print("🎼 ENHANCED MELODY-PRESERVED HARMONIZATION ANALYSIS")
    print("=" * 70)
    
    files_to_analyze = [
        ("realms2_idea.midi", "ORIGINAL MELODY"),
        ("enhanced_melody_preserved_v1.mid", "ENHANCED V1 (temp=0.7, strength=2.5, reduction=0.5)"),
        ("enhanced_melody_preserved_v2.mid", "ENHANCED V2 (temp=0.5, strength=3.0, reduction=0.4)")
    ]
    
    results = []
    
    for filepath, description in files_to_analyze:
        print(f"\n🎵 {description}")
        print("-" * 60)
        
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
                
                results.append((description, velocity_ratio, filepath))
            else:
                print(f"   ⚠️  Only one instrument found")
                results.append((description, 1.0, filepath))
                
        except Exception as e:
            print(f"   ❌ Error analyzing {filepath}: {e}")
            results.append((description, 0.0, filepath))
    
    # Summary
    print(f"\n📊 ENHANCED MELODY PRESERVATION SUMMARY")
    print("=" * 70)
    
    # Sort by velocity ratio (best first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    for i, (description, ratio, filepath) in enumerate(results):
        rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        print(f"{rank} {description}")
        print(f"   Velocity ratio: {ratio:.2f}x")
        print(f"   File: {filepath}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    best_result = results[0] if results else None
    if best_result:
        print(f"🎯 Best melody preservation: {best_result[0]}")
        print(f"📁 File: {best_result[2]}")
        
        if best_result[1] > 2.0:
            print(f"✅ This version should have VERY clearly audible melody!")
            print(f"🎵 The melody should stand out significantly from the harmony")
        elif best_result[1] > 1.5:
            print(f"✅ This version should have clearly audible melody")
            print(f"🎵 The melody should be noticeably louder than the harmony")
        elif best_result[1] > 1.2:
            print(f"✅ This version should have audible melody")
            print(f"🎵 The melody should be somewhat louder than the harmony")
        else:
            print(f"⚠️  Even the best version may have melody audibility issues")
    
    # Parameter insights
    print(f"\n🔧 ENHANCED PARAMETER INSIGHTS:")
    print("-" * 40)
    
    enhanced_results = [r for r in results if "ENHANCED" in r[0]]
    if enhanced_results:
        print(f"Enhanced versions average velocity ratio: {np.mean([r[1] for r in enhanced_results]):.2f}x")
        
        # Compare with original
        original_ratio = next((r[1] for r in results if "ORIGINAL" in r[0]), 1.0)
        enhanced_avg = np.mean([r[1] for r in enhanced_results])
        
        if enhanced_avg > original_ratio:
            improvement = (enhanced_avg / original_ratio - 1) * 100
            print(f"✅ Enhanced versions improve melody audibility by {improvement:.1f}%")
        else:
            print(f"⚠️  Enhanced versions don't show significant improvement")
    
    print(f"\n🎼 HARMONIZATION QUALITY ASSESSMENT:")
    print("-" * 40)
    
    # Check if we have good harmonizations
    good_harmonizations = [r for r in results if r[1] > 1.5 and "ENHANCED" in r[0]]
    if good_harmonizations:
        print(f"✅ Found {len(good_harmonizations)} harmonizations with good melody audibility:")
        for desc, ratio, filepath in good_harmonizations:
            print(f"   - {desc}: {ratio:.2f}x velocity ratio")
    else:
        print(f"⚠️  No harmonizations achieved good melody audibility")
        print(f"   Consider trying different parameters or post-processing")

if __name__ == "__main__":
    analyze_enhanced_melody_preservation() 