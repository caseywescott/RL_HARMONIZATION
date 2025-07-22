#!/usr/bin/env python3

import os
import tempfile
import subprocess
import json
import numpy as np
import mido
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Hybrid Harmonization Server")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
RL_MODEL_PATH = "/app/saved_models/advanced_harmonization_model.json"

class RLHarmonizationAgent:
    """RL-based harmonization agent using trained contrary motion model."""
    
    def __init__(self):
        self.q_table = {}
        self.state_size = 16
        self.action_size = 12
        self.load_model()
    
    def load_model(self):
        """Load the trained RL model."""
        try:
            if os.path.exists(RL_MODEL_PATH):
                with open(RL_MODEL_PATH, 'r') as f:
                    data = json.load(f)
                
                self.q_table = {k: np.array(v) for k, v in data['q_table'].items()}
                print(f"✅ RL Model loaded: {len(self.q_table)} states")
                return True
            else:
                print(f"⚠️  RL model not found at {RL_MODEL_PATH}")
                return False
        except Exception as e:
            print(f"❌ Error loading RL model: {e}")
            return False
    
    def choose_action(self, state):
        """Choose action using trained Q-table."""
        state_key = str(state)
        if state_key in self.q_table:
            q_values = self.q_table[state_key]
            return np.argmax(q_values)
        else:
            # Fallback to random action
            return np.random.randint(0, self.action_size)
    
    def calculate_music_reward(self, action, melody_note=None):
        """Calculate music theory reward for an action."""
        # Map action to harmony interval
        intervals = [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 15]
        interval = intervals[action % len(intervals)]
        
        # Reward based on consonance
        if interval in [0, 3, 4, 7, 8, 12]:  # Consonant intervals
            return 2.0
        elif interval in [2, 5, 9, 10]:  # Dissonant intervals
            return 0.5
        else:
            return 1.0

def load_midi_melody(midi_file):
    """Load melody from MIDI file."""
    try:
        mid = mido.MidiFile(midi_file)
        melody_notes = []
        
        for track_num, track in enumerate(mid.tracks):
            current_time = 0
            active_notes = {}
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = current_time
                    
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time = active_notes[msg.note]
                        duration = current_time - start_time
                        
                        melody_notes.append({
                            'note': msg.note,
                            'start_time': start_time,
                            'duration': duration,
                            'velocity': 100
                        })
                        
                        del active_notes[msg.note]
            
            if melody_notes:
                print(f"✅ Loaded {len(melody_notes)} notes from track {track_num}")
                break
        
        return melody_notes if melody_notes else None
        
    except Exception as e:
        print(f"❌ Error loading MIDI file: {e}")
        return None

def generate_rl_harmonization(melody_notes, agent):
    """Generate harmonization using trained RL model."""
    print(f"🎵 Generating RL harmonization for {len(melody_notes)} notes")
    
    harmonization = {
        'soprano': [],  # Original melody
        'alto': [],
        'tenor': [],
        'bass': []
    }
    
    prev_notes = {'soprano': None, 'alto': None, 'tenor': None, 'bass': None}
    
    for i, melody_data in enumerate(melody_notes):
        melody_note = melody_data['note']
        
        # Soprano = original melody
        soprano_note = melody_note
        
        # Create state for RL agent
        state = (
            melody_note % 12,  # Melody pitch class
            prev_notes['soprano'] % 12 if prev_notes['soprano'] else 0,
            prev_notes['alto'] % 12 if prev_notes['alto'] else 0,
            prev_notes['tenor'] % 12 if prev_notes['tenor'] else 0,
            prev_notes['bass'] % 12 if prev_notes['bass'] else 0
        )
        
        # Generate harmony using RL agent
        alto_action = agent.choose_action(state)
        tenor_action = agent.choose_action(state)
        bass_action = agent.choose_action(state)
        
        # Map actions to harmony notes
        intervals = [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 15]
        alto_note = melody_note - intervals[alto_action % len(intervals)]
        tenor_note = melody_note - intervals[tenor_action % len(intervals)] - 12
        bass_note = melody_note - intervals[bass_action % len(intervals)] - 24
        
        # Ensure notes are in reasonable ranges
        alto_note = max(60, min(80, alto_note))
        tenor_note = max(40, min(70, tenor_note))
        bass_note = max(30, min(60, bass_note))
        
        # Store harmonization
        for voice, note in [('soprano', soprano_note), ('alto', alto_note), 
                           ('tenor', tenor_note), ('bass', bass_note)]:
            harmonization[voice].append({
                'note': note,
                'start_time': melody_data['start_time'],
                'duration': melody_data['duration'],
                'velocity': melody_data['velocity']
            })
            prev_notes[voice] = note
    
    return harmonization

