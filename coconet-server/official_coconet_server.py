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

app = FastAPI(title="Official Coconet Harmonization Server", version="1.0")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
MAGENTA_COCONET_DIR = "/app/magenta/models/coconet"

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Official Coconet Harmonization Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
                .method { color: #007cba; font-weight: bold; }
                .url { color: #333; font-family: monospace; }
                .description { color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎼 Official Coconet Harmonization Server</h1>
                <p>This server uses the official Magenta Coconet scripts to perform Bach-style harmonization.</p>
                
                <div class="endpoint">
                    <div class="method">GET</div>
                    <div class="url">/status</div>
                    <div class="description">Check server status and model availability</div>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST</div>
                    <div class="url">/harmonize</div>
                    <div class="description">Harmonize a MIDI melody using official Coconet Gibbs sampling</div>
                    <p><strong>Parameters:</strong></p>
                    <ul>
                        <li><code>file</code>: MIDI file containing melody to harmonize</li>
                        <li><code>temperature</code>: Sampling temperature (0.1-2.0, default: 0.99)</li>
                    </ul>
                </div>
                
                <h2>How it works:</h2>
                <ol>
                    <li>Upload a MIDI file containing a melody</li>
                    <li>The server runs the official <code>coconet_sample.py</code> script</li>
                    <li>Coconet performs Gibbs sampling with harmonization masking</li>
                    <li>Returns a 4-part Bach-style harmonization</li>
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
        "harmonization_method": "Official Coconet Gibbs Sampling"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """Harmonize a MIDI melody using official Coconet Gibbs sampling"""
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded MIDI file
            input_midi_path = os.path.join(temp_dir, "input.mid")
            with open(input_midi_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            print(f"   Saved input MIDI to: {input_midi_path}")
            
            # Analyze the input MIDI to determine appropriate piece length
            import pretty_midi
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
            
            print(f"   Running command: {' '.join(cmd)}")
            
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
            if result.stdout:
                print(f"   stdout: {result.stdout}")
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
            
            # Return the first MIDI file
            output_file = os.path.join(midi_dir, midi_files[0])
            
            print(f"   Returning harmonized file: {output_file}")
            
            # Copy the file to a persistent location before the temp directory is cleaned up
            persistent_file = f"/tmp/coconet_output_{file.filename}"
            import shutil
            shutil.copy2(output_file, persistent_file)
            
            return FileResponse(
                persistent_file,
                media_type="audio/midi",
                filename=f"coconet_harmonized_{file.filename}"
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