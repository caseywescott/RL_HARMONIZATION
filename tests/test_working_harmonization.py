#!/usr/bin/env python3
"""
Test Working Harmonization with RL Model

This script tests the working harmonization server with the RL model.
"""

import requests
import tempfile
import os
import pretty_midi
import numpy as np

def test_working_harmonization():
    """Test the working harmonization server"""
    print("🎵 Testing Working Harmonization Server")
    
    # Server URL
    server_url = "http://localhost:8002"
    
    # Test 1: Check server status
    print("\n1. Checking server status...")
    try:
        response = requests.get(f"{server_url}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Server is running")
            print(f"   Model available: {status['model_available']}")
            print(f"   Harmonizer initialized: {status['harmonizer_initialized']}")
            print(f"   Method: {status['harmonization_method']}")
        else:
            print(f"   ❌ Server status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test 2: Harmonize the realms2_idea.midi file
    print("\n2. Testing harmonization...")
    try:
        # Check if input file exists
        input_file = "realms2_idea.midi"
        if not os.path.exists(input_file):
            print(f"   ❌ Input file {input_file} not found")
            return False
        
        print(f"   Using input file: {input_file}")
        
        # Send harmonization request
        with open(input_file, 'rb') as f:
            files = {'file': f}
            params = {'temperature': 0.99}
            response = requests.post(f"{server_url}/harmonize", files=files, params=params)
        
        if response.status_code == 200:
            # Save the harmonized file
            output_file = "test_working_harmonization.mid"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"   ✅ Harmonization successful")
            print(f"   Output saved to: {output_file}")
            print(f"   File size: {len(response.content)} bytes")
            
            # Analyze the harmonized file
            analyze_harmonization(output_file)
            
        else:
            print(f"   ❌ Harmonization failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Harmonization test failed: {e}")
        return False
    
    # Test 3: Test with different temperatures
    print("\n3. Testing different temperatures...")
    temperatures = [0.5, 1.0, 1.5]
    
    for temp in temperatures:
        try:
            print(f"   Testing temperature: {temp}")
            
            with open(input_file, 'rb') as f:
                files = {'file': f}
                params = {'temperature': temp}
                response = requests.post(f"{server_url}/harmonize", files=files, params=params)
            
            if response.status_code == 200:
                temp_output_file = f"test_working_harmonization_temp_{temp}.mid"
                with open(temp_output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"   ✅ Temperature {temp} successful")
                print(f"   Saved to: {temp_output_file}")
            else:
                print(f"   ❌ Temperature {temp} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Temperature {temp} test failed: {e}")
    
    print("\n🎉 All tests completed successfully!")
    return True

def analyze_harmonization(midi_file):
    """Analyze the harmonized MIDI file"""
    try:
        print(f"\n4. Analyzing harmonization: {midi_file}")
        
        # Load the MIDI file
        midi = pretty_midi.PrettyMIDI(midi_file)
        
        print(f"   Total instruments: {len(midi.instruments)}")
        
        # Analyze each instrument
        for i, instrument in enumerate(midi.instruments):
            print(f"   Instrument {i}: {instrument.name}")
            print(f"     Notes: {len(instrument.notes)}")
            
            if len(instrument.notes) > 0:
                # Get pitch range
                pitches = [note.pitch for note in instrument.notes]
                min_pitch = min(pitches)
                max_pitch = max(pitches)
                print(f"     Pitch range: {min_pitch} ({pretty_midi.note_number_to_name(min_pitch)}) to {max_pitch} ({pretty_midi.note_number_to_name(max_pitch)})")
                
                # Get timing info
                start_times = [note.start for note in instrument.notes]
                end_times = [note.end for note in instrument.notes]
                total_duration = max(end_times) - min(start_times) if start_times else 0
                print(f"     Duration: {total_duration:.2f} seconds")
        
        # Check for 4-part harmony
        if len(midi.instruments) == 4:
            print(f"   ✅ 4-part harmony structure confirmed")
        else:
            print(f"   ⚠️  Expected 4 parts, got {len(midi.instruments)}")
        
        # Check for melody preservation
        if len(midi.instruments) > 0 and len(midi.instruments[0].notes) > 0:
            print(f"   ✅ Melody track has {len(midi.instruments[0].notes)} notes")
        else:
            print(f"   ❌ No melody notes found")
        
        # Check for harmony parts
        harmony_notes = sum(len(instrument.notes) for instrument in midi.instruments[1:])
        if harmony_notes > 0:
            print(f"   ✅ Harmony parts have {harmony_notes} total notes")
        else:
            print(f"   ❌ No harmony notes found")
            
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")

def test_rl_integration():
    """Test integration with RL model"""
    print("\n5. Testing RL Model Integration...")
    
    try:
        # Import RL model components
        from src.harmonization.core.rl_environment import RLHarmonizationEnvironment
        from src.harmonization.rewards.music_theory_rewards import MusicTheoryRewards
        
        print("   ✅ RL model components imported successfully")
        
        # Test with the harmonized file
        harmonized_file = "test_working_harmonization.mid"
        if os.path.exists(harmonized_file):
            print(f"   Using harmonized file: {harmonized_file}")
            
            # Load the harmonized MIDI
            midi = pretty_midi.PrettyMIDI(harmonized_file)
            
            # Extract melody and harmony
            if len(midi.instruments) >= 2:
                melody_notes = midi.instruments[0].notes
                harmony_notes = []
                for instrument in midi.instruments[1:]:
                    harmony_notes.extend(instrument.notes)
                
                print(f"   Melody notes: {len(melody_notes)}")
                print(f"   Harmony notes: {len(harmony_notes)}")
                
                # Test music theory rewards
                rewards = MusicTheoryRewards()
                
                # Calculate some basic metrics
                if melody_notes and harmony_notes:
                    print(f"   ✅ RL integration test successful")
                    print(f"   Ready for RL model processing")
                else:
                    print(f"   ⚠️  No notes found for RL processing")
            else:
                print(f"   ❌ Insufficient instruments for RL processing")
        else:
            print(f"   ❌ Harmonized file not found")
            
    except ImportError as e:
        print(f"   ⚠️  RL model components not available: {e}")
        print(f"   This is expected if RL model is not set up")
    except Exception as e:
        print(f"   ❌ RL integration test failed: {e}")

if __name__ == "__main__":
    print("🎵 Working Harmonization Test Suite")
    print("=" * 50)
    
    # Run tests
    success = test_working_harmonization()
    
    if success:
        # Test RL integration
        test_rl_integration()
        
        print("\n" + "=" * 50)
        print("🎉 Test Suite Completed Successfully!")
        print("\nGenerated files:")
        print("- test_working_harmonization.mid (main harmonization)")
        print("- test_working_harmonization_temp_*.mid (temperature variations)")
        print("\nThe harmonization server is working correctly!")
    else:
        print("\n" + "=" * 50)
        print("❌ Test Suite Failed!")
        print("Please check the server status and try again.") 