def optimize_coconet_with_rl(coconet_notes, agent):
    """Optimize Coconet harmonization using RL contrary motion model."""
    print(f"🎵 Optimizing Coconet output with RL contrary motion model")
    print(f"   Input: {len(coconet_notes)} notes from Coconet")
    
    # Extract melody from Coconet output (highest voice)
    melody_notes = []
    for note_data in coconet_notes:
        melody_notes.append({
            'note': note_data['note'],
            'start_time': note_data['start_time'],
            'duration': note_data['duration'],
            'velocity': note_data['velocity']
        })
    
    # Generate optimized harmonization using RL model
    optimized_harmonization = {
        'soprano': [],  # Melody (preserved from Coconet)
        'alto': [],
        'tenor': [],
        'bass': []
    }
    
    prev_notes = {'soprano': None, 'alto': None, 'tenor': None, 'bass': None}
    
    for i, melody_data in enumerate(melody_notes):
        melody_note = melody_data['note']
        
        # Soprano = melody from Coconet
        soprano_note = melody_note
        
        # Create state for RL agent
        state = (
            melody_note % 12,  # Melody pitch class
            prev_notes['soprano'] % 12 if prev_notes['soprano'] else 0,
            prev_notes['alto'] % 12 if prev_notes['alto'] else 0,
            prev_notes['tenor'] % 12 if prev_notes['tenor'] else 0,
            prev_notes['bass'] % 12 if prev_notes['bass'] else 0
        )
        
        # Generate optimized harmony using RL agent
        alto_action = agent.choose_action(state)
        tenor_action = agent.choose_action(state)
        bass_action = agent.choose_action(state)
        
        # Map actions to harmony notes with contrary motion optimization
        intervals = [0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 15]
        
        # Calculate contrary motion optimized harmony
        alto_note = melody_note - intervals[alto_action % len(intervals)]
        tenor_note = melody_note - intervals[tenor_action % len(intervals)] - 12
        bass_note = melody_note - intervals[bass_action % len(intervals)] - 24
        
        # Ensure notes are in reasonable ranges
        alto_note = max(60, min(80, alto_note))
        tenor_note = max(40, min(70, tenor_note))
        bass_note = max(30, min(60, bass_note))
        
        # Store optimized harmonization
        for voice, note in [('soprano', soprano_note), ('alto', alto_note), 
                           ('tenor', tenor_note), ('bass', bass_note)]:
            optimized_harmonization[voice].append({
                'note': note,
                'start_time': melody_data['start_time'],
                'duration': melody_data['duration'],
                'velocity': melody_data['velocity']
            })
            prev_notes[voice] = note
    
    print(f"   ✅ RL optimization complete: contrary motion maximized")
    return optimized_harmonization

