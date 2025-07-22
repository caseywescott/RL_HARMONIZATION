#!/usr/bin/env python3
"""
Fixed Coconet Server - Uses local Coconet model files
"""

import os
import tempfile
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
import subprocess
import sys
import requests
import json
import base64

# Set TF compatibility flags for older models
tf.compat.v1.disable_eager_execution()

# Import our Coconet inference module
from coconet_inference import initialize_coconet, harmonize_with_coconet

app = FastAPI(title="Coconet Harmonization API")

# Model paths - use our local Coconet model
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
CHECKPOINT_PATH = os.path.join(COCONET_MODEL_DIR, "best_model.ckpt")

# Initialize Coconet model lazily (when first needed)
coconet_available = False
coconet_initialized = False

def ensure_coconet_loaded():
    """Ensure Coconet model is loaded (lazy initialization)"""
    global coconet_available, coconet_initialized
    if not coconet_initialized:
        print("🤖 Initializing Coconet neural model...")
        coconet_available = initialize_coconet(COCONET_MODEL_DIR)
        coconet_initialized = True
        if coconet_available:
            print("✅ Coconet neural model loaded successfully!")
        else:
            print("❌ Coconet neural model failed to load, will use fallback")
    return coconet_available

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Coconet Harmonization API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                li { margin-bottom: 10px; }
                code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>Coconet Harmonization API</h1>
            <p>This API provides harmonization using Coconet model.</p>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>POST /generate_music</strong> - Harmonize a MIDI melody</li>
                <li><strong>GET /status</strong> - Check model status</li>
            </ul>
            
            <p>Check out the <a href="/docs">API documentation</a> for more details.</p>
        </body>
    </html>
    """

@app.get("/status")
async def check_status():
    """Check if the Coconet model is available"""
    # Check for the actual checkpoint files that exist
    checkpoint_files = [
        os.path.join(COCONET_MODEL_DIR, "best_model.ckpt.meta"),
        os.path.join(COCONET_MODEL_DIR, "best_model.ckpt.index"),
        os.path.join(COCONET_MODEL_DIR, "best_model.ckpt.data-00000-of-00001")
    ]
    model_exists = all(os.path.exists(f) for f in checkpoint_files)
    
    return {
        "model_available": model_exists,
        "neural_model_loaded": coconet_available,
        "neural_model_initialized": coconet_initialized,
        "model_path": CHECKPOINT_PATH,
        "model_files": os.listdir(COCONET_MODEL_DIR) if os.path.exists(COCONET_MODEL_DIR) else []
    }

def simple_harmonization(midi_data, temperature=1.0, num_steps=512):
    """
    Simple harmonization using music theory rules
    This is a fallback when Coconet model is not available
    """
    try:
        # Parse MIDI data - use BytesIO for reading from bytes
        import io
        midi = pretty_midi.PrettyMIDI(io.BytesIO(midi_data))
        
        # Extract melody (first track)
        if not midi.instruments:
            return None
        
        melody_track = midi.instruments[0]
        melody_notes = []
        
        for note in melody_track.notes:
            melody_notes.append({
                'pitch': note.pitch,
                'start': note.start,
                'end': note.end,
                'velocity': note.velocity
            })
        
        # Create harmonization using simple rules
        harmonized_midi = pretty_midi.PrettyMIDI(initial_tempo=120)
        
        # Melody track
        melody_instrument = pretty_midi.Instrument(program=0, name="Melody")
        for note_data in melody_notes:
            note = pretty_midi.Note(
                velocity=note_data['velocity'],
                pitch=note_data['pitch'],
                start=note_data['start'],
                end=note_data['end']
            )
            melody_instrument.notes.append(note)
        harmonized_midi.instruments.append(melody_instrument)
        
        # Harmony tracks (SATB)
        harmony_programs = [48, 49, 50, 51]  # String quartet
        harmony_names = ["Soprano", "Alto", "Tenor", "Bass"]
        
        for i, (program, name) in enumerate(zip(harmony_programs, harmony_names)):
            harmony_instrument = pretty_midi.Instrument(program=program, name=name)
            
            for j, note_data in enumerate(melody_notes):
                # Simple harmonization rules
                if i == 0:  # Soprano - third above
                    harmony_pitch = note_data['pitch'] + 4
                elif i == 1:  # Alto - fifth above
                    harmony_pitch = note_data['pitch'] + 7
                elif i == 2:  # Tenor - octave below
                    harmony_pitch = note_data['pitch'] - 12
                else:  # Bass - third below
                    harmony_pitch = note_data['pitch'] - 16
                
                # Ensure pitch is in valid range
                harmony_pitch = max(21, min(108, harmony_pitch))
                
                # Add some randomness based on temperature
                if temperature > 1.0:
                    harmony_pitch += np.random.randint(-2, 3)
                    harmony_pitch = max(21, min(108, harmony_pitch))
                
                note = pretty_midi.Note(
                    velocity=note_data['velocity'],
                    pitch=harmony_pitch,
                    start=note_data['start'],
                    end=note_data['end']
                )
                harmony_instrument.notes.append(note)
            
            harmonized_midi.instruments.append(harmony_instrument)
        
        return harmonized_midi
        
    except Exception as e:
        print(f"Error in simple harmonization: {e}")
        return None

@app.post("/generate_music")
async def generate_music(
    file: UploadFile = File(None),
    temperature: float = Query(1.0, description="Controls randomness of generation (0.1-2.0)"),
    num_steps: int = Query(512, description="Number of steps to generate (128-2048)"),
):
    """
    Generate harmonization using Coconet or fallback to simple rules.
    
    - Provide a MIDI file as input melody
    - Adjust temperature to control randomness (lower=more predictable)
    - Set num_steps to control the length of generated music
    """
    try:
        # Read the uploaded MIDI file
        if not file:
            return {"error": "No MIDI file provided"}
        
        midi_data = await file.read()
        
        # Try to use real Coconet neural model first
        coconet_ready = ensure_coconet_loaded()
        if coconet_ready:
            try:
                print(f"🤖 Using Coconet neural model for harmonization...")
                harmonized_midi = harmonize_with_coconet(midi_data, temperature)
                if harmonized_midi is not None:
                    method_used = "Coconet Neural Model"
                else:
                    raise Exception("Coconet harmonization returned None")
            except Exception as e:
                print(f"❌ Coconet neural model failed: {e}")
                print(f"🔄 Falling back to simple rules...")
                harmonized_midi = simple_harmonization(midi_data, temperature, num_steps)
                method_used = "Simple rules (Coconet failed)"
        else:
            # Use simple harmonization as fallback
            print(f"🔄 Using simple rules harmonization (no neural model)")
            harmonized_midi = simple_harmonization(midi_data, temperature, num_steps)
            method_used = "Simple rules (no neural model)"
        
        if not harmonized_midi:
            return {"error": "Failed to generate harmonization"}
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_file:
            harmonized_midi.write(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Return the harmonized MIDI file
        return FileResponse(
            tmp_path,
            media_type="audio/midi",
            filename="coconet_harmonized.mid",
            headers={"X-Method-Used": method_used}
        )
        
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}

@app.post("/generate_music_json")
async def generate_music_json(
    file: UploadFile = File(None),
    temperature: float = Query(1.0, description="Controls randomness of generation (0.1-2.0)"),
    num_steps: int = Query(512, description="Number of steps to generate (128-2048)"),
):
    """
    Generate harmonization and return as JSON with base64 encoded MIDI.
    """
    try:
        # Read the uploaded MIDI file
        if not file:
            return {"error": "No MIDI file provided"}
        
        midi_data = await file.read()
        
        # Try to use real Coconet neural model first
        coconet_ready = ensure_coconet_loaded()
        if coconet_ready:
            try:
                print(f"🤖 Using Coconet neural model for harmonization...")
                harmonized_midi = harmonize_with_coconet(midi_data, temperature)
                if harmonized_midi is None:
                    raise Exception("Coconet harmonization returned None")
                method_used = "Coconet Neural Model"
            except Exception as e:
                print(f"❌ Coconet neural model failed: {e}")
                print(f"🔄 Falling back to simple rules...")
                harmonized_midi = simple_harmonization(midi_data, temperature, num_steps)
                method_used = "Simple rules (Coconet failed)"
        else:
            # Use simple harmonization as fallback
            print(f"🔄 Using simple rules harmonization (no neural model)")
            harmonized_midi = simple_harmonization(midi_data, temperature, num_steps)
            method_used = "Simple rules (no neural model)"
        
        if not harmonized_midi:
            return {"error": "Failed to generate harmonization"}
        
        # Save to temporary file and encode as base64
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_file:
            harmonized_midi.write(tmp_file.name)
            
            # Read the file and encode as base64
            with open(tmp_file.name, 'rb') as f:
                harmonized_midi_data = f.read()
            
            # Clean up
            os.unlink(tmp_file.name)
        
        # Encode as base64
        harmonized_midi_base64 = base64.b64encode(harmonized_midi_data).decode('utf-8')
        
        return {
            "status": "success",
            "method": method_used,
            "harmonized_midi": harmonized_midi_base64,
            "temperature": temperature,
            "num_steps": num_steps
        }
        
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 