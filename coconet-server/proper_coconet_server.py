#!/usr/bin/env python3
"""
Proper Coconet Harmonization Server

This server implements the actual Coconet harmonization process using Gibbs sampling.
"""

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

app = FastAPI(title="Proper Coconet Harmonization Server", version="1.0")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
MAGENTA_COCONET_DIR = "/app/magenta_coconet"

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Proper Coconet Harmonization Server</title>
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
                <h1>🎼 Proper Coconet Harmonization Server</h1>
                <p>This server uses the official Magenta Coconet scripts with the <code>harmonize_midi_melody</code> strategy for authentic Bach-style harmonization.</p>
                
                <div class="endpoint">
                    <div class="method">GET</div>
                    <div class="url">/status</div>
                    <div class="description">Check server status and model availability</div>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST</div>
                    <div class="url">/harmonize</div>
                    <div class="description">Harmonize a MIDI melody using official Coconet</div>
                    <p><strong>Parameters:</strong></p>
                    <ul>
                        <li><code>file</code>: MIDI file containing melody to harmonize</li>
                        <li><code>temperature</code>: Sampling temperature (0.1-2.0, default: 0.99)</li>
                    </ul>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/status")
async def get_status():
    """Check server status and model availability"""
    model_available = os.path.exists(COCONET_MODEL_DIR) and os.path.exists(os.path.join(COCONET_MODEL_DIR, "best_model.ckpt.meta"))
    magenta_scripts_available = os.path.exists(MAGENTA_COCONET_DIR) and os.path.exists(os.path.join(MAGENTA_COCONET_DIR, "coconet_sample.py"))
    
    return {
        "server_status": "running",
        "model_available": model_available,
        "magenta_scripts_available": magenta_scripts_available,
        "model_path": COCONET_MODEL_DIR,
        "magenta_scripts_path": MAGENTA_COCONET_DIR,
        "harmonization_method": "Official Coconet Script (harmonize_midi_melody strategy)"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """Harmonize a MIDI melody using the official coconet_sample.py script"""
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as temp_input_file:
            content = await file.read()
            temp_input_file.write(content)
            temp_input_path = temp_input_file.name
        
        temp_output_path = temp_input_path.replace(".mid", "_harmonized.mid")
        
        try:
            # Construct the command to run coconet_sample.py
            # This uses the official harmonize_midi_melody strategy
            command = [
                "python",
                os.path.join(MAGENTA_COCONET_DIR, "coconet_sample.py"),
                f"--checkpoint={COCONET_MODEL_DIR}",
                "--strategy=harmonize_midi_melody",  # This is the key strategy for harmonization
                f"--prime_midi_melody_fpath={temp_input_path}",
                f"--generation_output_dir=/tmp",
                f"--temperature={temperature}",
                "--gen_batch_size=1",
                "--piece_length=32",
                "--logtostderr"  # To see logs from the script
            ]
            
            print(f"   Running command: {' '.join(command)}")
            
            # Run the subprocess
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            
            print("   Subprocess stdout:")
            print(process.stdout)
            print("   Subprocess stderr:")
            print(process.stderr)
            
            # The script creates output in /tmp/sample_* directory
            # We need to find the generated MIDI file
            output_dir = None
            for item in os.listdir("/tmp"):
                if item.startswith("sample_") and os.path.isdir(os.path.join("/tmp", item)):
                    output_dir = os.path.join("/tmp", item)
                    break
            
            if output_dir and os.path.exists(output_dir):
                midi_dir = os.path.join(output_dir, "midi")
                if os.path.exists(midi_dir):
                    # Find the generated MIDI file
                    midi_files = [f for f in os.listdir(midi_dir) if f.endswith(".mid")]
                    if midi_files:
                        generated_midi_path = os.path.join(midi_dir, midi_files[0])
                        
                        # Copy to our output path
                        import shutil
                        shutil.copy2(generated_midi_path, temp_output_path)
                        
                        if os.path.exists(temp_output_path) and os.path.getsize(temp_output_path) > 0:
                            # Return the harmonized file
                            return FileResponse(
                                temp_output_path,
                                media_type="audio/midi",
                                filename=f"proper_coconet_harmonized_{file.filename}"
                            )
            
            raise RuntimeError("Coconet script did not produce a valid output MIDI file.")
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Coconet script: {e}")
        print(f"   Stdout: {e.stdout}")
        print(f"   Stderr: {e.stderr}")
        return {"error": f"Coconet script failed: {e.stderr}"}
    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 