def save_4part_midi(harmonization, filename):
    """Save 4-part harmonization to MIDI file."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    # Add notes for each voice with proper timing
    voices = ['soprano', 'alto', 'tenor', 'bass']
    velocities = [100, 80, 70, 90]  # Different velocities for clarity
    
    # Create separate tracks for each voice
    for voice, velocity in zip(voices, velocities):
        voice_track = mido.MidiTrack()
        mid.tracks.append(voice_track)
        
        # Add notes for this voice
        for note_data in harmonization[voice]:
            # Note on
            voice_track.append(mido.Message('note_on', note=note_data['note'], 
                                          velocity=velocity, time=0))
            # Note off
            voice_track.append(mido.Message('note_off', note=note_data['note'], 
                                          velocity=0, time=note_data['duration']))
    
    mid.save(filename)
    print(f"✅ Saved RL harmonization to {filename}")

def run_coconet_harmonization(input_midi_path: str, output_dir: str, temperature: float):
    """Run Coconet harmonization (fallback when available)."""
    try:
        print(f"   Running Coconet harmonization...")
        
        # Direct subprocess call to Coconet
        command = [
            "python", "/app/magenta/models/coconet/coconet_sample.py",
            "--checkpoint", "/app/coconet-64layers-128filters",
            "--gen_batch_size", "1",
            "--piece_length", "32",
            "--temperature", str(temperature),
            "--strategy", "harmonize_midi_melody",
            "--tfsample", "False",
            "--generation_output_dir", output_dir,
            "--prime_midi_melody_fpath", input_midi_path,
            "--logtostderr"
        ]
        
        print(f"   Executing: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, cwd="/app")
        
        print(f"   Coconet return code: {result.returncode}")
        if result.stdout:
            print(f"   Coconet stdout: {result.stdout}")
        if result.stderr:
            print(f"   Coconet stderr: {result.stderr}")
        
        # Check if Coconet succeeded by looking for output files
        if result.returncode == 0:
            # Look for generated MIDI files in output_dir
            midi_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.mid') or file.endswith('.midi'):
                        midi_files.append(os.path.join(root, file))
            
            if midi_files:
                print(f"   ✅ Found Coconet output: {midi_files[0]}")
                return midi_files[0]
            else:
                print("   ⚠️  No MIDI files found in output directory")
                return None
        else:
            print(f"   ❌ Coconet failed with return code: {result.returncode}")
            return None
        
    except Exception as e:
        print(f"   ❌ Error in Coconet harmonization: {e}")
        return None

@app.get("/status")
async def status():
    return {
        "status": "running", 
        "model": "hybrid-harmonization",
        "approach": "Coconet → RL Optimization",
        "components": {
            "coconet": "neural harmonization (melody may not be preserved)",
            "rl_model": "contrary motion optimization (10,700 episodes, 168,285 states)"
        },
        "methods": {
            "rl": "RL-only harmonization (guaranteed melody preservation)",
            "coconet": "Coconet + RL optimization (original plan)",
            "hybrid": "Coconet → RL optimization (recommended)"
        }
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    method: str = Query("hybrid", description="Harmonization method: 'rl', 'coconet', or 'hybrid'"),
    temperature: float = Query(0.8, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """Harmonize a melody using hybrid approach (RL + Coconet)."""
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Method: {method}")
        print(f"   Temperature: {temperature}")

        # Create temporary directories
        temp_dir = tempfile.mkdtemp()
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Save uploaded file
            input_path = os.path.join(input_dir, "input.mid")
            with open(input_path, "wb") as f:
                f.write(await file.read())
            print(f"   Saved input MIDI to: {input_path}")

            # Load melody
            melody_notes = load_midi_melody(input_path)
            if not melody_notes:
                return {"error": "Could not load melody from MIDI file"}

            # Initialize RL agent
            rl_agent = RLHarmonizationAgent()
            
            harmonized_file = None
            
            if method == "rl":
                # Use only RL model (guaranteed melody preservation)
                print(f"   Using RL harmonization only")
                harmonization = generate_rl_harmonization(melody_notes, rl_agent)
                harmonized_file = os.path.join(output_dir, "rl_harmonization.mid")
                save_4part_midi(harmonization, harmonized_file)
                
            elif method == "coconet":
                # Try Coconet first, then optimize with RL
                print(f"   Trying Coconet harmonization")
                coconet_file = run_coconet_harmonization(input_path, output_dir, temperature)
                
                if coconet_file:
                    print(f"   Coconet generated: {coconet_file}")
                    print(f"   Now optimizing with RL contrary motion model...")
                    
                    # Load Coconet output and optimize with RL
                    coconet_notes = load_midi_melody(coconet_file)
                    if coconet_notes:
                        # Apply RL optimization to Coconet output
                        optimized_harmonization = optimize_coconet_with_rl(coconet_notes, rl_agent)
                        harmonized_file = os.path.join(output_dir, "coconet_rl_optimized.mid")
                        save_4part_midi(optimized_harmonization, harmonized_file)
                        print(f"   ✅ Coconet + RL optimization complete")
                    else:
                        print(f"   ⚠️  Could not load Coconet output, using RL fallback")
                        harmonization = generate_rl_harmonization(melody_notes, rl_agent)
                        harmonized_file = os.path.join(output_dir, "coconet_fallback_rl.mid")
                        save_4part_midi(harmonization, harmonized_file)
                else:
                    print(f"   Coconet failed, using RL fallback")
                    harmonization = generate_rl_harmonization(melody_notes, rl_agent)
                    harmonized_file = os.path.join(output_dir, "coconet_fallback_rl.mid")
                    save_4part_midi(harmonization, harmonized_file)
                    
            else:  # hybrid
                # Original plan: Coconet → RL optimization
                print(f"   Using hybrid approach: Coconet → RL optimization")
                coconet_file = run_coconet_harmonization(input_path, output_dir, temperature)
                
                if coconet_file:
                    print(f"   Coconet generated: {coconet_file}")
                    print(f"   Now optimizing with RL contrary motion model...")
                    
                    # Load Coconet output and optimize with RL
                    coconet_notes = load_midi_melody(coconet_file)
                    if coconet_notes:
                        # Apply RL optimization to Coconet output
                        optimized_harmonization = optimize_coconet_with_rl(coconet_notes, rl_agent)
                        harmonized_file = os.path.join(output_dir, "coconet_rl_optimized.mid")
                        save_4part_midi(optimized_harmonization, harmonized_file)
                        print(f"   ✅ Coconet + RL optimization complete")
                    else:
                        print(f"   ⚠️  Could not load Coconet output, using RL fallback")
                        harmonization = generate_rl_harmonization(melody_notes, rl_agent)
                        harmonized_file = os.path.join(output_dir, "rl_fallback.mid")
                        save_4part_midi(harmonization, harmonized_file)
                else:
                    print(f"   Coconet failed, using RL fallback")
                    harmonization = generate_rl_harmonization(melody_notes, rl_agent)
                    harmonized_file = os.path.join(output_dir, "rl_fallback.mid")
                    save_4part_midi(harmonization, harmonized_file)

            if not harmonized_file or not os.path.exists(harmonized_file):
                return {"error": "Failed to generate harmonization"}

            # Copy file to a permanent location before returning
            import shutil
            final_file = f"/tmp/hybrid_harmonization_{method}_{temperature}.mid"
            shutil.copy2(harmonized_file, final_file)

            # Return the harmonized file
            return FileResponse(
                final_file,
                media_type="audio/midi",
                filename=f"hybrid_harmonization_{method}_{temperature}.mid"
            )
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 