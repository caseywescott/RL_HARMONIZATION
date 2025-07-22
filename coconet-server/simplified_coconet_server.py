import os
import io
import tempfile
import numpy as np
import tensorflow.compat.v1 as tf
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from typing import Optional
import random

# Disable eager execution
tf.compat.v1.disable_eager_execution()

app = FastAPI(title="Simplified Coconet Harmonization Server", version="1.0")

COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
harmonizer = None

class SimplifiedCoconetHarmonizer:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.session = None
        self.graph = None
        self.load_model()
    
    def load_model(self):
        """Load the Coconet model with simplified approach"""
        try:
            print("🔧 Loading Coconet model (simplified approach)...")
            
            # Create a new graph and session
            self.graph = tf.Graph()
            config = tf.compat.v1.ConfigProto()
            config.gpu_options.allow_growth = True
            config.log_device_placement = False
            self.session = tf.compat.v1.Session(graph=self.graph, config=config)
            
            # Load the meta graph
            meta_path = os.path.join(self.model_dir, "best_model.ckpt.meta")
            checkpoint_path = os.path.join(self.model_dir, "best_model.ckpt")
            
            print(f"   Loading meta graph from: {meta_path}")
            print(f"   Loading checkpoint from: {checkpoint_path}")
            
            # Import the meta graph
            with self.graph.as_default():
                saver = tf.compat.v1.train.import_meta_graph(meta_path)
                saver.restore(self.session, checkpoint_path)
            
            print(f"✅ Model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def midi_to_pianoroll(self, midi_file_path):
        """Convert MIDI to pianoroll format"""
        try:
            print(f"🎵 Converting MIDI to pianoroll...")
            
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
            
            print(f"   Found {len(melody_track.notes)} notes in melody")
            
            # Create pianoroll with proper Coconet format
            # Coconet expects: (batch, time, pitch, instruments)
            time_steps = 32  # Fixed length for now
            num_pitches = 46  # Coconet pitch range (21-66)
            num_instruments = 4  # SATB
            
            pianoroll = np.zeros((1, time_steps, num_pitches, num_instruments), dtype=np.float32)
            
            # Fill melody into first instrument (Soprano)
            for note in melody_track.notes:
                start_time = int(note.start * 4)  # 16th note quantization
                end_time = int(note.end * 4)
                pitch_idx = note.pitch - 21  # Coconet pitch offset
                
                if 0 <= pitch_idx < num_pitches and start_time < time_steps:
                    for t in range(start_time, min(end_time, time_steps)):
                        pianoroll[0, t, pitch_idx, 0] = 1.0
            
            print(f"   Pianoroll shape: {pianoroll.shape}")
            print(f"   Melody notes placed: {np.sum(pianoroll[:, :, :, 0])}")
            
            return pianoroll
            
        except Exception as e:
            print(f"❌ Error converting MIDI to pianoroll: {e}")
            raise
    
    def create_harmonization_mask(self, pianoroll_shape):
        """Create mask for harmonization (keep melody, mask harmony)"""
        masks = np.zeros(pianoroll_shape, dtype=np.float32)
        masks[:, :, :, 1:] = 1.0  # Mask Alto, Tenor, Bass
        return masks
    
    def gibbs_sampling(self, pianorolls, masks, temperature=0.99, num_steps=10):
        """Perform Gibbs sampling for harmonization"""
        try:
            print(f"🎼 Running Gibbs sampling...")
            print(f"   Temperature: {temperature}")
            print(f"   Steps: {num_steps}")
            
            current_pianorolls = pianorolls.copy()
            
            # Get input and output tensors from the graph
            operations = self.graph.get_operations()
            
            # Find input tensors (usually named with 'Placeholder')
            input_tensors = []
            output_tensors = []
            
            for op in operations:
                if 'Placeholder' in op.name:
                    input_tensors.append(self.graph.get_tensor_by_name(op.name + ':0'))
                elif 'Softmax' in op.name or 'output' in op.name.lower():
                    output_tensors.append(self.graph.get_tensor_by_name(op.name + ':0'))
            
            print(f"   Found {len(input_tensors)} input tensors")
            print(f"   Found {len(output_tensors)} output tensors")
            
            if not input_tensors or not output_tensors:
                raise ValueError("Could not find input or output tensors in the model")
            
            # Use the first input and output tensors
            input_tensor = input_tensors[0]
            output_tensor = output_tensors[0]
            
            for step in range(num_steps):
                print(f"   Step {step + 1}/{num_steps}")
                
                # Run model prediction
                feed_dict = {input_tensor: current_pianorolls}
                predictions = self.session.run(output_tensor, feed_dict=feed_dict)
                
                # Sample from predictions for masked areas
                for b in range(pianorolls.shape[0]):  # batch
                    for t in range(pianorolls.shape[1]):  # time
                        for p in range(pianorolls.shape[2]):  # pitch
                            for i in range(pianorolls.shape[3]):  # instrument
                                if masks[b, t, p, i] > 0.5:  # If masked
                                    # Sample from prediction
                                    prob = predictions[b, t, p, i] if predictions.shape == current_pianorolls.shape else predictions[b, t, p]
                                    if np.random.random() < prob * temperature:
                                        current_pianorolls[b, t, p, i] = 1.0
                                    else:
                                        current_pianorolls[b, t, p, i] = 0.0
                
                # Apply mask to keep melody unchanged
                current_pianorolls = current_pianorolls * (1 - masks)
                current_pianorolls += pianorolls * masks  # Restore original melody
            
            print(f"   Gibbs sampling completed")
            return current_pianorolls
            
        except Exception as e:
            print(f"❌ Error during Gibbs sampling: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def harmonize(self, pianoroll, temperature=0.99):
        """Harmonize using simplified Coconet Gibbs sampling"""
        try:
            print(f"🎼 Running simplified Coconet harmonization...")
            
            # Create harmonization mask
            masks = self.create_harmonization_mask(pianoroll.shape)
            
            print(f"   Input shape: {pianoroll.shape}")
            print(f"   Mask shape: {masks.shape}")
            print(f"   Melody preserved, harmony masked")
            
            # Apply mask to input (keep melody, zero harmony)
            masked_input = pianoroll * (1 - masks)
            
            # Run Gibbs sampling
            harmonized = self.gibbs_sampling(masked_input, masks, temperature)
            
            return harmonized
            
        except Exception as e:
            print(f"❌ Error during harmonization: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def pianoroll_to_midi(self, pianoroll, output_path):
        """Convert pianoroll back to MIDI with proper voice ranges"""
        try:
            print(f"🎵 Converting to MIDI...")
            
            midi = pretty_midi.PrettyMIDI()
            
            # Create instruments with proper voice ranges
            instrument_names = ["Soprano", "Alto", "Tenor", "Bass"]
            instruments = []
            
            for i, name in enumerate(instrument_names):
                instrument = pretty_midi.Instrument(program=0, name=name)
                instruments.append(instrument)
                midi.instruments.append(instrument)
            
            # Convert pianoroll to notes with proper voice leading
            total_notes = 0
            for i in range(pianoroll.shape[3]):  # instruments
                instrument_notes = 0
                current_notes = {}  # Track active notes
                
                for t in range(pianoroll.shape[1]):  # time
                    # Find notes that start at this time
                    for p in range(pianoroll.shape[2]):  # pitch
                        if pianoroll[0, t, p, i] > 0.5:  # Note is on
                            pitch = p + 21  # Coconet pitch offset
                            
                            # Check if note is already active
                            if pitch not in current_notes:
                                # Start new note
                                note = pretty_midi.Note(
                                    velocity=100,
                                    pitch=pitch,
                                    start=t * 0.25,  # 16th note = 0.25 seconds
                                    end=(t + 1) * 0.25
                                )
                                instruments[i].notes.append(note)
                                current_notes[pitch] = note
                                instrument_notes += 1
                            else:
                                # Extend existing note
                                current_notes[pitch].end = (t + 1) * 0.25
                    
                    # Remove notes that end at this time
                    pitches_to_remove = []
                    for pitch, note in current_notes.items():
                        if pianoroll[0, t, pitch - 21, i] <= 0.5:  # Note is off
                            pitches_to_remove.append(pitch)
                    
                    for pitch in pitches_to_remove:
                        del current_notes[pitch]
                
                print(f"   {instrument_names[i]}: {instrument_notes} notes")
                total_notes += instrument_notes
            
            # Save MIDI
            midi.write(output_path)
            print(f"✅ MIDI saved to {output_path} with {total_notes} total notes")
            
        except Exception as e:
            print(f"❌ Error converting to MIDI: {e}")
            raise

# Initialize harmonizer
harmonizer = None

@app.on_event("startup")
async def startup_event():
    global harmonizer
    try:
        harmonizer = SimplifiedCoconetHarmonizer(COCONET_MODEL_DIR)
        print("✅ Simplified Coconet harmonizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize harmonizer: {e}")
        import traceback
        traceback.print_exc()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Simplified Coconet Harmonization Server</title>
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
                <h1>🎼 Simplified Coconet Harmonization Server</h1>
                <p>This server uses a simplified approach to load the Coconet model and perform Bach-style harmonization.</p>
                
                <div class="endpoint">
                    <div class="method">GET</div>
                    <div class="url">/status</div>
                    <div class="description">Check server status and model availability</div>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST</div>
                    <div class="url">/harmonize</div>
                    <div class="description">Harmonize a MIDI melody using simplified Coconet</div>
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
    model_files = []
    if os.path.exists(COCONET_MODEL_DIR):
        model_files = os.listdir(COCONET_MODEL_DIR)
    
    return {
        "server_status": "running",
        "model_available": len(model_files) > 0,
        "harmonizer_initialized": harmonizer is not None,
        "model_path": COCONET_MODEL_DIR,
        "model_files": model_files,
        "harmonization_method": "Simplified Coconet Gibbs Sampling"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """Harmonize a MIDI melody using simplified Coconet"""
    global harmonizer
    
    if harmonizer is None:
        return {"error": "Harmonizer not initialized"}
    
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Convert MIDI to pianoroll
            pianoroll = harmonizer.midi_to_pianoroll(temp_file_path)
            
            # Harmonize using Gibbs sampling
            harmonized_pianoroll = harmonizer.harmonize(pianoroll, temperature)
            
            # Convert back to MIDI
            output_path = temp_file_path.replace(".mid", "_harmonized.mid")
            harmonizer.pianoroll_to_midi(harmonized_pianoroll, output_path)
            
            # Return the harmonized file
            return FileResponse(
                output_path,
                media_type="audio/midi",
                filename=f"simplified_coconet_harmonized_{file.filename}"
            )
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 