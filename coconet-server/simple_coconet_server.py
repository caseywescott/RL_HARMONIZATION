#!/usr/bin/env python3
"""
Simple Coconet Harmonization Server

This server directly uses the Coconet model for harmonization
without requiring the full Magenta package.
"""

import os
import io
import tempfile
import numpy as np
import tensorflow.compat.v1 as tf
from tensorflow.python.lib.io import file_io
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from typing import Optional

app = FastAPI(title="Simple Coconet Harmonization API")

# Model configuration
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"

class SimpleCoconetHarmonizer:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.session = None
        self.graph = None
        self.input_placeholder = None
        self.output_tensor = None
        self.load_model()
    
    def load_model(self):
        """Load the Coconet model"""
        try:
            # Load the graph
            graph_path = os.path.join(self.model_dir, "graph.pbtxt")
            if not os.path.exists(graph_path):
                raise FileNotFoundError(f"Graph file not found: {graph_path}")
            
            # Create a new graph
            self.graph = tf.Graph()
            with self.graph.as_default():
                # Load the graph definition
                with open(graph_path, 'r') as f:
                    graph_def = tf.compat.v1.GraphDef()
                    tf.io.gfile.GFile(graph_path, 'r').read()
                    tf.compat.v1.text_format.Merge(f.read(), graph_def)
                
                # Import the graph
                tf.import_graph_def(graph_def, name='')
                
                # Create session
                self.session = tf.compat.v1.Session(graph=self.graph)
                
                # Load the checkpoint
                checkpoint_path = os.path.join(self.model_dir, "best_model.ckpt")
                saver = tf.compat.v1.train.Saver()
                saver.restore(self.session, checkpoint_path)
                
                # Find input and output tensors
                self.input_placeholder = self.graph.get_tensor_by_name("Placeholder:0")
                self.output_tensor = self.graph.get_tensor_by_name("model/Softmax:0")
                
                print(f"✅ Model loaded successfully")
                print(f"   Input shape: {self.input_placeholder.shape}")
                print(f"   Output shape: {self.output_tensor.shape}")
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def midi_to_pianoroll(self, midi_file_path):
        """Convert MIDI to pianoroll"""
        try:
            # Load MIDI
            midi = pretty_midi.PrettyMIDI(midi_file_path)
            
            # Get the melody track (first track with notes)
            melody_track = None
            for instrument in midi.instruments:
                if len(instrument.notes) > 0:
                    melody_track = instrument
                    break
            
            if melody_track is None:
                raise ValueError("No melody found in MIDI file")
            
            # Create pianoroll
            # Coconet expects: (batch, time, pitch, instruments)
            # For harmonization: 4 instruments (melody + 3 harmony parts)
            time_steps = 32  # Fixed length for now
            num_pitches = 46  # Coconet pitch range
            num_instruments = 4
            
            pianoroll = np.zeros((1, time_steps, num_pitches, num_instruments), dtype=np.float32)
            
            # Fill melody into first instrument
            for note in melody_track.notes:
                start_time = int(note.start * 4)  # 16th note quantization
                end_time = int(note.end * 4)
                pitch_idx = note.pitch - 21  # Coconet pitch offset
                
                if 0 <= pitch_idx < num_pitches and start_time < time_steps:
                    for t in range(start_time, min(end_time, time_steps)):
                        pianoroll[0, t, pitch_idx, 0] = 1.0
            
            return pianoroll
            
        except Exception as e:
            print(f"❌ Error converting MIDI to pianoroll: {e}")
            raise
    
    def harmonize(self, pianoroll, temperature=0.99):
        """Harmonize using Coconet"""
        try:
            # Create mask: keep melody (instrument 0), mask harmony (instruments 1-3)
            mask = np.ones_like(pianoroll)
            mask[:, :, :, 1:] = 0  # Mask harmony parts
            
            # Apply mask to input
            masked_input = pianoroll * mask
            
            # Run inference
            feed_dict = {
                self.input_placeholder: masked_input
            }
            
            output = self.session.run(self.output_tensor, feed_dict=feed_dict)
            
            # Sample from output probabilities
            harmonized = self.sample_from_output(output, pianoroll, mask, temperature)
            
            return harmonized
            
        except Exception as e:
            print(f"❌ Error during harmonization: {e}")
            raise
    
    def sample_from_output(self, output, original_pianoroll, mask, temperature):
        """Sample harmonized notes from model output"""
        try:
            # output shape: (batch, time, pitch, instruments)
            harmonized = original_pianoroll.copy()
            
            # Apply temperature
            logits = np.log(output + 1e-8) / temperature
            
            # Sample for each masked position
            for t in range(output.shape[1]):  # time
                for p in range(output.shape[2]):  # pitch
                    for i in range(1, output.shape[3]):  # instruments (skip melody)
                        if mask[0, t, p, i] == 0:  # If masked
                            probs = output[0, t, p, i]
                            if np.sum(probs) > 0:
                                # Sample note
                                if np.random.random() < probs:
                                    harmonized[0, t, p, i] = 1.0
            
            return harmonized
            
        except Exception as e:
            print(f"❌ Error sampling from output: {e}")
            raise
    
    def pianoroll_to_midi(self, pianoroll, output_path):
        """Convert pianoroll back to MIDI"""
        try:
            midi = pretty_midi.PrettyMIDI()
            
            # Create instruments
            instrument_names = ["Melody", "Alto", "Tenor", "Bass"]
            instruments = []
            
            for i, name in enumerate(instrument_names):
                instrument = pretty_midi.Instrument(program=0, name=name)
                instruments.append(instrument)
                midi.instruments.append(instrument)
            
            # Convert pianoroll to notes
            for i in range(pianoroll.shape[3]):  # instruments
                for t in range(pianoroll.shape[1]):  # time
                    for p in range(pianoroll.shape[2]):  # pitch
                        if pianoroll[0, t, p, i] > 0.5:  # Note is on
                            # Find note duration
                            duration = 1
                            for dt in range(1, pianoroll.shape[1] - t):
                                if t + dt < pianoroll.shape[1] and pianoroll[0, t + dt, p, i] > 0.5:
                                    duration += 1
                                else:
                                    break
                            
                            # Create note
                            note = pretty_midi.Note(
                                velocity=100,
                                pitch=p + 21,  # Coconet pitch offset
                                start=t * 0.25,  # 16th note = 0.25 seconds
                                end=(t + duration) * 0.25
                            )
                            instruments[i].notes.append(note)
            
            # Save MIDI
            midi.write(output_path)
            print(f"✅ MIDI saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Error converting to MIDI: {e}")
            raise

