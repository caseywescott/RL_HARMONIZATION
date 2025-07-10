import os
import tempfile
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from pydantic import BaseModel
import subprocess
import sys
import requests

# Set TF compatibility flags for older models
tf.compat.v1.disable_eager_execution()

app = FastAPI(title="Music Transformer API")

# Model paths and configs
CHECKPOINT_DIR = "/app/models/music_transformer"

# Class for generation parameters
class GenerationParams(BaseModel):
    temperature: float = 1.0
    num_steps: int = 1024
    primer_midi: str = None
    
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Music Transformer API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                li { margin-bottom: 10px; }
                code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>Music Transformer API</h1>
            <p>This API provides endpoints for music generation using Magenta's Music Transformer model.</p>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>POST /generate_music</strong> - Generate music with optional MIDI file primer</li>
                <li><strong>GET /download_checkpoints</strong> - Download pretrained model checkpoints</li>
                <li><strong>GET /list_models</strong> - List available model checkpoints</li>
            </ul>
            
            <p>Check out the <a href="/docs">API documentation</a> for more details.</p>
        </body>
    </html>
    """

@app.post("/generate_music")
async def generate_music(
    file: UploadFile = File(None),
    temperature: float = Query(1.0, description="Controls randomness of generation (0.1-2.0)"),
    num_steps: int = Query(512, description="Number of steps to generate (128-2048)"),
):
    """
    Generate music using Music Transformer.
    
    - Optionally provide a MIDI file as a primer
    - Adjust temperature to control randomness (lower=more predictable)
    - Set num_steps to control the length of generated music
    """
    # Create a temporary directory for our files
    with tempfile.TemporaryDirectory() as temp_dir:
        primer_path = None
        output_path = os.path.join(temp_dir, "generated.mid")
        
        # If a primer file was uploaded, save it
        if file:
            primer_path = os.path.join(temp_dir, "primer.mid")
            contents = await file.read()
            with open(primer_path, "wb") as f:
                f.write(contents)
        
        # Build the command to run the Music Transformer
        cmd = [
            "python", 
            "/magenta/magenta/models/score2perf/score2perf_generate.py",
            "--output_dir", temp_dir,
            "--checkpoint_dir", CHECKPOINT_DIR,
            "--num_outputs", "1",
            "--num_steps", str(num_steps),
            "--temperature", str(temperature)
        ]
        
        if primer_path:
            cmd.extend(["--primer_midi", primer_path])
        
        try:
            # Run the generation command
            print(f"Running command: {' '.join(cmd)}")
            process = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True, 
                check=True
            )
            
            # Find the generated file - it will have a timestamp in the name
            generated_files = [f for f in os.listdir(temp_dir) if f.endswith('.mid') and f != "primer.mid"]
            
            if not generated_files:
                return {"error": "No output files were generated", "details": process.stdout + "\n" + process.stderr}
            
            # Use the first generated file
            output_file = os.path.join(temp_dir, generated_files[0])
            
            # Return the generated MIDI file
            return FileResponse(
                output_file, 
                media_type="audio/midi",
                filename="music_transformer_generated.mid"
            )
            
        except subprocess.CalledProcessError as e:
            return {
                "error": "Generation failed", 
                "stdout": e.stdout, 
                "stderr": e.stderr
            }
        except Exception as e:
            return {"error": str(e)}

@app.get("/download_checkpoints")
async def download_checkpoints():
    """
    Download the pretrained Music Transformer checkpoints.
    This might take a while as the model files are large.
    """
    try:
        # Run the download script
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        
        # Use direct requests to download instead of subprocess
        checkpoint_url = "https://storage.googleapis.com/magentadata/models/music_transformer/checkpoints.tar"
        print(f"Downloading from {checkpoint_url}")
        
        response = requests.get(checkpoint_url, stream=True)
        if response.status_code == 200:
            tar_path = os.path.join(CHECKPOINT_DIR, "checkpoints.tar")
            with open(tar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the tarball
            subprocess.run(["tar", "-xf", tar_path, "-C", CHECKPOINT_DIR], check=True)
            return {"status": "success", "message": "Model checkpoints downloaded successfully"}
        else:
            return {"status": "error", "message": f"Failed to download: HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/list_models")
async def list_models():
    """
    List available Music Transformer model checkpoints.
    """
    if not os.path.exists(CHECKPOINT_DIR):
        return {"status": "error", "message": "Checkpoint directory not found"}
        
    models = []
    try:
        for root, dirs, files in os.walk(CHECKPOINT_DIR):
            # Look for checkpoint files
            if any(f.endswith('.index') for f in files):
                checkpoint_name = os.path.basename(root)
                checkpoint_files = [f for f in files if '.data' in f or '.index' in f or '.meta' in f]
                models.append({
                    "name": checkpoint_name,
                    "path": root,
                    "files": checkpoint_files
                })
        
        return {
            "status": "success", 
            "model_count": len(models),
            "models": models
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
