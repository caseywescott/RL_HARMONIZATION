#!/usr/bin/env python3

import os
import tempfile
import subprocess
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Corrected Melody Preserving Coconet Server")

# Paths
COCONET_MODEL_DIR = "/app/coconet-64layers-128filters"

@app.get("/status")
async def status():
    return {"status": "running", "model": "corrected-melody-preserving-coconet"}

def run_corrected_coconet_harmonization(input_midi_path: str, output_dir: str, temperature: float):
    """Run Coconet harmonization with corrected melody preservation"""
    try:
        print(f"   Running corrected Coconet harmonization...")

        # Create a temporary Python script with the corrected masker
        corrected_script_content = f'''
#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

import tensorflow.compat.v1 as tf
# Disable eager execution for Coconet compatibility
tf.compat.v1.disable_eager_execution()
from magenta.models.coconet.coconet_sample import *
from magenta.models.coconet import lib_sampling, lib_mask
import numpy as np

# Create corrected melody-preserving masker
class CorrectedMelodyPreservingMasker(lib_sampling.BaseMasker):
    """Correctly masks harmony parts while preserving melody.
    
    When mask_indicates_context=True:
    - mask=1 means "preserved context" (keep this)
    - mask=0 means "to be filled in" (generate this)
    
    For melody preservation:
    - melody (instrument 0) should have mask=1 (preserve)
    - harmony (instruments 1-3) should have mask=0 (fill in)
    """
    key = "corrected_melody_preserving"

    def __call__(self, shape, outer_masks=1., separate_instruments=True):
        if not separate_instruments:
            raise NotImplementedError()

        # Create mask where:
        # - mask=1 means "preserved context" (melody in instrument 0)
        # - mask=0 means "to be filled in" (harmony in instruments 1-3)
        masks = np.zeros(shape, dtype=np.float32)
        masks[:, :, :, 0] = 1.0  # Preserve melody (instrument 0)
        masks[:, :, :, 1:] = 0.0  # Fill in harmony (instruments 1-3)

        return masks * outer_masks

# Override the HarmonizeMidiMelodyStrategy to use our corrected masker
class CorrectedHarmonizeMidiMelodyStrategy(HarmonizeMidiMelodyStrategy):
    def run(self, tuple_in):
        shape, midi_in = tuple_in
        mroll = self.load_midi_melody(midi_in)
        pianorolls = self.make_pianoroll_from_melody_roll(mroll, shape)

        # Use our corrected masker instead of the default HarmonizationMasker
        masks = CorrectedMelodyPreservingMasker()(pianorolls.shape)

        gibbs = self.make_sampler(
            "gibbs",
            masker=lib_sampling.BernoulliMasker(),
            sampler=self.make_sampler("independent", temperature={temperature}),
            schedule=lib_sampling.YaoSchedule())

        with self.logger.section("context"):
            context = np.array([
                lib_mask.apply_mask(pianoroll, mask)
                for pianoroll, mask in zip(pianorolls, masks)
            ])
            self.logger.log(pianorolls=context, masks=masks, predictions=context)

        pianorolls = gibbs(pianorolls, masks)
        return pianorolls

# Override the strategy in the main function
if __name__ == "__main__":
    # Replace the strategy
    HarmonizeMidiMelodyStrategy = CorrectedHarmonizeMidiMelodyStrategy

    # Run the original main function
    tf.app.run()
'''

        # Write the corrected script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(corrected_script_content)
            corrected_script_path = f.name

        try:
            # Run the corrected Coconet script
            command = [
                "python", corrected_script_path,
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

            print(f"   Running command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, cwd="/app")

            if result.returncode != 0:
                print(f"   Command completed with return code: {result.returncode}")
                print(f"   stderr: {result.stderr}")
                raise Exception(f"Coconet sampling failed: {result.stderr}")

            print(f"   Command completed successfully")

        finally:
            # Clean up the temporary script
            os.unlink(corrected_script_path)

        # Find generated MIDI files (Coconet creates subdirectories)
        midi_files = []
        for root, dirs, files in os.walk(output_dir):
            for midi_file in files:
                if midi_file.endswith('.mid') or midi_file.endswith('.midi'):
                    midi_files.append(os.path.join(root, midi_file))

        if not midi_files:
            raise Exception("No MIDI files generated")

        # Get the harmonized MIDI file
        harmonized_file = midi_files[0]
        print(f"   Generated harmonization: {harmized_file}")

        return harmonized_file

    except Exception as e:
        print(f"   ❌ Error in corrected harmonization: {e}")
        raise

@app.post("/harmonize")
async def harmonize_melody(
    file: UploadFile = File(..., description="MIDI file containing melody to harmonize"),
    temperature: float = Query(0.99, description="Sampling temperature (0.1-2.0)", ge=0.1, le=2.0),
):
    """Harmonize a melody using Coconet with corrected melody preservation."""
    try:
        print(f"🎵 Received harmonization request")
        print(f"   File: {file.filename}")
        print(f"   Temperature: {temperature}")

        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(input_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)

            # Save uploaded file
            input_path = os.path.join(input_dir, "input.mid")
            with open(input_path, "wb") as f:
                f.write(await file.read())
            print(f"   Saved input MIDI to: {input_path}")

            # Run corrected harmonization
            harmonized_file = run_corrected_coconet_harmonization(input_path, output_dir, temperature)

            # Return the harmonized file
            return FileResponse(
                harmonized_file,
                media_type="audio/midi",
                filename=f"corrected_harmonization_temp_{temperature}.mid"
            )

    except Exception as e:
        print(f"❌ Error during harmonization: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 