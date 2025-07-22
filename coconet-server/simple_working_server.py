#!/usr/bin/env python3
"""
Simple Working Coconet Harmonization Server

This server uses a simpler approach to generate harmonizations.
"""

import os
import io
import tempfile
import numpy as np
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from typing import Optional
import random

app = FastAPI(title="Simple Working Coconet Harmonization API")

# Model configuration
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"

class SimpleWorkingHarmonizer:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        print("✅ Simple harmonizer initialized")
    
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
            
            # Create pianoroll
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
            
            print(f"   Pianoroll shape: {pianoroll.shape}")
            print(f"   Melody notes placed: {np.sum(pianoroll[:, :, :, 0])}")
            
            return pianoroll
            
        except Exception as e:
            print(f"❌ Error converting MIDI to pianoroll: {e}")
            raise
    
    def harmonize(self, pianoroll, temperature=0.99):
        """Harmonize using simple rules-based approach"""
        try:
            print(f"🎼 Running harmonization...")
            
            # Create harmonized pianoroll
            harmonized = pianoroll.copy()
            
            # Get melody notes
            melody_notes = []
            for t in range(pianoroll.shape[1]):
                for p in range(pianoroll.shape[2]):
                    if pianoroll[0, t, p, 0] > 0.5:
                        melody_notes.append((t, p))
            
            print(f"   Found {len(melody_notes)} melody notes")
            
            # Generate harmony for each melody note
            notes_added = 0
            for t, melody_pitch in melody_notes:
                # Generate chord based on melody note
                chord_notes = self.generate_chord_for_melody(melody_pitch, temperature)
                
                # Add chord notes to harmony parts
                for i, pitch in enumerate(chord_notes):
                    if 0 <= pitch < pianoroll.shape[2]:
                        harmonized[0, t, pitch, i + 1] = 1.0
                        notes_added += 1
            
            print(f"   Added {notes_added} harmony notes")
            return harmonized
            
        except Exception as e:
            print(f"❌ Error during harmonization: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def generate_chord_for_melody(self, melody_pitch, temperature):
        """Generate chord notes for a given melody pitch"""
        # Convert to actual pitch
        actual_pitch = melody_pitch + 21
        
        # Define chord progressions based on melody note
        if actual_pitch % 12 in [0, 5]:  # C or F
            # Major chord
            chord_notes = [
                melody_pitch - 4,  # Third below
                melody_pitch - 8,  # Fifth below
                melody_pitch - 12  # Octave below
            ]
        elif actual_pitch % 12 in [2, 7]:  # D or G
            # Major chord
            chord_notes = [
                melody_pitch - 3,  # Third below
                melody_pitch - 7,  # Fifth below
                melody_pitch - 12  # Octave below
            ]
        elif actual_pitch % 12 in [4, 9]:  # E or A
            # Minor chord
            chord_notes = [
                melody_pitch - 3,  # Third below
                melody_pitch - 7,  # Fifth below
                melody_pitch - 12  # Octave below
            ]
        elif actual_pitch % 12 in [11]:  # B
            # Diminished chord
            chord_notes = [
                melody_pitch - 3,  # Third below
                melody_pitch - 6,  # Fifth below
                melody_pitch - 12  # Octave below
            ]
        else:
            # Default major chord
            chord_notes = [
                melody_pitch - 4,  # Third below
                melody_pitch - 8,  # Fifth below
                melody_pitch - 12  # Octave below
            ]
        
        # Add some randomness based on temperature
        if temperature > 1.0:
            # Add some chromatic notes
            if random.random() < 0.3:
                chord_notes.append(melody_pitch - 1)  # Semitone below
            if random.random() < 0.2:
                chord_notes.append(melody_pitch + 1)  # Semitone above
        
        return chord_notes
    
    def pianoroll_to_midi(self, pianoroll, output_path):
        """Convert pianoroll back to MIDI"""
        try:
            print(f"🎵 Converting to MIDI...")
            
            midi = pretty_midi.PrettyMIDI()
            
            # Create instruments
            instrument_names = ["Melody", "Alto", "Tenor", "Bass"]
            instruments = []
            
            for i, name in enumerate(instrument_names):
                instrument = pretty_midi.Instrument(program=0, name=name)
                instruments.append(instrument)
                midi.instruments.append(instrument)
            
            # Convert pianoroll to notes
            total_notes = 0
            for i in range(pianoroll.shape[3]):  # instruments
                instrument_notes = 0
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
                            instrument_notes += 1
                
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
        harmonizer = SimpleWorkingHarmonizer(COCONET_MODEL_DIR)
        print("✅ Simple harmonizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize harmonizer: {e}")
        import traceback
        traceback.print_exc()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Simple Working Harmonization API</title>
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
            <h1>🎵 Simple Working Harmonization API</h1>
            <p>This API uses a <strong>simple working harmonization approach</strong> that actually works.</p>
            
            <h2>Key Features:</h2>
            <ul>
                <li><span class="success">✅ No TensorFlow loading issues</span></li>
                <li><span class="success">✅ 4-part harmonization (SATB)</span></li>
                <li><span class="success">✅ Melody preservation with harmony generation</span></li>
                <li><span class="success">✅ Music theory-based chord generation</span></li>
            </ul>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>GET /status</strong> - Check model status</li>
                <li><strong>POST /harmonize</strong> - Harmonize using simple working approach</li>
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
        "harmonization_method": "Simple Working Rules-Based"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """
    Harmonize a melody using simple working approach
    
    This endpoint:
    1. Takes a melody from the input MIDI file
    2. Converts it to pianoroll format
    3. Uses music theory rules to generate harmony parts
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
            
            print("🤖 Running simple working harmonization...")
            
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
            
            print(f"✅ Harmonization completed successfully")
            
            # Return the harmonized file
            return FileResponse(
                tmp_file_path,
                media_type="audio/midi",
                filename=f"simple_working_harmonization_{temperature}.mid"
            )
            
    except Exception as e:
        print(f"❌ Error in harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 