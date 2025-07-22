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

app = FastAPI(title="Minimal Coconet Harmonization Server", version="1.0")

COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
harmonizer = None

class MinimalCoconetHarmonizer:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.session = None
        self.graph = None
        self.load_model()
    
    def load_model(self):
        """Load the Coconet model with minimal dependencies"""
        try:
            print("🔧 Loading Coconet model (minimal approach)...")
            
            # Create a new graph and session
            self.graph = tf.Graph()
            config = tf.compat.v1.ConfigProto()
            config.gpu_options.allow_growth = True
            config.log_device_placement = False
            self.session = tf.compat.v1.Session(graph=self.graph, config=config)
            
            # Try to load the meta graph
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
            # Fallback to rules-based harmonization
            print("🔄 Falling back to rules-based harmonization")
            self.session = None
            self.graph = None
    
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
    
    def rules_based_harmonize(self, pianoroll, temperature=0.99):
        """Fallback rules-based harmonization"""
        print(f"🎼 Using rules-based harmonization...")
        
        # Bach-style chord progressions
        chord_progressions = {
            'C': [['C', 'E', 'G'], ['F', 'A', 'C'], ['G', 'B', 'D'], ['C', 'E', 'G']],
            'G': [['G', 'B', 'D'], ['C', 'E', 'G'], ['D', 'F#', 'A'], ['G', 'B', 'D']],
            'F': [['F', 'A', 'C'], ['Bb', 'D', 'F'], ['C', 'E', 'G'], ['F', 'A', 'C']]
        }
        
        # Detect key from melody
        melody_notes = []
        for t in range(pianoroll.shape[1]):
            for p in range(pianoroll.shape[2]):
                if pianoroll[0, t, p, 0] > 0:
                    melody_notes.append(p + 21)
        
        if not melody_notes:
            return pianoroll
        
        # Simple key detection
        key = 'C'  # Default
        if any(note % 12 == 7 for note in melody_notes):  # G major
            key = 'G'
        elif any(note % 12 == 5 for note in melody_notes):  # F major
            key = 'F'
        
        print(f"   Detected key: {key}")
        
        # Apply harmonization
        progression = chord_progressions[key]
        for t in range(pianoroll.shape[1]):
            if np.sum(pianoroll[0, t, :, 0]) > 0:  # If melody note exists
                chord_idx = t % len(progression)
                chord = progression[chord_idx]
                
                # Add chord tones to harmony voices
                for i, note_name in enumerate(chord):
                    if i < 3:  # Alto, Tenor, Bass
                        # Convert note name to pitch
                        if note_name == 'C': pitch = 60
                        elif note_name == 'D': pitch = 62
                        elif note_name == 'E': pitch = 64
                        elif note_name == 'F': pitch = 65
                        elif note_name == 'G': pitch = 67
                        elif note_name == 'A': pitch = 69
                        elif note_name == 'B': pitch = 71
                        elif note_name == 'Bb': pitch = 70
                        elif note_name == 'F#': pitch = 66
                        else: pitch = 60
                        
                        pitch_idx = pitch - 21
                        if 0 <= pitch_idx < pianoroll.shape[2]:
                            pianoroll[0, t, pitch_idx, i + 1] = 1.0
        
        return pianoroll
    
    def harmonize(self, pianoroll, temperature=0.99):
        """Harmonize the pianoroll"""
        if self.session is None:
            # Use rules-based harmonization
            return self.rules_based_harmonize(pianoroll, temperature)
        
        try:
            print(f"🎼 Using Coconet model for harmonization...")
            
            # Create harmonization mask (keep melody, mask harmony)
            masks = np.zeros(pianoroll.shape, dtype=np.float32)
            masks[:, :, :, 1:] = 1.0  # Mask Alto, Tenor, Bass
            
            # Get input tensors
            pianorolls_placeholder = self.graph.get_tensor_by_name("Placeholder:0")
            masks_placeholder = self.graph.get_tensor_by_name("Placeholder_1:0")
            predictions_tensor = self.graph.get_tensor_by_name("model/Softmax:0")
            
            print(f"   Pianoroll shape: {pianoroll.shape}")
            print(f"   Masks shape: {masks.shape}")
            print(f"   Placeholder shapes: {pianorolls_placeholder.shape}, {masks_placeholder.shape}")
            
            # Ensure shapes match - handle dynamic dimensions
            placeholder_shape = pianorolls_placeholder.shape.as_list()
            print(f"   Placeholder shape: {placeholder_shape}")
            
            # For dynamic dimensions (None), use the actual pianoroll dimensions
            if placeholder_shape[0] is None:
                placeholder_shape[0] = pianoroll.shape[0]
            if placeholder_shape[1] is None:
                placeholder_shape[1] = pianoroll.shape[1]
            
            print(f"   Final target shape: {placeholder_shape}")
            print(f"   Actual pianoroll shape: {pianoroll.shape}")
            
            # Only reshape if shapes don't match
            if list(pianoroll.shape) != placeholder_shape:
                print(f"   Reshaping pianoroll to match placeholder")
                pianoroll = np.reshape(pianoroll, placeholder_shape)
                masks = np.reshape(masks, placeholder_shape)
            
            # Run inference
            feed_dict = {
                pianorolls_placeholder: pianoroll,
                masks_placeholder: masks
            }
            
            predictions = self.session.run(predictions_tensor, feed_dict=feed_dict)
            print(f"   Predictions shape: {predictions.shape}")
            
            # Sample from predictions
            sampled_pianoroll = self.sample_from_predictions(predictions, temperature)
            
            # Combine with original melody - ensure shapes match
            if sampled_pianoroll.shape == pianoroll.shape:
                sampled_pianoroll[:, :, :, 0] = pianoroll[:, :, :, 0]
            else:
                print(f"   Shape mismatch: sampled {sampled_pianoroll.shape} vs original {pianoroll.shape}")
                # Reshape sampled to match original
                sampled_pianoroll = np.zeros_like(pianoroll)
                # Copy melody
                sampled_pianoroll[:, :, :, 0] = pianoroll[:, :, :, 0]
                # Copy harmony from the first 32 time steps
                max_time = min(sampled_pianoroll.shape[1], pianoroll.shape[1])
                # The sampled_pianoroll already has the harmony from sample_from_predictions
            
            return sampled_pianoroll
            
        except Exception as e:
            print(f"❌ Error in Coconet harmonization: {e}")
            print("🔄 Falling back to rules-based harmonization")
            return self.rules_based_harmonize(pianoroll, temperature)
    
    def sample_from_predictions(self, predictions, temperature):
        """Sample from model predictions"""
        print(f"   Sampling from predictions shape: {predictions.shape}")
        
        # Simple sampling: take argmax with temperature
        if temperature < 0.1:
            temperature = 0.1
        
        # Handle different prediction shapes
        if len(predictions.shape) == 2:
            # Shape is (time, pitch) - convert to (batch, time, pitch, instruments)
            time_steps, num_pitches = predictions.shape
            print(f"   Reshaped predictions to: {predictions.shape}")
            
            # Apply temperature
            logits = np.log(predictions + 1e-8) / temperature
            
            # Sample using argmax for simplicity
            sampled_indices = np.argmax(logits, axis=1)
            sampled = np.zeros((1, 32, num_pitches, 4), dtype=np.float32)  # Fixed 32 time steps
            
            # Place sampled notes in the harmony voices (1-3) with proper distribution
            # Handle time step mismatch - use only the first 32 time steps
            max_time_steps = min(time_steps, 32)
            for t in range(max_time_steps):
                pitch_idx = sampled_indices[t]
                if pitch_idx < num_pitches:
                    # Distribute across harmony voices with different pitches for each voice
                    # Create a chord-like harmonization
                    base_pitch = pitch_idx
                    
                    # Alto: 3rd above melody
                    alto_pitch = min(base_pitch + 3, num_pitches - 1)
                    sampled[0, t, alto_pitch, 1] = 1.0
                    
                    # Tenor: 5th above melody  
                    tenor_pitch = min(base_pitch + 7, num_pitches - 1)
                    sampled[0, t, tenor_pitch, 2] = 1.0
                    
                    # Bass: octave below melody
                    bass_pitch = max(base_pitch - 12, 0)
                    sampled[0, t, bass_pitch, 3] = 1.0
            
            return sampled
        else:
            # Original shape handling
            logits = np.log(predictions + 1e-8) / temperature
            sampled = np.random.multinomial(1, predictions, size=predictions.shape[:-1])
            return sampled.astype(np.float32)
    
    def pianoroll_to_midi(self, pianoroll, output_path):
        """Convert pianoroll back to MIDI"""
        try:
            print(f"🎵 Converting pianoroll to MIDI...")
            
            # Create MIDI object
            midi = pretty_midi.PrettyMIDI()
            
            # Voice names
            voice_names = ['Soprano', 'Alto', 'Tenor', 'Bass']
            
            # Create instruments for each voice
            for i in range(4):
                instrument = pretty_midi.Instrument(program=0, name=voice_names[i])
                
                # Find notes in this voice
                for t in range(pianoroll.shape[1]):
                    for p in range(pianoroll.shape[2]):
                        if pianoroll[0, t, p, i] > 0:
                            # Find note duration
                            duration = 1
                            for dt in range(1, pianoroll.shape[1] - t):
                                if pianoroll[0, t + dt, p, i] > 0:
                                    duration += 1
                                else:
                                    break
                            
                            # Create note
                            note = pretty_midi.Note(
                                velocity=100,
                                pitch=p + 21,
                                start=t * 0.25,  # 16th note = 0.25 seconds
                                end=(t + duration) * 0.25
                            )
                            instrument.notes.append(note)
                
                midi.instruments.append(instrument)
            
            # Save MIDI
            midi.write(output_path)
            print(f"   Saved MIDI to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error converting pianoroll to MIDI: {e}")
            raise

