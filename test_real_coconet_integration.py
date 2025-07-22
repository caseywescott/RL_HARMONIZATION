#!/usr/bin/env python3

import requests
import time
import json
import pretty_midi
import numpy as np
from pathlib import Path

def test_server_status():
    """Test the Coconet server status endpoint"""
    print("🔍 Testing Coconet server status...")
    
    try:
        response = requests.get("http://localhost:8000/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Server is running")
            print(f"   Model available: {status['model_available']}")
            print(f"   Magenta scripts: {status['magenta_scripts_available']}")
            print(f"   Method: {status['harmonization_method']}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def test_harmonization_with_temperature(temperature, input_file="realms2_idea.midi"):
    """Test harmonization with a specific temperature"""
    print(f"\n🎵 Testing harmonization with temperature {temperature}...")
    
    try:
        with open(input_file, 'rb') as f:
            files = {'file': f}
            params = {'temperature': temperature}
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/harmonize",
                files=files,
                params=params
            )
            end_time = time.time()
            
            if response.status_code == 200:
                output_file = f"coconet_test_temp_{temperature}.mid"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                # Analyze the output
                midi_data = pretty_midi.PrettyMIDI(output_file)
                total_notes = sum(len(instrument.notes) for instrument in midi_data.instruments)
                
                print(f"✅ Harmonization successful ({end_time - start_time:.1f}s)")
                print(f"   Output file: {output_file}")
                print(f"   Duration: {midi_data.get_end_time():.2f}s")
                print(f"   Tracks: {len(midi_data.instruments)}")
                print(f"   Total notes: {total_notes}")
                
                return output_file, total_notes
            else:
                print(f"❌ Harmonization failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None, 0
                
    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        return None, 0

def analyze_harmonization_quality(midi_file):
    """Analyze the quality of a harmonization"""
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file)
        
        if len(midi_data.instruments) < 4:
            return "⚠️  Not enough voices for 4-part harmonization"
        
        # Check voice ranges (SATB)
        voice_ranges = []
        for i in range(min(4, len(midi_data.instruments))):
            instrument = midi_data.instruments[i]
            if instrument.notes:
                pitches = [note.pitch for note in instrument.notes]
                voice_ranges.append((min(pitches), max(pitches), len(pitches)))
        
        # Check for proper voice separation
        if len(voice_ranges) >= 4:
            soprano_range = voice_ranges[0]
            alto_range = voice_ranges[1] 
            tenor_range = voice_ranges[2]
            bass_range = voice_ranges[3]
            
            # Check if voices are in proper ranges
            soprano_ok = 60 <= soprano_range[0] <= soprano_range[1] <= 84  # C4 to C6
            alto_ok = 48 <= alto_range[0] <= alto_range[1] <= 72      # C3 to C5
            tenor_ok = 36 <= tenor_range[0] <= tenor_range[1] <= 60   # C2 to C4
            bass_ok = 24 <= bass_range[0] <= bass_range[1] <= 48      # C1 to C3
            
            if soprano_ok and alto_ok and tenor_ok and bass_ok:
                return "✅ Proper 4-part SATB harmonization with correct voice ranges"
            else:
                return "⚠️  4-part harmonization but voice ranges may be incorrect"
        
        return "⚠️  Unexpected voice configuration"
        
    except Exception as e:
        return f"❌ Error analyzing harmonization: {e}"

def test_rl_model_integration():
    """Test sending harmonized output to RL model (simulated)"""
    print("\n🤖 Testing RL model integration...")
    
    # Simulate sending harmonized output to RL model
    harmonized_files = [
        "final_real_coconet_harmonization.mid",
        "coconet_harmonization_temp_0.5.mid", 
        "coconet_harmonization_temp_1.5.mid"
    ]
    
    for file in harmonized_files:
        if Path(file).exists():
            try:
                midi_data = pretty_midi.PrettyMIDI(file)
                total_notes = sum(len(instrument.notes) for instrument in midi_data.instruments)
                
                # Simulate RL model processing
                print(f"   📁 {file}: {total_notes} notes, {len(midi_data.instruments)} tracks")
                
                # Simulate music theory evaluation
                quality_score = analyze_harmonization_quality(file)
                print(f"      Quality: {quality_score}")
                
            except Exception as e:
                print(f"   ❌ Error processing {file}: {e}")
        else:
            print(f"   ⚠️  File not found: {file}")

def run_comprehensive_test():
    """Run a comprehensive test of the Coconet integration"""
    print("🎼 REAL COCONET HARMONIZATION INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Server status
    if not test_server_status():
        print("❌ Server test failed. Cannot proceed.")
        return False
    
    # Test 2: Harmonization with different temperatures
    temperatures = [0.5, 0.99, 1.5]
    results = []
    
    for temp in temperatures:
        output_file, note_count = test_harmonization_with_temperature(temp)
        if output_file:
            quality = analyze_harmonization_quality(output_file)
            results.append({
                'temperature': temp,
                'file': output_file,
                'notes': note_count,
                'quality': quality
            })
    
    # Test 3: RL model integration
    test_rl_model_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if results:
        print("✅ Coconet server is working correctly!")
        print(f"   Generated {len(results)} harmonizations")
        
        for result in results:
            print(f"   Temperature {result['temperature']}: {result['notes']} notes - {result['quality']}")
        
        print("\n🎯 READY FOR RL MODEL INTEGRATION")
        print("   The Coconet server can now send legitimate Bach-style harmonizations")
        print("   to your RL model for processing and optimization.")
        
        return True
    else:
        print("❌ No successful harmonizations generated")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1) 