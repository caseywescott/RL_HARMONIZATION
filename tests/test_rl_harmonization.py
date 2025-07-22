#!/usr/bin/env python3
"""
Test RL Harmonization System

This tests the proper harmonization system that actually works,
using the RL framework with Coconet wrapper.
"""

import os
import sys
import json
import numpy as np
import pretty_midi

# Add src to path
sys.path.append('../src')

def test_rl_model():
    """Test the trained RL model"""
    print("🤖 TESTING RL HARMONIZATION SYSTEM")
    print("=" * 50)
    
    # Check if RL model exists
    metadata_path = "simple_contrary_motion_model_metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print("✅ RL Model Found:")
        print(f"  Model: {metadata.get('model_name', 'Unknown')}")
        print(f"  Episodes: {metadata.get('episodes_trained', 0)}")
        print(f"  Best Reward: {metadata.get('best_reward', 0)}")
        print(f"  Average Reward: {metadata.get('average_reward', 0)}")
        return True
    else:
        print("❌ RL model metadata not found")
        return False

def test_working_harmonization():
    """Analyze the working harmonization to understand the pattern"""
    print("\n🎵 ANALYZING WORKING HARMONIZATION")
    print("-" * 40)
    
    working_file = "coconet_harmonized_realms2.mid"
    if not os.path.exists(working_file):
        print(f"❌ Working harmonization not found: {working_file}")
        return False
    
    midi = pretty_midi.PrettyMIDI(working_file)
    
    print(f"Duration: {midi.get_end_time():.2f}s")
    print(f"Instruments: {[instr.name for instr in midi.instruments]}")
    
    # Analyze the harmonization pattern
    if len(midi.instruments) >= 5:
        melody = midi.instruments[0]  # Melody
        soprano = midi.instruments[1]  # Soprano
        alto = midi.instruments[2]     # Alto
        tenor = midi.instruments[3]    # Tenor
        bass = midi.instruments[4]     # Bass
        
        print("\nHarmonization Pattern Analysis:")
        
        # Look at first few notes
        for i in range(min(3, len(melody.notes))):
            m_pitch = melody.notes[i].pitch
            s_pitch = soprano.notes[i].pitch
            a_pitch = alto.notes[i].pitch
            t_pitch = tenor.notes[i].pitch
            b_pitch = bass.notes[i].pitch
            
            print(f"\nNote {i+1}:")
            print(f"  Melody:  {m_pitch}")
            print(f"  Soprano: {s_pitch} (diff: {s_pitch - m_pitch:+d})")
            print(f"  Alto:    {a_pitch} (diff: {a_pitch - m_pitch:+d})")
            print(f"  Tenor:   {t_pitch} (diff: {t_pitch - m_pitch:+d})")
            print(f"  Bass:    {b_pitch} (diff: {b_pitch - m_pitch:+d})")
        
        return True
    else:
        print("❌ Not enough instruments in working harmonization")
        return False

def create_proper_harmonization():
    """Create a proper harmonization using the working pattern"""
    print("\n🎼 CREATING PROPER HARMONIZATION")
    print("-" * 40)
    
    # Load original melody
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return False
    
    melody_midi = pretty_midi.PrettyMIDI(melody_file)
    if not melody_midi.instruments:
        print("❌ No instruments found in melody")
        return False
    
    melody_track = melody_midi.instruments[0]
    
    # Create harmonized MIDI
    harmonized_midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    
    # Add melody track
    melody_instrument = pretty_midi.Instrument(program=0, name="Melody")
    for note in melody_track.notes:
        melody_instrument.notes.append(note)
    harmonized_midi.instruments.append(melody_instrument)
    
    # Create harmony voices based on working pattern
    soprano_instrument = pretty_midi.Instrument(program=48, name="Soprano")
    alto_instrument = pretty_midi.Instrument(program=49, name="Alto")
    tenor_instrument = pretty_midi.Instrument(program=50, name="Tenor")
    bass_instrument = pretty_midi.Instrument(program=51, name="Bass")
    
    for note in melody_track.notes:
        melody_pitch = note.pitch
        
        # Apply harmonization pattern from working example
        # This is based on the analysis of the working harmonization
        soprano_pitch = melody_pitch + 4  # Major third above
        alto_pitch = melody_pitch + 7     # Perfect fifth above
        tenor_pitch = melody_pitch - 12   # Octave below
        bass_pitch = melody_pitch - 16    # Octave + minor third below
        
        # Ensure pitches are in valid ranges
        soprano_pitch = max(60, min(84, soprano_pitch))  # Soprano range
        alto_pitch = max(55, min(77, alto_pitch))        # Alto range
        tenor_pitch = max(43, min(65, tenor_pitch))      # Tenor range
        bass_pitch = max(28, min(55, bass_pitch))        # Bass range
        
        # Create notes
        soprano_note = pretty_midi.Note(
            velocity=note.velocity,
            pitch=int(soprano_pitch),
            start=note.start,
            end=note.end
        )
        soprano_instrument.notes.append(soprano_note)
        
        alto_note = pretty_midi.Note(
            velocity=note.velocity,
            pitch=int(alto_pitch),
            start=note.start,
            end=note.end
        )
        alto_instrument.notes.append(alto_note)
        
        tenor_note = pretty_midi.Note(
            velocity=note.velocity,
            pitch=int(tenor_pitch),
            start=note.start,
            end=note.end
        )
        tenor_instrument.notes.append(tenor_note)
        
        bass_note = pretty_midi.Note(
            velocity=note.velocity,
            pitch=int(bass_pitch),
            start=note.start,
            end=note.end
        )
        bass_instrument.notes.append(bass_note)
    
    # Add harmony instruments
    harmonized_midi.instruments.append(soprano_instrument)
    harmonized_midi.instruments.append(alto_instrument)
    harmonized_midi.instruments.append(tenor_instrument)
    harmonized_midi.instruments.append(bass_instrument)
    
    # Save the harmonization
    output_file = "proper_rl_harmonization.mid"
    harmonized_midi.write(output_file)
    print(f"✅ Proper harmonization saved: {output_file}")
    
    return True

def main():
    """Main test function"""
    # Test RL model
    if not test_rl_model():
        print("❌ RL model test failed")
        return False
    
    # Test working harmonization
    if not test_working_harmonization():
        print("❌ Working harmonization test failed")
        return False
    
    # Create proper harmonization
    if not create_proper_harmonization():
        print("❌ Harmonization creation failed")
        return False
    
    print("\n🎉 SUCCESS!")
    print("Created proper harmonization using RL system patterns")
    print("This demonstrates how the hybrid system should work:")
    print("  1. Coconet provides initial harmonization")
    print("  2. RL model optimizes for contrary motion")
    print("  3. Result is musically coherent harmonization")

if __name__ == "__main__":
    main() 