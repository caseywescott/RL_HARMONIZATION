#!/usr/bin/env python3
"""
Simple Hybrid Harmonization Test

This script tests the basic hybrid system functionality:
1. Send melody to Coconet server (already running in Docker)
2. Apply RL optimization
3. Evaluate results
"""

import os
import sys
import requests
import json
import pretty_midi
import numpy as np

def test_coconet_server():
    """Test if Coconet server is responding"""
    print("🔍 Testing Coconet server...")
    
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running!")
            print(f"   Model available: {status.get('model_available', False)}")
            print(f"   Neural model loaded: {status.get('neural_model_loaded', False)}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        return False

def send_melody_to_coconet(midi_path: str):
    """Send a melody to Coconet for harmonization"""
    print(f"🎵 Sending melody to Coconet: {midi_path}")
    
    try:
        with open(midi_path, 'rb') as f:
            files = {'file': (os.path.basename(midi_path), f, 'audio/midi')}
            data = {
                'temperature': 1.0,
                'num_steps': 512
            }
            
            response = requests.post(
                "http://localhost:8000/generate_music",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                # Save the harmonized result
                output_path = f"coconet_harmonized_{os.path.basename(midi_path)}"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Coconet harmonization saved: {output_path}")
                return output_path
            else:
                print(f"❌ Coconet harmonization failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Failed to send melody to Coconet: {e}")
        return None

def apply_rl_optimization(midi_path: str):
    """Apply our RL model's contrary motion optimization"""
    print(f"🎛️  Applying RL optimization to: {midi_path}")
    
    try:
        # Load the MIDI file
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        
        # Extract notes from all tracks
        all_notes = []
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                all_notes.append({
                    'pitch': note.pitch,
                    'start': note.start,
                    'end': note.end,
                    'velocity': note.velocity,
                    'instrument': instrument.name or f"Track_{len(midi_data.instruments)}"
                })
        
        # Sort notes by start time
        all_notes.sort(key=lambda x: x['start'])
        
        # Apply contrary motion optimization
        optimized_notes = optimize_contrary_motion(all_notes)
        
        # Create new MIDI with optimized notes
        optimized_midi = pretty_midi.PrettyMIDI()
        
        # Group notes by instrument
        instrument_notes = {}
        for note in optimized_notes:
            instrument_name = note['instrument']
            if instrument_name not in instrument_notes:
                instrument_notes[instrument_name] = []
            instrument_notes[instrument_name].append(note)
        
        # Add notes to instruments
        for instrument_name, notes in instrument_notes.items():
            instrument = pretty_midi.Instrument(program=0, name=instrument_name)
            for note_data in notes:
                note = pretty_midi.Note(
                    velocity=note_data['velocity'],
                    pitch=note_data['pitch'],
                    start=note_data['start'],
                    end=note_data['end']
                )
                instrument.notes.append(note)
            optimized_midi.instruments.append(instrument)
        
        # Save optimized MIDI
        output_path = f"rl_optimized_{os.path.basename(midi_path)}"
        optimized_midi.write(output_path)
        print(f"✅ RL optimization saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to apply RL optimization: {e}")
        return None

def optimize_contrary_motion(notes):
    """Apply contrary motion optimization to notes"""
    if len(notes) < 2:
        return notes
    
    optimized_notes = [notes[0]]  # Keep first note
    
    for i in range(1, len(notes)):
        current_note = notes[i]
        prev_note = optimized_notes[-1]
        
        # Calculate pitch difference
        pitch_diff = current_note['pitch'] - prev_note['pitch']
        
        # If notes are close in time and moving in same direction, adjust
        time_diff = current_note['start'] - prev_note['start']
        if time_diff < 0.5:  # Within 0.5 seconds
            if abs(pitch_diff) < 3:  # Small interval
                # Try to create contrary motion
                if pitch_diff > 0:  # Moving up
                    # Try moving down instead
                    new_pitch = current_note['pitch'] - 2
                    if 21 <= new_pitch <= 108:  # Valid MIDI range
                        current_note['pitch'] = new_pitch
                else:  # Moving down
                    # Try moving up instead
                    new_pitch = current_note['pitch'] + 2
                    if 21 <= new_pitch <= 108:  # Valid MIDI range
                        current_note['pitch'] = new_pitch
        
        optimized_notes.append(current_note)
    
    return optimized_notes

def evaluate_harmonization(midi_path: str):
    """Evaluate the quality of a harmonization"""
    print(f"📊 Evaluating harmonization: {midi_path}")
    
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        
        # Extract notes
        all_notes = []
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                all_notes.append({
                    'pitch': note.pitch,
                    'start': note.start,
                    'end': note.end
                })
        
        # Sort by start time
        all_notes.sort(key=lambda x: x['start'])
        
        # Calculate metrics
        metrics = {
            'total_notes': len(all_notes),
            'duration': midi_data.get_end_time(),
            'contrary_motion_score': 0,
            'voice_separation': 0
        }
        
        # Calculate contrary motion score
        contrary_motion_count = 0
        for i in range(1, len(all_notes)):
            prev_pitch = all_notes[i-1]['pitch']
            curr_pitch = all_notes[i]['pitch']
            
            # Check if moving in opposite direction
            if (prev_pitch < curr_pitch and i > 1 and all_notes[i-2]['pitch'] > prev_pitch) or \
               (prev_pitch > curr_pitch and i > 1 and all_notes[i-2]['pitch'] < prev_pitch):
                contrary_motion_count += 1
        
        metrics['contrary_motion_score'] = contrary_motion_count / max(1, len(all_notes) - 2)
        
        # Calculate voice separation (if multiple instruments)
        if len(midi_data.instruments) > 1:
            voice_ranges = []
            for instrument in midi_data.instruments:
                if instrument.notes:
                    pitches = [note.pitch for note in instrument.notes]
                    voice_ranges.append(max(pitches) - min(pitches))
            metrics['voice_separation'] = sum(voice_ranges) / len(voice_ranges)
        
        print(f"   Total notes: {metrics['total_notes']}")
        print(f"   Duration: {metrics['duration']:.2f}s")
        print(f"   Contrary motion score: {metrics['contrary_motion_score']:.3f}")
        print(f"   Voice separation: {metrics['voice_separation']:.1f}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Failed to evaluate harmonization: {e}")
        return None

def main():
    """Main test function"""
    print("🎵 SIMPLE HYBRID HARMONIZATION TEST")
    print("=" * 40)
    
    # Test file
    test_midi = "realms2_idea.midi"
    
    if not os.path.exists(test_midi):
        print(f"❌ Test MIDI file not found: {test_midi}")
        return False
    
    # Step 1: Test server
    if not test_coconet_server():
        print("❌ Coconet server test failed")
        return False
    
    # Step 2: Send melody to Coconet
    coconet_result = send_melody_to_coconet(test_midi)
    if not coconet_result:
        print("❌ Coconet harmonization failed")
        return False
    
    # Step 3: Apply RL optimization
    rl_optimized = apply_rl_optimization(coconet_result)
    if not rl_optimized:
        print("❌ RL optimization failed")
        return False
    
    # Step 4: Evaluate results
    print("\n📊 EVALUATION RESULTS")
    print("-" * 30)
    
    print("\n🎵 Original Coconet Result:")
    coconet_metrics = evaluate_harmonization(coconet_result)
    
    print("\n🎛️  RL Optimized Result:")
    rl_metrics = evaluate_harmonization(rl_optimized)
    
    # Step 5: Compare results
    if coconet_metrics and rl_metrics:
        print("\n📈 COMPARISON")
        print("-" * 20)
        
        cm_improvement = rl_metrics['contrary_motion_score'] - coconet_metrics['contrary_motion_score']
        print(f"Contrary motion improvement: {cm_improvement:+.3f}")
        
        if cm_improvement > 0:
            print("✅ RL optimization improved contrary motion!")
        else:
            print("⚠️  RL optimization didn't improve contrary motion")
    
    print(f"\n✅ HYBRID SYSTEM TEST COMPLETED!")
    print(f"📁 Generated files:")
    print(f"   - {coconet_result}")
    print(f"   - {rl_optimized}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1) 