#!/usr/bin/env python3

import os
import io
import tempfile
import subprocess
import numpy as np
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, HTMLResponse
import pretty_midi
from typing import Optional
import shutil

app = FastAPI(title="Fixed Masking Coconet Harmonization Server", version="1.0")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"
MAGENTA_COCONET_DIR = "/app/magenta/models/coconet"

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Fixed Masking Coconet Harmonization Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
                .method { color: #007cba; font-weight: bold; }
                .url { color: #333; font-family: monospace; }
                .description { color: #666; }
                .highlight { background: #fff3cd; padding: 10px; border-radius: 5px; }
                .warning { background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎼 Fixed Masking Coconet Harmonization Server</h1>
                <div class="highlight">
                    <strong>🎵 Key Feature:</strong> This server fixes the Coconet masking issue to properly preserve the original melody!
                </div>
                
                <div class="warning">
                    <strong>🔧 Problem Fixed:</strong> The original Coconet harmonization was overwriting the melody. This server implements proper masking to preserve it.
                </div>

                <p>This server uses the official Magenta Coconet scripts with fixed masking to ensure melody preservation.</p>

                <div class="endpoint">
                    <div class="method">GET</div>
                    <div class="url">/status</div>
                    <div class="description">Check server status and model availability</div>
                </div>

                <div class="endpoint">
                    <div class="method">POST</div>
                    <div class="url">/harmonize</div>
                    <div class="description">Harmonize a MIDI melody with fixed masking</div>
                    <p><strong>Parameters:</strong></p>
                    <ul>
                        <li><code>file</code>: MIDI file containing melody to harmonize</li>
                        <li><code>temperature</code>: Sampling temperature (0.1-2.0, default: 0.7)</li>
                        <li><code>melody_strength</code>: Melody velocity multiplier (1.0-3.0, default: 2.0)</li>
                        <li><code>harmony_reduction</code>: Harmony velocity reduction factor (0.1-1.0, default: 0.6)</li>
                    </ul>
                </div>

                <h2>How Fixed Masking Works:</h2>
                <ol>
                    <li><strong>Extract Original Melody</strong> - Parse the input MIDI to get exact melody notes</li>
                    <li><strong>Create Proper Mask</strong> - Mask harmony parts (instruments 1-3) while preserving melody (instrument 0)</li>
                    <li><strong>Run Coconet with Fixed Masking</strong> - Use proper HarmonizationMasker logic</li>
                    <li><strong>Verify Melody Preservation</strong> - Ensure the output contains the original melody</li>
                    <li><strong>Enhance Audibility</strong> - Boost melody velocity and reduce harmony velocity</li>
                </ol>
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

    script_files = []
    if os.path.exists(MAGENTA_COCONET_DIR):
        script_files = os.listdir(MAGENTA_COCONET_DIR)

    return {
        "server_status": "running",
        "model_available": os.path.exists(COCONET_MODEL_DIR),
        "model_path": COCONET_MODEL_DIR,
        "model_files": model_files,
        "magenta_scripts_available": os.path.exists(MAGENTA_COCONET_DIR),
        "magenta_scripts": script_files,
        "harmonization_method": "Fixed Masking Coconet Gibbs Sampling",
        "default_temperature": 0.7,
        "melody_preservation": "fixed_masking"
    }

def create_fixed_masking_strategy():
    """Create a fixed version of the HarmonizeMidiMelodyStrategy"""
    import sys
    sys.path.append('/app')
    
    # Import the original strategy
    from magenta.models.coconet.coconet_sample import HarmonizeMidiMelodyStrategy
    from magenta.models.coconet import lib_sampling, lib_mask
    
    class FixedHarmonizeMidiMelodyStrategy(HarmonizeMidiMelodyStrategy):
        """Fixed version that properly preserves the melody"""
        
        def run(self, tuple_in):
            shape, midi_in = tuple_in
            
            # Load the original melody
            mroll = self.load_midi_melody(midi_in)
            print(f"   Original melody shape: {mroll.shape}")
            
            # Create pianoroll with melody in first instrument
            pianorolls = self.make_pianoroll_from_melody_roll(mroll, shape)
            print(f"   Pianoroll shape: {pianorolls.shape}")
            
            # Create proper harmonization mask
            # This is the key fix: mask harmony parts (1-3) but preserve melody (0)
            masks = np.zeros(pianorolls.shape, dtype=np.float32)
            masks[:, :, :, 1:] = 1.0  # Mask Alto, Tenor, Bass (instruments 1-3)
            masks[:, :, :, 0] = 0.0   # Preserve Soprano (instrument 0)
            
            print(f"   Mask shape: {masks.shape}")
            print(f"   Melody preserved (instrument 0): {np.sum(masks[:, :, :, 0] == 0)} positions")
            print(f"   Harmony masked (instruments 1-3): {np.sum(masks[:, :, :, 1:] == 1)} positions")
            
            # Create Gibbs sampler
            gibbs = self.make_sampler(
                "gibbs",
                masker=lib_sampling.BernoulliMasker(),
                sampler=self.make_sampler("independent", temperature=FLAGS.temperature),
                schedule=lib_sampling.YaoSchedule())

            # Apply mask to create context (melody preserved, harmony zeroed)
            with self.logger.section("context"):
                context = np.array([
                    lib_mask.apply_mask(pianoroll, mask)
                    for pianoroll, mask in zip(pianorolls, masks)
                ])
                self.logger.log(pianorolls=context, masks=masks, predictions=context)
            
            # Run Gibbs sampling to fill in harmony
            print(f"   Running Gibbs sampling with fixed masking...")
            pianorolls = gibbs(pianorolls, masks)
            
            # Verify melody preservation
            original_melody = mroll
            final_melody = pianorolls[0, :, :, 0]  # First instrument
            
            # Check if melody is preserved
            melody_preserved = np.array_equal(original_melody, final_melody)
            print(f"   Melody preservation check: {'✅ PRESERVED' if melody_preserved else '❌ LOST'}")
            
            if not melody_preserved:
                print(f"   ⚠️  Melody was not preserved by masking, applying post-processing...")
                # Apply post-processing to restore melody
                pianorolls[0, :, :, 0] = original_melody
            
            return pianorolls
    
    return FixedHarmonizeMidiMelodyStrategy

def run_fixed_coconet_harmonization(input_midi_path: str, output_dir: str, temperature: float):
    """Run Coconet harmonization with fixed masking"""
    try:
        print(f"   Running fixed Coconet harmonization...")
        
        # Create a temporary Python script with the fixed strategy
        fixed_script_content = f'''
#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

import tensorflow.compat.v1 as tf
from magenta.models.coconet.coconet_sample import *
from magenta.models.coconet import lib_sampling, lib_mask
import numpy as np

# Override the strategy
class FixedHarmonizeMidiMelodyStrategy(HarmonizeMidiMelodyStrategy):
    def run(self, tuple_in):
        shape, midi_in = tuple_in
        
        # Load the original melody
        mroll = self.load_midi_melody(midi_in)
        print(f"Original melody shape: {{mroll.shape}}")
        
        # Create pianoroll with melody in first instrument
        pianorolls = self.make_pianoroll_from_melody_roll(mroll, shape)
        print(f"Pianoroll shape: {{pianorolls.shape}}")
        
        # Create proper harmonization mask
        masks = np.zeros(pianorolls.shape, dtype=np.float32)
        masks[:, :, :, 1:] = 1.0  # Mask Alto, Tenor, Bass
        masks[:, :, :, 0] = 0.0   # Preserve Soprano
        
        print(f"Mask applied - melody preserved, harmony masked")
        
        # Create Gibbs sampler
        gibbs = self.make_sampler(
            "gibbs",
            masker=lib_sampling.BernoulliMasker(),
            sampler=self.make_sampler("independent", temperature={temperature}),
            schedule=lib_sampling.YaoSchedule())

        # Apply mask to create context
        context = np.array([
            lib_mask.apply_mask(pianoroll, mask)
            for pianoroll, mask in zip(pianorolls, masks)
        ])
        
        # Run Gibbs sampling to fill in harmony
        print(f"Running Gibbs sampling with fixed masking...")
        pianorolls = gibbs(pianorolls, masks)
        
        # Verify and restore melody if needed
        original_melody = mroll
        final_melody = pianorolls[0, :, :, 0]
        
        if not np.array_equal(original_melody, final_melody):
            print(f"Restoring original melody...")
            pianorolls[0, :, :, 0] = original_melody
        
        return pianorolls

# Override the strategy in the main function
if __name__ == "__main__":
    # Replace the strategy
    HarmonizeMidiMelodyStrategy = FixedHarmonizeMidiMelodyStrategy
    
    # Run the original main function
    tf.app.run()
'''
        
        # Write the fixed script
        fixed_script_path = os.path.join(output_dir, "fixed_coconet_sample.py")
        with open(fixed_script_path, 'w') as f:
            f.write(fixed_script_content)
        
        # Run the fixed Coconet script
        cmd = [
            "python",
            fixed_script_path,
            "--checkpoint", COCONET_MODEL_DIR,
            "--gen_batch_size", "1",
            "--piece_length", "32",
            "--temperature", str(temperature),
            "--strategy", "harmonize_midi_melody",
            "--tfsample", "False",
            "--generation_output_dir", output_dir,
            "--prime_midi_melody_fpath", input_midi_path,
            "--logtostderr"
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = f"/app:{env.get('PYTHONPATH', '')}"
        
        # Run the command
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"   Command completed with return code: {result.returncode}")
        if result.stderr:
            print(f"   stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Fixed Coconet sampling failed: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error in fixed Coconet harmonization: {e}")
        return False

def enhance_melody_visibility(midi_file_path: str, melody_strength: float = 2.0, harmony_reduction: float = 0.6):
    """Enhance melody visibility in the harmonized MIDI"""
    try:
        print(f"   Enhancing melody visibility...")
        
        # Load the harmonized MIDI
        midi = pretty_midi.PrettyMIDI(midi_file_path)
        
        if not midi.instruments:
            return False
        
        # Boost melody (first instrument) velocity
        if midi.instruments[0].notes:
            for note in midi.instruments[0].notes:
                note.velocity = min(127, int(note.velocity * melody_strength))
        
        # Reduce harmony instruments velocity
        for instrument in midi.instruments[1:]:
            for note in instrument.notes:
                note.velocity = max(40, int(note.velocity * harmony_reduction))
        
        # Save the enhanced MIDI
        midi.write(midi_file_path)
        print(f"   ✅ Enhanced MIDI saved")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error enhancing melody visibility: {e}")
        return False

def verify_melody_preservation(original_midi_path: str, harmonized_midi_path: str):
    """Verify that the original melody is preserved"""
    try:
        print(f"   Verifying melody preservation...")
        
        # Load both MIDI files
        original_midi = pretty_midi.PrettyMIDI(original_midi_path)
        harmonized_midi = pretty_midi.PrettyMIDI(harmonized_midi_path)
        
        if not original_midi.instruments or not harmonized_midi.instruments:
            return False
        
        # Extract original melody
        original_notes = []
        for note in original_midi.instruments[0].notes:
            original_notes.append(note.pitch)
        
        # Extract harmonized melody (first instrument)
        harmonized_notes = []
        for note in harmonized_midi.instruments[0].notes:
            harmonized_notes.append(note.pitch)
        
        # Check if they match
        if original_notes == harmonized_notes:
            print(f"   ✅ VERIFICATION PASSED: Original melody is preserved!")
            return True
        else:
            print(f"   ❌ VERIFICATION FAILED: Melody mismatch")
            print(f"      Original: {original_notes}")
            print(f"      Harmonized: {harmonized_notes}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in verification: {e}")
        return False

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.7, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
    melody_strength: float = Query(2.0, description="Melody velocity multiplier (1.0-3.0)", ge=1.0, le=3.0),
    harmony_reduction: float = Query(0.6, description="Harmony velocity reduction factor (0.1-1.0)", ge=0.1, le=1.0),
):
    """Harmonize a MIDI melody with fixed masking"""
    try:
        print(f"🎵 Received fixed masking harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")
        print(f"   Melody strength: {melody_strength}")
        print(f"   Harmony reduction: {harmony_reduction}")

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded MIDI file
            input_midi_path = os.path.join(temp_dir, "input.mid")
            with open(input_midi_path, "wb") as f:
                content = await file.read()
                f.write(content)

            print(f"   Saved input MIDI to: {input_midi_path}")

            # Analyze the input MIDI to determine appropriate piece length
            input_midi = pretty_midi.PrettyMIDI(input_midi_path)
            duration_seconds = input_midi.get_end_time()

            # Convert duration to time steps
            piece_length = max(32, int(duration_seconds / 0.25) + 8)

            print(f"   Input duration: {duration_seconds:.2f} seconds")
            print(f"   Calculated piece length: {piece_length} time steps")

            # Create output directory
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)

            # Run fixed Coconet harmonization
            success = run_fixed_coconet_harmonization(input_midi_path, output_dir, temperature)
            
            if not success:
                raise Exception("Fixed Coconet harmonization failed")

            # Find the generated output directory
            output_dirs = os.listdir(output_dir)
            print(f"   Output directories: {output_dirs}")

            if not output_dirs:
                raise Exception("No output directories generated")

            # The Coconet script creates a directory with the MIDI file inside
            sample_dir = os.path.join(output_dir, output_dirs[0])
            midi_dir = os.path.join(sample_dir, "midi")

            if not os.path.exists(midi_dir):
                raise Exception(f"MIDI directory not found: {midi_dir}")

            # Find the MIDI file in the midi subdirectory
            midi_files = os.listdir(midi_dir)
            print(f"   MIDI files: {midi_files}")

            if not midi_files:
                raise Exception("No MIDI files generated")

            # Get the harmonized MIDI file
            harmonized_file = os.path.join(midi_dir, midi_files[0])

            # Enhance melody visibility
            print(f"   Applying melody enhancement...")
            enhance_success = enhance_melody_visibility(harmonized_file, melody_strength, harmony_reduction)
            
            if not enhance_success:
                print(f"   ⚠️  Warning: Could not enhance melody visibility")

            # Verify melody preservation
            print(f"   Verifying melody preservation...")
            verification_success = verify_melody_preservation(input_midi_path, harmonized_file)
            
            if not verification_success:
                print(f"   ⚠️  Warning: Melody preservation verification failed")
            else:
                print(f"   ✅ Melody preservation verified successfully!")

            print(f"   Returning harmonized file with fixed masking: {harmonized_file}")

            # Copy the file to a persistent location
            persistent_file = f"/tmp/fixed_masking_harmonized_{file.filename}"
            shutil.copy2(harmonized_file, persistent_file)

            return FileResponse(
                persistent_file,
                media_type="audio/midi",
                filename=f"fixed_masking_harmonized_{file.filename}"
            )

    except subprocess.TimeoutExpired:
        print(f"❌ Coconet sampling timed out")
        return {"error": "Harmonization timed out. Please try again."}
    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Harmonization failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 