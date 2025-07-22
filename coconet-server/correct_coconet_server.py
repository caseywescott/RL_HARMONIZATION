#!/usr/bin/env python3
"""
Correct Coconet Harmonization Server

This server uses the proper Coconet sampling scripts for harmonization,
following the official Coconet methodology with Gibbs sampling.
"""

import os
import io
import tempfile
import subprocess
import sys
import numpy as np
from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from pydantic import BaseModel
from typing import Optional

# Add Magenta Coconet to path
sys.path.insert(0, '/app/magenta_coconet')

app = FastAPI(title="Correct Coconet Harmonization API")

# Model configuration
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
MAGENTA_COCONET_DIR = "/app/magenta_coconet"

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Correct Coconet Harmonization API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                li { margin-bottom: 10px; }
                code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
                .success { color: #28a745; }
                .warning { color: #ffc107; }
            </style>
        </head>
        <body>
            <h1>🎵 Correct Coconet Harmonization API</h1>
            <p>This API uses the <strong>official Coconet sampling scripts</strong> for proper harmonization.</p>
            
            <h2>Key Features:</h2>
            <ul>
                <li><span class="success">✅ Uses Gibbs sampling (igibbs strategy)</span></li>
                <li><span class="success">✅ Proper harmonization masking</span></li>
                <li><span class="success">✅ Yao schedule for sampling</span></li>
                <li><span class="success">✅ Official Coconet methodology</span></li>
            </ul>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>GET /status</strong> - Check model status</li>
                <li><strong>POST /harmonize</strong> - Harmonize using proper Coconet</li>
            </ul>
            
            <p>Check out the <a href="/docs">API documentation</a> for more details.</p>
        </body>
    </html>
    """

@app.get("/status")
async def get_status():
    """Get the status of the harmonization model"""
    # Check if model files exist
    model_files = []
    if os.path.exists(COCONET_MODEL_DIR):
        model_files = os.listdir(COCONET_MODEL_DIR)
    
    # Check if Magenta Coconet scripts exist
    magenta_files = []
    if os.path.exists(MAGENTA_COCONET_DIR):
        magenta_files = os.listdir(MAGENTA_COCONET_DIR)
    
    return {
        "model_available": len(model_files) > 0,
        "magenta_scripts_available": len(magenta_files) > 0,
        "model_path": COCONET_MODEL_DIR,
        "magenta_path": MAGENTA_COCONET_DIR,
        "model_files": model_files,
        "magenta_files": magenta_files,
        "harmonization_method": "Official Coconet Gibbs Sampling"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
    piece_length: int = Query(32, description="Number of time steps", ge=16, le=128),
):
    """
    Harmonize a melody using the official Coconet sampling scripts
    
    This endpoint:
    1. Takes a melody from the input MIDI file
    2. Uses the HarmonizeMidiMelodyStrategy with Gibbs sampling
    3. Applies proper harmonization masking
    4. Returns a harmonized MIDI file
    
    - **file**: MIDI file containing the melody to harmonize
    - **temperature**: Controls randomness (lower = more predictable, higher = more creative)
    - **piece_length**: Number of time steps in the generated piece
    """
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        print(f"   Piece length: {piece_length}")
        
        # Read the uploaded file
        midi_data = await file.read()
        print(f"   File size: {len(midi_data)} bytes")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save input MIDI
            input_midi_path = os.path.join(temp_dir, "input.mid")
            with open(input_midi_path, "wb") as f:
                f.write(midi_data)
            
            # Create output directory
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            print("🤖 Running Coconet harmonization with proper sampling...")
            
            # Run the Coconet sampling script with harmonization strategy
            cmd = [
                "python", 
                os.path.join(MAGENTA_COCONET_DIR, "coconet_sample.py"),
                "--checkpoint", COCONET_MODEL_DIR,
                "--strategy", "harmonize_midi_melody",
                "--prime_midi_melody_fpath", input_midi_path,
                "--temperature", str(temperature),
                "--piece_length", str(piece_length),
                "--gen_batch_size", "1",
                "--generation_output_dir", output_dir,
                "--tfsample", "True"
            ]
            
            print(f"   Command: {' '.join(cmd)}")
            
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=MAGENTA_COCONET_DIR
            )
            
            print(f"   Return code: {result.returncode}")
            if result.stdout:
                print(f"   Stdout: {result.stdout}")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")
            
            if result.returncode != 0:
                print("❌ Coconet sampling failed")
                return {"error": f"Coconet sampling failed: {result.stderr}"}
            
            # Find the generated MIDI file
            generated_midi = None
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.mid'):
                        generated_midi = os.path.join(root, file)
                        break
                if generated_midi:
                    break
            
            if generated_midi and os.path.exists(generated_midi):
                print(f"✅ Harmonization completed: {generated_midi}")
                
                # Read the generated MIDI
                with open(generated_midi, 'rb') as f:
                    harmonized_data = f.read()
                
                # Save to a temporary file for response
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_file:
                    tmp_file.write(harmonized_data)
                    tmp_file_path = tmp_file.name
                
                # Return the harmonized file
                return FileResponse(
                    tmp_file_path,
                    media_type="audio/midi",
                    filename=f"correct_coconet_harmonization_{temperature}.mid"
                )
            else:
                print("❌ No harmonized MIDI file found")
                return {"error": "No harmonized MIDI file generated"}
            
    except Exception as e:
        print(f"❌ Error in harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

@app.post("/generate_music")
async def generate_music(
    file: UploadFile = File(None),
    temperature: float = Query(0.99, description="Controls randomness of generation (0.1-2.0)"),
    num_steps: int = Query(32, description="Number of steps to generate (16-128)"),
):
    """
    Legacy endpoint - redirects to proper harmonization
    
    This endpoint is maintained for compatibility but now uses proper Coconet sampling.
    """
    print("🔄 Legacy endpoint called - redirecting to proper harmonization")
    
    if file is None:
        return {"error": "No file provided"}
    
    # Redirect to proper harmonization
    return await harmonize_melody(file=file, temperature=temperature, piece_length=num_steps)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 