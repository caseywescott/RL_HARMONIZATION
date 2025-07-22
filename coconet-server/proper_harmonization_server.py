#!/usr/bin/env python3
"""
Proper Coconet Harmonization Server

This server properly uses Coconet for harmonization with masking,
preserving the original melody and generating appropriate harmony parts.
"""

import os
import io
import tempfile
import numpy as np
from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from pydantic import BaseModel
from typing import Optional

# Import our proper Coconet implementation
from coconet_inference import initialize_coconet, harmonize_with_coconet

app = FastAPI(title="Proper Coconet Harmonization API")

# Model configuration
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"

# Initialize Coconet model lazily (when first needed)
coconet_available = False
coconet_initialized = False

def ensure_coconet_loaded():
    """Ensure Coconet model is loaded"""
    global coconet_available, coconet_initialized
    if not coconet_initialized:
        print("🤖 Initializing proper Coconet harmonization model...")
        coconet_available = initialize_coconet(COCONET_MODEL_DIR)
        coconet_initialized = True
        if coconet_available:
            print("✅ Proper Coconet harmonization model loaded successfully!")
        else:
            print("❌ Failed to load proper Coconet harmonization model")
    return coconet_available

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Proper Coconet Harmonization API</title>
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
            <h1>🎵 Proper Coconet Harmonization API</h1>
            <p>This API provides <strong>proper harmonization</strong> using Coconet with masking.</p>
            
            <h2>Key Features:</h2>
            <ul>
                <li><span class="success">✅ Preserves original melody</span></li>
                <li><span class="success">✅ Generates proper 4-part harmony</span></li>
                <li><span class="success">✅ Uses masking for authentic harmonization</span></li>
                <li><span class="success">✅ Maintains original timing and structure</span></li>
            </ul>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>GET /status</strong> - Check model status</li>
                <li><strong>POST /harmonize</strong> - Harmonize a melody with proper Coconet</li>
            </ul>
            
            <p>Check out the <a href="/docs">API documentation</a> for more details.</p>
        </body>
    </html>
    """

@app.get("/status")
async def get_status():
    """Get the status of the harmonization model"""
    coconet_ready = ensure_coconet_loaded()
    
    # Check if model files exist
    model_files = []
    if os.path.exists(COCONET_MODEL_DIR):
        model_files = os.listdir(COCONET_MODEL_DIR)
    
    return {
        "model_available": coconet_ready,
        "neural_model_loaded": coconet_ready,
        "neural_model_initialized": coconet_initialized,
        "model_path": COCONET_MODEL_DIR,
        "model_files": model_files,
        "harmonization_method": "Proper Coconet with Masking"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(1.0, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """
    Harmonize a melody using proper Coconet implementation
    
    This endpoint:
    1. Takes a melody from the input MIDI file
    2. Preserves the melody in the first voice
    3. Generates proper 4-part harmony using Coconet masking
    4. Returns a harmonized MIDI file
    
    - **file**: MIDI file containing the melody to harmonize
    - **temperature**: Controls randomness (lower = more predictable, higher = more creative)
    """
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        
        # Read the uploaded file
        midi_data = await file.read()
        print(f"   File size: {len(midi_data)} bytes")
        
        # Ensure Coconet is loaded
        coconet_ready = ensure_coconet_loaded()
        
        if coconet_ready:
            print("🤖 Using proper Coconet harmonization...")
            
            # Harmonize using proper Coconet implementation
            harmonized_midi = harmonize_with_coconet(midi_data, temperature)
            
            if harmonized_midi is not None:
                print("✅ Proper harmonization completed successfully")
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_file:
                    harmonized_midi.write(tmp_file.name)
                    tmp_file_path = tmp_file.name
                
                # Return the harmonized file
                return FileResponse(
                    tmp_file_path,
                    media_type="audio/midi",
                    filename=f"proper_coconet_harmonization_{temperature}.mid"
                )
            else:
                print("❌ Proper Coconet harmonization failed")
                return {"error": "Proper Coconet harmonization failed"}
        else:
            print("❌ Coconet model not available")
            return {"error": "Coconet model not available"}
            
    except Exception as e:
        print(f"❌ Error in harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

@app.post("/generate_music")
async def generate_music(
    file: UploadFile = File(None),
    temperature: float = Query(1.0, description="Controls randomness of generation (0.1-2.0)"),
    num_steps: int = Query(512, description="Number of steps to generate (128-2048)"),
):
    """
    Legacy endpoint - redirects to proper harmonization
    
    This endpoint is maintained for compatibility but now uses proper harmonization.
    """
    print("🔄 Legacy endpoint called - redirecting to proper harmonization")
    
    if file is None:
        return {"error": "No file provided"}
    
    # Redirect to proper harmonization
    return await harmonize_melody(file=file, temperature=temperature)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 