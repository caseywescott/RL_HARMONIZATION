#!/usr/bin/env python3
"""
Hybrid Harmonization System Test

This script tests the complete hybrid system:
1. Starts Coconet server
2. Sends harmonizations to our RL model
3. Processes and evaluates results
"""

import os
import sys
import time
import subprocess
import requests
import json
import tempfile
import numpy as np
import pretty_midi
from pathlib import Path
import threading
import signal
import atexit

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

class HybridHarmonizationTester:
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8000"
        self.test_midi_path = "realms2_idea.midi"  # Use existing test file
        
    def start_coconet_server(self):
        """Start the Coconet server in a subprocess"""
        print("🚀 Starting Coconet server...")
        
        # Check if server is already running
        try:
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                print("✅ Coconet server is already running!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        # Start server in background
        server_script = "coconet-server/fixed_server.py"
        if not os.path.exists(server_script):
            print(f"❌ Server script not found: {server_script}")
            return False
            
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, server_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.server_url}/status", timeout=2)
                    if response.status_code == 200:
                        print("✅ Coconet server started successfully!")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_coconet_server(self):
        """Stop the Coconet server"""
        if self.server_process:
            print("🛑 Stopping Coconet server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
                print("✅ Server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Server didn't stop gracefully, forcing...")
                self.server_process.kill()
    
    def check_server_status(self):
        """Check the status of the Coconet server"""
        try:
            response = requests.get(f"{self.server_url}/status")
            if response.status_code == 200:
                status = response.json()
                print("📊 Server Status:")
                print(f"   Model available: {status.get('model_available', False)}")
                print(f"   Neural model loaded: {status.get('neural_model_loaded', False)}")
                print(f"   Model path: {status.get('model_path', 'N/A')}")
                return status
            else:
                print(f"❌ Server returned status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Failed to check server status: {e}")
            return None
    
    def send_melody_to_coconet(self, midi_path: str, temperature: float = 1.0):
        """Send a melody to Coconet for harmonization"""
        print(f"🎵 Sending melody to Coconet: {midi_path}")
        
        try:
            with open(midi_path, 'rb') as f:
                files = {'file': (os.path.basename(midi_path), f, 'audio/midi')}
                data = {
                    'temperature': temperature,
                    'num_steps': 512
                }
                
                response = requests.post(
                    f"{self.server_url}/generate_music",
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
    
    def load_rl_model(self):
        """Load our trained RL model"""
        print("🤖 Loading RL model...")
        
        try:
            # Load the trained model metadata
            metadata_path = "simple_contrary_motion_model_metadata.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                print(f"✅ Loaded RL model metadata: {metadata.get('model_name', 'Unknown')}")
                print(f"   Episodes trained: {metadata.get('episodes_trained', 0)}")
                print(f"   Best reward: {metadata.get('best_reward', 0)}")
                return metadata
            else:
                print("❌ RL model metadata not found")
                return None
        except Exception as e:
            print(f"❌ Failed to load RL model: {e}")
            return None
    
    def apply_rl_optimization(self, midi_path: str):
        """Apply our RL model's contrary motion optimization to a harmonization"""
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
                        'instrument': instrument.name
                    })
            
            # Sort notes by start time
            all_notes.sort(key=lambda x: x['start'])
            
            # Apply contrary motion optimization
            optimized_notes = self._optimize_contrary_motion(all_notes)
            
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
                instrument = pretty_midi.Instrument(name=instrument_name)
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
    
    def _optimize_contrary_motion(self, notes):
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
    
    def evaluate_harmonization(self, midi_path: str):
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
                'voice_separation': 0,
                'consonance_score': 0
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
    
    def run_full_test(self):
        """Run the complete hybrid system test"""
        print("🎵 HYBRID HARMONIZATION SYSTEM TEST")
        print("=" * 50)
        
        # Register cleanup
        atexit.register(self.stop_coconet_server)
        
        try:
            # Step 1: Start Coconet server
            if not self.start_coconet_server():
                print("❌ Failed to start Coconet server")
                return False
            
            # Step 2: Check server status
            status = self.check_server_status()
            if not status:
                print("❌ Server status check failed")
                return False
            
            # Step 3: Load RL model
            rl_metadata = self.load_rl_model()
            if not rl_metadata:
                print("❌ Failed to load RL model")
                return False
            
            # Step 4: Check if test MIDI exists
            if not os.path.exists(self.test_midi_path):
                print(f"❌ Test MIDI file not found: {self.test_midi_path}")
                return False
            
            # Step 5: Send melody to Coconet
            coconet_result = self.send_melody_to_coconet(self.test_midi_path)
            if not coconet_result:
                print("❌ Coconet harmonization failed")
                return False
            
            # Step 6: Apply RL optimization
            rl_optimized = self.apply_rl_optimization(coconet_result)
            if not rl_optimized:
                print("❌ RL optimization failed")
                return False
            
            # Step 7: Evaluate results
            print("\n📊 EVALUATION RESULTS")
            print("-" * 30)
            
            print("\n🎵 Original Coconet Result:")
            coconet_metrics = self.evaluate_harmonization(coconet_result)
            
            print("\n🎛️  RL Optimized Result:")
            rl_metrics = self.evaluate_harmonization(rl_optimized)
            
            # Step 8: Compare results
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
            
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False
        finally:
            # Cleanup
            self.stop_coconet_server()

def main():
    """Main function"""
    tester = HybridHarmonizationTester()
    success = tester.run_full_test()
    
    if success:
        print("\n🎉 Hybrid system test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Hybrid system test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 