# Initialize harmonizer
harmonizer = None

@app.on_event("startup")
async def startup_event():
    global harmonizer
    try:
        harmonizer = SimpleCoconetHarmonizer(COCONET_MODEL_DIR)
        print("✅ Coconet harmonizer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize harmonizer: {e}")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Simple Coconet Harmonization API</title>
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
            <h1>🎵 Simple Coconet Harmonization API</h1>
            <p>This API uses a <strong>simplified Coconet implementation</strong> for harmonization.</p>
            
            <h2>Key Features:</h2>
            <ul>
                <li><span class="success">✅ Direct TensorFlow model usage</span></li>
                <li><span class="success">✅ No full Magenta dependency</span></li>
                <li><span class="success">✅ 4-part harmonization (SATB)</span></li>
                <li><span class="success">✅ Melody preservation with harmony generation</span></li>
            </ul>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>GET /status</strong> - Check model status</li>
                <li><strong>POST /harmonize</strong> - Harmonize using simplified Coconet</li>
            </ul>
            
            <p>Check out the <a href="/docs">API documentation</a> for more details.</p>
        </body>
    </html>
    """

@app.get("/status")
async def get_status():
    """Get the status of the harmonization model"""
    global harmonizer
    
    model_files = []
    if os.path.exists(COCONET_MODEL_DIR):
        model_files = os.listdir(COCONET_MODEL_DIR)
    
    return {
        "model_available": len(model_files) > 0,
        "harmonizer_initialized": harmonizer is not None,
        "model_path": COCONET_MODEL_DIR,
        "model_files": model_files,
        "harmonization_method": "Simplified Coconet Direct Model"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """
    Harmonize a melody using simplified Coconet
    
    This endpoint:
    1. Takes a melody from the input MIDI file
    2. Converts it to pianoroll format
    3. Uses Coconet model to generate harmony parts
    4. Returns a harmonized MIDI file
    
    - **file**: MIDI file containing the melody to harmonize
    - **temperature**: Controls randomness (lower = more predictable, higher = more creative)
    """
    global harmonizer
    
    if harmonizer is None:
        return {"error": "Harmonizer not initialized"}
    
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        
        # Read the uploaded file
        midi_data = await file.read()
        print(f"   File size: {len(midi_data)} bytes")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save input MIDI
            input_midi_path = os.path.join(temp_dir, "input.mid")
            with open(input_midi_path, "wb") as f:
                f.write(midi_data)
            
            print("🤖 Running simplified Coconet harmonization...")
            
            # Convert MIDI to pianoroll
            pianoroll = harmonizer.midi_to_pianoroll(input_midi_path)
            print(f"   Pianoroll shape: {pianoroll.shape}")
            
            # Harmonize
            harmonized_pianoroll = harmonizer.harmonize(pianoroll, temperature)
            print(f"   Harmonized pianoroll shape: {harmonized_pianoroll.shape}")
            
            # Convert back to MIDI
            output_midi_path = os.path.join(temp_dir, "output.mid")
            harmonizer.pianoroll_to_midi(harmonized_pianoroll, output_midi_path)
            
            # Read the generated MIDI
            with open(output_midi_path, 'rb') as f:
                harmonized_data = f.read()
            
            # Save to a temporary file for response
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_file:
                tmp_file.write(harmonized_data)
                tmp_file_path = tmp_file.name
            
            print(f"✅ Harmonization completed")
            
            # Return the harmonized file
            return FileResponse(
                tmp_file_path,
                media_type="audio/midi",
                filename=f"simple_coconet_harmonization_{temperature}.mid"
            )
            
    except Exception as e:
        print(f"❌ Error in harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 