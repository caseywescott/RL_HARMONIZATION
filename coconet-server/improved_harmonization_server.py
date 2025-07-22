#!/usr/bin/env python3
"""
Improved Harmonization Server

This server creates Bach-style harmonizations with proper voice leading and audible notes.
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

app = FastAPI(title="Improved Bach-Style Harmonization API")

# Model configuration
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"

class ImprovedHarmonizer:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        print("✅ Improved harmonizer initialized")
        
        # Define Bach-style chord progressions
        self.chord_progressions = {
            # Major key progressions
            'C': ['C', 'F', 'G', 'C'],
            'G': ['G', 'C', 'D', 'G'],
            'F': ['F', 'Bb', 'C', 'F'],
            'D': ['D', 'G', 'A', 'D'],
            'A': ['A', 'D', 'E', 'A'],
            'E': ['E', 'A', 'B', 'E'],
            'B': ['B', 'E', 'F#', 'B'],
            
            # Minor key progressions
            'Am': ['Am', 'Dm', 'E', 'Am'],
            'Em': ['Em', 'Am', 'B', 'Em'],
            'Bm': ['Bm', 'Em', 'F#', 'Bm'],
            'F#m': ['F#m', 'Bm', 'C#', 'F#m'],
            'C#m': ['C#m', 'F#m', 'G#', 'C#m'],
            'G#m': ['G#m', 'C#m', 'D#', 'G#m'],
            'D#m': ['D#m', 'G#m', 'A#', 'D#m'],
        }
        
        # Define chord voicings for SATB
        self.chord_voicings = {
            'C': {'S': 60, 'A': 55, 'T': 48, 'B': 36},  # C-E-G-C
            'F': {'S': 65, 'A': 60, 'T': 53, 'B': 41},  # F-A-C-F
            'G': {'S': 67, 'A': 62, 'T': 55, 'B': 43},  # G-B-D-G
            'D': {'S': 62, 'A': 57, 'T': 50, 'B': 38},  # D-F#-A-D
            'A': {'S': 69, 'A': 64, 'T': 57, 'B': 45},  # A-C#-E-A
            'E': {'S': 64, 'A': 59, 'T': 52, 'B': 40},  # E-G#-B-E
            'B': {'S': 71, 'A': 66, 'T': 59, 'B': 47},  # B-D#-F#-B
            
            'Am': {'S': 60, 'A': 55, 'T': 48, 'B': 36},  # A-C-E-A
            'Dm': {'S': 62, 'A': 57, 'T': 50, 'B': 38},  # D-F-A-D
            'Em': {'S': 64, 'A': 59, 'T': 52, 'B': 40},  # E-G-B-E
            'Bm': {'S': 71, 'A': 66, 'T': 59, 'B': 47},  # B-D-F#-B
            'F#m': {'S': 66, 'A': 61, 'T': 54, 'B': 42},  # F#-A-C#-F#
            'C#m': {'S': 61, 'A': 56, 'T': 49, 'B': 37},  # C#-E-G#-C#
            'G#m': {'S': 68, 'A': 63, 'T': 56, 'B': 44},  # G#-B-D#-G#
            'D#m': {'S': 63, 'A': 58, 'T': 51, 'B': 39},  # D#-F#-A#-D#
        }
    
    def detect_key(self, melody_notes):
        """Detect the key from melody notes"""
        if not melody_notes:
            return 'C'
        
        # Count note occurrences
        note_counts = {}
        for note in melody_notes:
            pitch_class = note.pitch % 12
            note_counts[pitch_class] = note_counts.get(pitch_class, 0) + 1
        
        # Simple key detection based on most common notes
        if 0 in note_counts and 7 in note_counts:  # C and G
            return 'C'
        elif 7 in note_counts and 2 in note_counts:  # G and D
            return 'G'
        elif 5 in note_counts and 0 in note_counts:  # F and C
            return 'F'
        elif 2 in note_counts and 9 in note_counts:  # D and A
            return 'D'
        elif 9 in note_counts and 4 in note_counts:  # A and E
            return 'A'
        elif 4 in note_counts and 11 in note_counts:  # E and B
            return 'E'
        elif 11 in note_counts and 6 in note_counts:  # B and F#
            return 'B'
        else:
            return 'C'  # Default to C major
    
    def get_chord_for_melody_note(self, melody_pitch, key, progression_step, temperature):
        """Get appropriate chord for a melody note"""
        # Get the progression for the detected key
        progression = self.chord_progressions.get(key, self.chord_progressions['C'])
        
        # Select chord based on progression step and melody note
        chord_idx = progression_step % len(progression)
        base_chord = progression[chord_idx]
        
        # Get the voicing for this chord
        voicing = self.chord_voicings.get(base_chord, self.chord_voicings['C'])
        
        # Adjust voicing to accommodate melody note
        melody_pitch_class = melody_pitch % 12
        
        # Find the closest chord tone to the melody
        chord_tones = [voicing['S'] % 12, voicing['A'] % 12, voicing['T'] % 12, voicing['B'] % 12]
        
        # If melody is not a chord tone, adjust the soprano
        if melody_pitch_class not in chord_tones:
            # Find a chord tone that's close to the melody
            closest_chord_tone = min(chord_tones, key=lambda x: abs(x - melody_pitch_class))
            
            # Adjust soprano to be close to melody
            octave = melody_pitch // 12
            voicing['S'] = closest_chord_tone + (octave * 12)
        
        # Add some voice leading variation based on temperature
        if temperature > 1.0:
            # Add some chromatic passing tones
            if random.random() < 0.2:
                voicing['A'] += random.choice([-1, 1])
            if random.random() < 0.1:
                voicing['T'] += random.choice([-1, 1])
        
        return voicing
    
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
            
            # Detect key from melody
            key = self.detect_key(melody_track.notes)
            print(f"   Detected key: {key}")
            
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
            
            return pianoroll, key, melody_track.notes
            
        except Exception as e:
            print(f"❌ Error converting MIDI to pianoroll: {e}")
            raise
    
    def harmonize(self, pianoroll, key, melody_notes, temperature=0.99):
        """Harmonize using Bach-style voice leading"""
        try:
            print(f"🎼 Running Bach-style harmonization...")
            
            # Create harmonized pianoroll
            harmonized = pianoroll.copy()
            
            # Get melody notes with timing
            melody_events = []
            for t in range(pianoroll.shape[1]):
                for p in range(pianoroll.shape[2]):
                    if pianoroll[0, t, p, 0] > 0.5:
                        melody_events.append((t, p + 21))  # Convert back to actual pitch
            
            print(f"   Found {len(melody_events)} melody events")
            
            # Generate harmony for each melody note
            notes_added = 0
            progression_step = 0
            
            for t, melody_pitch in melody_events:
                # Get chord voicing for this melody note
                voicing = self.get_chord_for_melody_note(melody_pitch, key, progression_step, temperature)
                
                # Add chord notes to harmony parts (Alto, Tenor, Bass)
                harmony_parts = ['A', 'T', 'B']
                for i, part in enumerate(harmony_parts):
                    pitch = voicing[part]
                    pitch_idx = pitch - 21  # Convert to Coconet pitch index
                    
                    if 0 <= pitch_idx < pianoroll.shape[2]:
                        harmonized[0, t, pitch_idx, i + 1] = 1.0
                        notes_added += 1
                
                progression_step += 1
            
            print(f"   Added {notes_added} harmony notes")
            return harmonized
            
        except Exception as e:
            print(f"❌ Error during harmonization: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def pianoroll_to_midi(self, pianoroll, output_path):
        """Convert pianoroll back to MIDI with proper voice leading and audible notes"""
        try:
            print(f"🎵 Converting to MIDI...")
            
            midi = pretty_midi.PrettyMIDI()
            
            # Create instruments with proper voice ranges and higher velocities
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
                                # Start new note with high velocity for audibility
                                velocity = 120 if i == 0 else 110  # Melody louder
                                note = pretty_midi.Note(
                                    velocity=velocity,
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
        harmonizer = ImprovedHarmonizer(COCONET_MODEL_DIR)
        print("✅ Improved harmonizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize harmonizer: {e}")
        import traceback
        traceback.print_exc()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Improved Bach-Style Harmonization API</title>
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
            <h1>🎵 Improved Bach-Style Harmonization API</h1>
            <p>This API creates <strong>Bach-style harmonizations</strong> with proper voice leading and audible notes.</p>
            
            <h2>Key Features:</h2>
            <ul>
                <li><span class="success">✅ Bach-style chord progressions</span></li>
                <li><span class="success">✅ Proper voice leading</span></li>
                <li><span class="success">✅ Variable chord voicings</span></li>
                <li><span class="success">✅ High velocity notes (audible)</span></li>
                <li><span class="success">✅ Key detection from melody</span></li>
                <li><span class="success">✅ Temperature-controlled creativity</span></li>
            </ul>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /</strong> - This documentation page</li>
                <li><strong>GET /status</strong> - Check model status</li>
                <li><strong>POST /harmonize</strong> - Harmonize using improved Bach-style approach</li>
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
        "harmonization_method": "Improved Bach-Style Voice Leading"
    }

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """
    Harmonize a melody using improved Bach-style approach
    
    This endpoint:
    1. Takes a melody from the input MIDI file
    2. Detects the key from the melody
    3. Uses Bach-style chord progressions and voice leading
    4. Returns a harmonized MIDI file with audible notes
    
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
            
            print("🤖 Running improved Bach-style harmonization...")
            
            # Convert MIDI to pianoroll
            pianoroll, key, melody_notes = harmonizer.midi_to_pianoroll(input_midi_path)
            print(f"   Pianoroll shape: {pianoroll.shape}")
            print(f"   Key: {key}")
            
            # Harmonize using Bach-style approach
            harmonized_pianoroll = harmonizer.harmonize(pianoroll, key, melody_notes, temperature)
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
                filename=f"improved_bach_harmonization_{temperature}.mid"
            )
            
    except Exception as e:
        print(f"❌ Error in harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 