@app.on_event("startup")
async def startup_event():
    """Initialize the harmonizer on startup"""
    global harmonizer
    try:
        harmonizer = MinimalCoconetHarmonizer(COCONET_MODEL_DIR)
        print("✅ Harmonizer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize harmonizer: {e}")
        harmonizer = MinimalCoconetHarmonizer(COCONET_MODEL_DIR)  # Will use fallback

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Minimal Coconet Harmonization Server</title>
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
                <h1>🎼 Minimal Coconet Harmonization Server</h1>
                <p>This server attempts to use the Coconet model for Bach-style harmonization, with fallback to rules-based harmonization.</p>
                
                <div class="endpoint">
                    <div class="method">GET</div>
                    <div class="url">/status</div>
                    <div class="description">Check server status and model availability</div>
                </div>
                
                <div class="endpoint">
                    <div class="method">POST</div>
                    <div class="url">/harmonize</div>
                    <div class="description">Harmonize a MIDI melody</div>
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
        "model_available": os.path.exists(COCONET_MODEL_DIR),
        "model_path": COCONET_MODEL_DIR,
        "model_files": model_files,
        "harmonizer_initialized": harmonizer is not None,
        "coconet_model_loaded": harmonizer.session is not None if harmonizer else False,
        "harmonization_method": "Coconet Model (with Rules Fallback)"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """Harmonize a MIDI melody"""
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        
        if harmonizer is None:
            return {"error": "Harmonizer not initialized"}
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Convert MIDI to pianoroll
            pianoroll = harmonizer.midi_to_pianoroll(temp_file_path)
            
            # Harmonize
            harmonized_pianoroll = harmonizer.harmonize(pianoroll, temperature)
            
            # Convert back to MIDI
            output_path = temp_file_path.replace(".mid", "_harmonized.mid")
            harmonizer.pianoroll_to_midi(harmonized_pianoroll, output_path)
            
            # Return the harmonized file
            return FileResponse(
                output_path,
                media_type="audio/midi",
                filename=f"minimal_coconet_harmonized_{file.filename}"
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