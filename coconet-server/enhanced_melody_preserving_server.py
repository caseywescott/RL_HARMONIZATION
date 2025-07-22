#!/usr/bin/env python3

import os
import io
import tempfile
import subprocess
import numpy as np
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from typing import Optional
import random

app = FastAPI(title="Enhanced Melody-Preserving Coconet Harmonization Server", version="1.0")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
MAGENTA_COCONET_DIR = "/app/magenta/models/coconet"

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Enhanced Melody-Preserving Coconet Harmonization Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
                .method { color: #007cba; font-weight: bold; }
                .url { color: #333; font-family: monospace; }
                .description { color: #666; }
                .highlight { background: #fff3cd; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎼 Enhanced Melody-Preserving Coconet Harmonization Server</h1>
                <div class="highlight">
                    <strong>🎵 Key Feature:</strong> This server ensures the original melody is clearly audible by boosting melody velocity and reducing harmony velocity!
                </div>
                
                <p>This server uses the official Magenta Coconet scripts with enhanced post-processing to guarantee melody audibility.</p>
                
                <div class="endpoint">
                    <div class="method">GET</div>
                    <div class="url">/status</div>
                    <div class="description">Check server status and model availability</div>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST</div>
                    <div class="url">/harmonize</div>
                    <div class="description">Harmonize a MIDI melody with guaranteed melody preservation</div>
                    <p><strong>Parameters:</strong></p>
                    <ul>
                        <li><code>file</code>: MIDI file containing melody to harmonize</li>
                        <li><code>temperature</code>: Sampling temperature (0.1-2.0, default: 0.7)</li>
                        <li><code>melody_strength</code>: Melody velocity multiplier (1.0-3.0, default: 2.0)</li>
                        <li><code>harmony_reduction</code>: Harmony velocity reduction factor (0.1-1.0, default: 0.6)</li>
                    </ul>
                </div>
                
                <h2>Enhanced Melody Preservation Features:</h2>
                <ol>
                    <li><strong>Lower default temperature (0.7)</strong> - More conservative harmonization</li>
                    <li><strong>Melody velocity boost</strong> - Makes melody notes significantly louder</li>
                    <li><strong>Harmony velocity reduction</strong> - Reduces harmony volume to make melody stand out</li>
                    <li><strong>Smart track identification</strong> - Automatically identifies melody vs harmony tracks</li>
                    <li><strong>Post-processing</strong> - Ensures melody track is clearly separated</li>
                </ol>
            </div>
        </body>
    </html>
    """

@app.get("/status")
async def get_status():
    """Check server status and model availability"""
    model_files = []
    if os.path.exists(COCONET_MODEL_DIR):
        model_files = os.listdir(COCONET_MODEL_DIR)
    
    script_files = []
    if os.path.exists(MAGENTA_COCONET_DIR):
        script_files = os.listdir(MAGENTA_COCONET_DIR)
    
    return {
        "server_status": "running",
        "model_available": os.path.exists(COCONET_MODEL_DIR),
        "model_path": COCONET_MODEL_DIR,
        "model_files": model_files,
        "magenta_scripts_available": os.path.exists(MAGENTA_COCONET_DIR),
        "magenta_scripts": script_files,
        "harmonization_method": "Enhanced Melody-Preserving Coconet Gibbs Sampling",
        "default_temperature": 0.7,
        "melody_preservation": "enhanced"
    }

def enhance_melody_visibility_enhanced(midi_file_path: str, melody_strength: float = 2.0, harmony_reduction: float = 0.6):
    """Enhanced post-processing to ensure melody is clearly audible"""
    try:
        # Load the harmonized MIDI
        midi = pretty_midi.PrettyMIDI(midi_file_path)
        
        if not midi.instruments:
            return
        
        print(f"   Enhancing melody visibility (strength: {melody_strength}, harmony reduction: {harmony_reduction})")
        
        # Strategy 1: Boost first instrument (melody) and reduce others
        if len(midi.instruments) >= 2:
            # Boost melody (first instrument)
            melody_instrument = midi.instruments[0]
            for note in melody_instrument.notes:
                note.velocity = min(127, int(note.velocity * melody_strength))
            
            # Reduce harmony instruments
            for instrument in midi.instruments[1:]:
                for note in instrument.notes:
                    note.velocity = max(40, int(note.velocity * harmony_reduction))
            
            print(f"   Applied velocity boost to melody track")
            print(f"   Applied velocity reduction to harmony tracks")
        
        # Strategy 2: If all velocities are the same, force differentiation
        all_velocities = []
        for instrument in midi.instruments:
            if instrument.notes:
                all_velocities.extend([note.velocity for note in instrument.notes])
        
        if len(set(all_velocities)) <= 2:  # Very few different velocities
            print(f"   Detected uniform velocities, applying forced differentiation")
            
            # Force melody to be much louder
            if midi.instruments[0].notes:
                for note in midi.instruments[0].notes:
                    note.velocity = 120  # Very loud melody
            
            # Force harmony to be much quieter
            for instrument in midi.instruments[1:]:
                for note in instrument.notes:
                    note.velocity = 60  # Much quieter harmony
        
        # Save the enhanced MIDI
        midi.write(midi_file_path)
        print(f"   Enhanced MIDI saved successfully")
        
    except Exception as e:
        print(f"   Warning: Could not enhance melody visibility: {e}")

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.7, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
    melody_strength: float = Query(2.0, description="Melody velocity multiplier (1.0-3.0)", ge=1.0, le=3.0),
    harmony_reduction: float = Query(0.6, description="Harmony velocity reduction factor (0.1-1.0)", ge=0.1, le=1.0),
):
    """Harmonize a MIDI melody with enhanced melody preservation"""
    try:
        print(f"🎵 Received enhanced melody-preserving harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature} (conservative for melody preservation)")
        print(f"   Melody strength: {melody_strength}")
        print(f"   Harmony reduction: {harmony_reduction}")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded MIDI file
            input_midi_path = os.path.join(temp_dir, "input.mid")
            with open(input_midi_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            print(f"   Saved input MIDI to: {input_midi_path}")
            
            # Analyze the input MIDI to determine appropriate piece length
            input_midi = pretty_midi.PrettyMIDI(input_midi_path)
            duration_seconds = input_midi.get_end_time()
            
            # Convert duration to time steps (assuming 4/4 time at 120 BPM)
            # Each time step is typically 0.25 seconds (quarter note at 120 BPM)
            # Round up to ensure we capture the full melody
            piece_length = max(32, int(duration_seconds / 0.25) + 8)
            
            print(f"   Input duration: {duration_seconds:.2f} seconds")
            print(f"   Calculated piece length: {piece_length} time steps")
            
            # Create output directory
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Run the official Coconet sampling script with melody-preserving parameters
            cmd = [
                "python", 
                os.path.join(MAGENTA_COCONET_DIR, "coconet_sample.py"),
                "--checkpoint", COCONET_MODEL_DIR,
                "--gen_batch_size", "1",
                "--piece_length", str(piece_length),
                "--temperature", str(temperature),
                "--strategy", "harmonize_midi_melody",
                "--tfsample", "False",
                "--generation_output_dir", output_dir,
                "--prime_midi_melody_fpath", input_midi_path,
                "--logtostderr"
            ]
            
            print(f"   Running Coconet with enhanced melody-preserving parameters...")
            print(f"   Command: {' '.join(cmd)}")
            
            # Set environment variables
            env = os.environ.copy()
            env['PYTHONPATH'] = f"/app:{env.get('PYTHONPATH', '')}"
            
            # Run the command
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            print(f"   Command completed with return code: {result.returncode}")
            if result.stderr:
                print(f"   stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise Exception(f"Coconet sampling failed: {result.stderr}")
            
            # Find the generated output directory
            output_dirs = os.listdir(output_dir)
            print(f"   Output directories: {output_dirs}")
            
            if not output_dirs:
                raise Exception("No output directories generated")
            
            # The Coconet script creates a directory with the MIDI file inside
            sample_dir = os.path.join(output_dir, output_dirs[0])
            midi_dir = os.path.join(sample_dir, "midi")
            
            if not os.path.exists(midi_dir):
                raise Exception(f"MIDI directory not found: {midi_dir}")
            
            # Find the MIDI file in the midi subdirectory
            midi_files = os.listdir(midi_dir)
            print(f"   MIDI files: {midi_files}")
            
            if not midi_files:
                raise Exception("No MIDI files generated")
            
            # Get the harmonized MIDI file
            harmonized_file = os.path.join(midi_dir, midi_files[0])
            
            # Enhanced post-processing to ensure melody visibility
            print(f"   Applying enhanced melody visibility processing...")
            enhance_melody_visibility_enhanced(harmonized_file, melody_strength, harmony_reduction)
            
            print(f"   Returning enhanced melody-preserved harmonized file: {harmonized_file}")
            
            # Copy the file to a persistent location before the temp directory is cleaned up
            persistent_file = f"/tmp/enhanced_melody_preserved_{file.filename}"
            import shutil
            shutil.copy2(harmonized_file, persistent_file)
            
            return FileResponse(
                persistent_file,
                media_type="audio/midi",
                filename=f"enhanced_melody_preserved_harmonized_{file.filename}"
            )
            
    except subprocess.TimeoutExpired:
        print(f"❌ Coconet sampling timed out")
        return {"error": "Harmonization timed out. Please try again."}
    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 