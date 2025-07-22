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
import shutil

app = FastAPI(title="Melody-Copy Coconet Harmonization Server", version="1.0")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
MAGENTA_COCONET_DIR = "/app/magenta/models/coconet"

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Melody-Copy Coconet Harmonization Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
                .method { color: #007cba; font-weight: bold; }
                .url { color: #333; font-family: monospace; }
                .description { color: #666; }
                .highlight { background: #fff3cd; padding: 10px; border-radius: 5px; }
                .warning { background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎼 Melody-Copy Coconet Harmonization Server</h1>
                <div class="highlight">
                    <strong>🎵 Key Feature:</strong> This server GUARANTEES the original melody is preserved by copying it into the harmonized output!
                </div>
                
                <div class="warning">
                    <strong>⚠️  Problem Solved:</strong> Previous harmonizations were missing the original melody entirely. This server fixes that by enforcing melody preservation.
                </div>

                <p>This server uses the official Magenta Coconet scripts with guaranteed melody preservation through post-processing.</p>

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

                <h2>How Melody Preservation Works:</h2>
                <ol>
                    <li><strong>Extract Original Melody</strong> - Parse the input MIDI to get exact melody notes</li>
                    <li><strong>Run Coconet Harmonization</strong> - Generate 4-voice harmonization</li>
                    <li><strong>Copy Original Melody</strong> - Replace the first instrument with the exact original melody</li>
                    <li><strong>Enhance Audibility</strong> - Boost melody velocity and reduce harmony velocity</li>
                    <li><strong>Verify Preservation</strong> - Ensure the output contains the original melody</li>
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
        "harmonization_method": "Melody-Copy Coconet Gibbs Sampling",
        "default_temperature": 0.7,
        "melody_preservation": "guaranteed_copy"
    }

def copy_original_melody_to_harmonization(original_midi_path: str, harmonized_midi_path: str, 
                                        melody_strength: float = 2.0, harmony_reduction: float = 0.6):
    """
    Copy the original melody into the harmonized MIDI file
    
    Args:
        original_midi_path: Path to original MIDI file
        harmonized_midi_path: Path to harmonized MIDI file (will be modified)
        melody_strength: Velocity multiplier for melody
        harmony_reduction: Velocity reduction factor for harmony
    """
    try:
        print(f"   Copying original melody to harmonization...")
        
        # Load original and harmonized MIDI
        original_midi = pretty_midi.PrettyMIDI(original_midi_path)
        harmonized_midi = pretty_midi.PrettyMIDI(harmonized_midi_path)
        
        if not original_midi.instruments or not harmonized_midi.instruments:
            print(f"   ❌ Missing instruments in MIDI files")
            return False
        
        # Extract original melody notes
        original_melody_notes = []
        for note in original_midi.instruments[0].notes:
            original_melody_notes.append({
                'pitch': note.pitch,
                'start': note.start,
                'end': note.end,
                'velocity': note.velocity
            })
        
        print(f"   Original melody: {len(original_melody_notes)} notes")
        
        # Replace the first instrument (melody) with original melody
        if harmonized_midi.instruments:
            # Clear the first instrument
            harmonized_midi.instruments[0].notes.clear()
            
            # Add original melody notes with enhanced velocity
            for note_data in original_melody_notes:
                note = pretty_midi.Note(
                    velocity=min(127, int(note_data['velocity'] * melody_strength)),
                    pitch=note_data['pitch'],
                    start=note_data['start'],
                    end=note_data['end']
                )
                harmonized_midi.instruments[0].notes.append(note)
            
            print(f"   ✅ Copied {len(original_melody_notes)} original melody notes to first instrument")
            
            # Reduce velocity of harmony instruments
            for instrument in harmonized_midi.instruments[1:]:
                for note in instrument.notes:
                    note.velocity = max(40, int(note.velocity * harmony_reduction))
            
            print(f"   ✅ Reduced harmony velocities by factor {harmony_reduction}")
            
            # Save the modified harmonized MIDI
            harmonized_midi.write(harmonized_midi_path)
            print(f"   ✅ Saved harmonized MIDI with original melody")
            
            return True
        else:
            print(f"   ❌ No instruments in harmonized MIDI")
            return False
            
    except Exception as e:
        print(f"   ❌ Error copying melody: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_melody_preservation(original_midi_path: str, harmonized_midi_path: str):
    """Verify that the original melody is preserved in the harmonization"""
    try:
        print(f"   Verifying melody preservation...")
        
        # Load both MIDI files
        original_midi = pretty_midi.PrettyMIDI(original_midi_path)
        harmonized_midi = pretty_midi.PrettyMIDI(harmonized_midi_path)
        
        if not original_midi.instruments or not harmonized_midi.instruments:
            return False
        
        # Extract original melody
        original_notes = []
        for note in original_midi.instruments[0].notes:
            original_notes.append(note.pitch)
        
        # Extract harmonized melody (first instrument)
        harmonized_notes = []
        for note in harmonized_midi.instruments[0].notes:
            harmonized_notes.append(note.pitch)
        
        # Check if they match
        if original_notes == harmonized_notes:
            print(f"   ✅ VERIFICATION PASSED: Original melody is preserved!")
            return True
        else:
            print(f"   ❌ VERIFICATION FAILED: Melody mismatch")
            print(f"      Original: {original_notes}")
            print(f"      Harmonized: {harmonized_notes}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in verification: {e}")
        return False

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.7, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
    melody_strength: float = Query(2.0, description="Melody velocity multiplier (1.0-3.0)", ge=1.0, le=3.0),
    harmony_reduction: float = Query(0.6, description="Harmony velocity reduction factor (0.1-1.0)", ge=0.1, le=1.0),
):
    """Harmonize a MIDI melody with guaranteed melody preservation"""
    try:
        print(f"🎵 Received melody-copy harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
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
            piece_length = max(32, int(duration_seconds / 0.25) + 8)

            print(f"   Input duration: {duration_seconds:.2f} seconds")
            print(f"   Calculated piece length: {piece_length} time steps")

            # Create output directory
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)

            # Run the official Coconet sampling script
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

            print(f"   Running Coconet harmonization...")
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

            # CRITICAL STEP: Copy original melody into harmonization
            print(f"   Applying melody copy-over...")
            success = copy_original_melody_to_harmonization(
                input_midi_path, 
                harmonized_file, 
                melody_strength, 
                harmony_reduction
            )
            
            if not success:
                raise Exception("Failed to copy original melody to harmonization")

            # Verify melody preservation
            print(f"   Verifying melody preservation...")
            verification_success = verify_melody_preservation(input_midi_path, harmonized_file)
            
            if not verification_success:
                print(f"   ⚠️  Warning: Melody preservation verification failed")
            else:
                print(f"   ✅ Melody preservation verified successfully!")

            print(f"   Returning harmonized file with guaranteed melody preservation: {harmonized_file}")

            # Copy the file to a persistent location before the temp directory is cleaned up
            persistent_file = f"/tmp/melody_copy_harmonized_{file.filename}"
            shutil.copy2(harmonized_file, persistent_file)

            return FileResponse(
                persistent_file,
                media_type="audio/midi",
                filename=f"melody_copy_harmonized_{file.filename}"
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