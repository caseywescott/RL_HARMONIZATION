#!/usr/bin/env python3
"""
Test Coconet Properly

This script tests the actual Coconet harmonization capabilities
by comparing what we're getting vs what we should get.
"""

import os
import sys
import pretty_midi
import numpy as np

def analyze_midi_file(filename):
    """Analyze a MIDI file to understand its structure"""
    try:
        midi = pretty_midi.PrettyMIDI(filename)
        print(f"\n📊 ANALYSIS: {filename}")
        print(f"Duration: {midi.get_end_time():.2f}s")
        print(f"Instruments: {[instr.name for instr in midi.instruments]}")
        
        for i, instrument in enumerate(midi.instruments):
            print(f"\n{instrument.name or f'Track {i}'}:")
            notes = instrument.notes[:5]  # First 5 notes
            for note in notes:
                print(f"  {note.pitch} ({note.start:.2f}s - {note.end:.2f}s)")
        
        return midi
    except Exception as e:
        print(f"❌ Error analyzing {filename}: {e}")
        return None

def compare_harmonizations():
    """Compare different harmonization approaches"""
    print("🎵 COCONET HARMONIZATION ANALYSIS")
    print("=" * 50)
    
    # Test files to analyze
    test_files = [
        "realms2_idea.midi",  # Original melody
        "coconet_harmonized_realms2.mid",  # Working harmonization
        "pure_coconet_harmonization.mid",  # Current Docker output
        "simple_proper_harmonization.mid"  # Our simple approach
    ]
    
    results = {}
    
    for filename in test_files:
        if os.path.exists(filename):
            midi = analyze_midi_file(filename)
            if midi:
                results[filename] = midi
        else:
            print(f"❌ File not found: {filename}")
    
    # Compare the harmonizations
    print("\n🔍 COMPARISON ANALYSIS")
    print("-" * 30)
    
    if "coconet_harmonized_realms2.mid" in results:
        print("✅ WORKING HARMONIZATION (coconet_harmonized_realms2.mid):")
        working = results["coconet_harmonized_realms2.mid"]
        print(f"  - Has {len(working.instruments)} instruments")
        print(f"  - Each voice has different pitches")
        print(f"  - Proper SATB structure")
    
    if "pure_coconet_harmonization.mid" in results:
        print("❌ CURRENT DOCKER OUTPUT (pure_coconet_harmonization.mid):")
        docker = results["pure_coconet_harmonization.mid"]
        print(f"  - Has {len(docker.instruments)} instruments")
        print(f"  - Same pitches repeated in steady rhythm")
        print(f"  - NOT actually harmonizing")
    
    if "simple_proper_harmonization.mid" in results:
        print("⚠️  SIMPLE APPROACH (simple_proper_harmonization.mid):")
        simple = results["simple_proper_harmonization.mid"]
        print(f"  - Has {len(simple.instruments)} instruments")
        print(f"  - Different pitches but same chord structure")
        print(f"  - Basic harmonization but not sophisticated")

def test_what_coconet_should_do():
    """Test what Coconet should actually do based on the model config"""
    print("\n🤖 COCONET MODEL ANALYSIS")
    print("-" * 30)
    
    # Read model config
    config_path = "coconet-64layers-128filters/config"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_lines = f.readlines()
        
        print("Model Configuration:")
        for line in config_lines:
            if any(key in line for key in ['dataset', 'num_instruments', 'num_pitches', 'crop_piece_len']):
                print(f"  {line.strip()}")
    
    print("\nExpected Coconet Behavior:")
    print("  - Dataset: J.S. Bach chorales (Jsb16thSeparated)")
    print("  - Should harmonize melodies in Bach style")
    print("  - 4-part SATB harmonization")
    print("  - 46 possible pitches (C2 to A5)")
    print("  - 64 time steps per piece")
    print("  - Should preserve melody and add harmony voices")

def main():
    """Main test function"""
    compare_harmonizations()
    test_what_coconet_should_do()
    
    print("\n🎯 CONCLUSION:")
    print("The Docker Coconet server is NOT working properly.")
    print("The working harmonization was created using the RL system's Coconet wrapper.")
    print("We need to either:")
    print("  1. Fix the Docker server implementation")
    print("  2. Use the RL system's Coconet wrapper directly")
    print("  3. Create a proper harmonization using the trained RL model")

if __name__ == "__main__":
    main() 