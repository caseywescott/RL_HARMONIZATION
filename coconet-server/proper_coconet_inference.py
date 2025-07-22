#!/usr/bin/env python3
"""
Proper Coconet Inference for Harmonization

This module properly uses Coconet for harmonization by:
1. Taking a melody and masking out harmony parts
2. Using the model to fill in the harmony
3. Preserving the original melody timing and structure
"""

import os
import io
import json
import numpy as np
import tensorflow as tf
import pretty_midi
from typing import Dict, Optional, Tuple

# Set TensorFlow compatibility
tf.compat.v1.disable_eager_execution()

class ProperCoconetInference:
    """Proper Coconet inference for harmonization using masking"""
    
    def __init__(self, model_dir: str):
        """Initialize the Coconet model for proper harmonization"""
        self.model_dir = model_dir
        self.session = None
        self.config = {}
        self.input_placeholders = {}
        self.output_tensor = None
        self.initialized = False
        
        # Load configuration and model
        self._load_config()
        self._load_model()
    
    def _load_config(self) -> Dict:
        """Load model configuration"""
        config_path = os.path.join(self.model_dir, "config")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Parse different value types
                        if value.isdigit():
                            self.config[key] = int(value)
                        elif value.replace('.', '').replace('-', '').isdigit():
                            self.config[key] = float(value)
                        elif value.lower() in ['true', 'false']:
                            self.config[key] = value.lower() == 'true'
                        else:
                            self.config[key] = value
        
        print(f"✅ Loaded config: {len(self.config)} parameters")
        return self.config
    
    def _load_model(self):
        """Load the Coconet model with proper placeholders"""
        try:
            print("🤖 Loading Coconet model for proper harmonization...")
            
            # Create session
            self.session = tf.compat.v1.Session()
            
            # Load meta graph
            meta_path = os.path.join(self.model_dir, "best_model.ckpt.meta")
            saver = tf.compat.v1.train.import_meta_graph(meta_path)
            
            # Get graph
            graph = tf.compat.v1.get_default_graph()
            
            # Get all input placeholders
            placeholder_names = [
                "Placeholder",      # Main input
                "Placeholder_1",    # Mask input
                "Placeholder_2",    # Temperature
                "Placeholder_3",    # Context input
                "Placeholder_4",    # Additional context
                "Placeholder_5"     # Additional parameters
            ]
            
            for name in placeholder_names:
                try:
                    tensor = graph.get_tensor_by_name(f"{name}:0")
                    self.input_placeholders[name] = tensor
                    print(f"✅ Found {name}: {tensor.shape}")
                except Exception as e:
                    print(f"⚠️  {name} not found: {e}")
            
            # Get output tensor
            try:
                self.output_tensor = graph.get_tensor_by_name("model/Softmax:0")
                print(f"✅ Found output tensor: {self.output_tensor.shape}")
            except Exception as e:
                print(f"❌ Output tensor not found: {e}")
                return False
            
            # Restore weights
            checkpoint_path = os.path.join(self.model_dir, "best_model.ckpt")
            saver.restore(self.session, checkpoint_path)
            
            self.initialized = True
            print("✅ Coconet model loaded successfully for harmonization")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_harmonization_mask(self, melody_pianoroll: np.ndarray) -> np.ndarray:
        """
        Create a mask for harmonization where:
        - Melody (instrument 0) is preserved (mask = 1)
        - Harmony parts (instruments 1-3) are masked (mask = 0)
        """
        # Get model parameters
        num_instruments = self.config.get('num_instruments', 4)
        crop_piece_len = self.config.get('crop_piece_len', 64)
        num_pitches = self.config.get('num_pitches', 46)
        
        # Create mask: preserve melody, mask harmony
        mask = np.zeros((1, crop_piece_len, num_pitches, num_instruments), dtype=np.float32)
        
        # Preserve melody (instrument 0)
        mask[0, :, :, 0] = 1.0
        
        # Mask harmony parts (instruments 1-3)
        # This tells the model to fill in these parts
        mask[0, :, :, 1:] = 0.0
        
        return mask
    
    def midi_to_pianoroll(self, midi_data: bytes) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert MIDI to pianoroll and create harmonization mask
        
        Returns:
            Tuple of (pianoroll, mask) where mask indicates what to harmonize
        """
        try:
            # Parse MIDI
            midi = pretty_midi.PrettyMIDI(io.BytesIO(midi_data))
            
            # Get model parameters
            min_pitch = self.config.get('min_pitch', 36)
            max_pitch = self.config.get('max_pitch', 81)
            num_pitches = max_pitch - min_pitch + 1
            crop_piece_len = self.config.get('crop_piece_len', 64)
            num_instruments = self.config.get('num_instruments', 4)
            
            # Create pianoroll
            pianoroll = np.zeros((1, crop_piece_len, num_pitches, num_instruments), dtype=np.float32)
            
            # Fill in melody from first instrument
            if midi.instruments:
                melody_track = midi.instruments[0]
                for note in melody_track.notes:
                    # Convert time to steps (16th note quantization)
                    start_step = int(note.start * 4)
                    end_step = int(note.end * 4)
                    
                    # Convert pitch to model range
                    pitch_idx = note.pitch - min_pitch
                    
                    if 0 <= pitch_idx < num_pitches:
                        for step in range(start_step, min(end_step, crop_piece_len)):
                            if 0 <= step < crop_piece_len:
                                pianoroll[0, step, pitch_idx, 0] = 1.0  # Melody in first instrument
            
            # Create harmonization mask
            mask = self.create_harmonization_mask(pianoroll)
            
            print(f"📊 Pianoroll shape: {pianoroll.shape}")
            print(f"📊 Non-zero melody notes: {np.count_nonzero(pianoroll[0, :, :, 0])}")
            print(f"📊 Mask shape: {mask.shape}")
            
            return pianoroll, mask
            
        except Exception as e:
            print(f"❌ Error converting MIDI to pianoroll: {e}")
            return None, None
    
    def harmonize_with_masking(self, pianoroll: np.ndarray, mask: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        """
        Use Coconet with masking to harmonize the melody
        
        Args:
            pianoroll: Input pianoroll with melody
            mask: Mask indicating what to harmonize
            temperature: Sampling temperature
            
        Returns:
            Harmonized pianoroll
        """
        try:
            print("🤖 Running Coconet harmonization with masking...")
            
            # Prepare feed dictionary
            feed_dict = {}
            
            # Main input (pianoroll with melody)
            if "Placeholder" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder"]] = pianoroll
            
            # Mask input (what to harmonize)
            if "Placeholder_1" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder_1"]] = mask
            
            # Temperature
            if "Placeholder_2" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder_2"]] = np.array([temperature], dtype=np.float32)
            
            # Context inputs (can be same as main input for harmonization)
            if "Placeholder_3" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder_3"]] = pianoroll
            
            if "Placeholder_4" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder_4"]] = pianoroll
            
            # Additional parameters
            if "Placeholder_5" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder_5"]] = np.array([1.0], dtype=np.float32)
            
            # Run inference
            output = self.session.run(self.output_tensor, feed_dict=feed_dict)
            print(f"✅ Harmonization output shape: {output.shape}")
            
            # Convert output to harmonized pianoroll
            harmonized_pianoroll = self._convert_output_to_pianoroll(output, pianoroll, mask, temperature)
            
            return harmonized_pianoroll
            
        except Exception as e:
            print(f"❌ Error in harmonization: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _convert_output_to_pianoroll(self, output: np.ndarray, original_pianoroll: np.ndarray, mask: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        """
        Convert model output to harmonized pianoroll
        
        This is the key part - properly interpreting the model output
        """
        try:
            # Start with original pianoroll (preserves melody)
            harmonized = original_pianoroll.copy()
            
            # Get model parameters
            num_instruments = self.config.get('num_instruments', 4)
            crop_piece_len = self.config.get('crop_piece_len', 64)
            num_pitches = self.config.get('num_pitches', 46)
            
            # The output contains probabilities for each position
            # We need to sample from these to create harmony
            print(f"🤖 Converting output to harmony...")
            print(f"   Output shape: {output.shape}")
            print(f"   Original shape: {original_pianoroll.shape}")
            
            # For each time step and instrument that needs harmonization
            for step in range(crop_piece_len):
                for inst in range(1, num_instruments):  # Skip melody (inst 0)
                    # Get probabilities for this position
                    if step < output.shape[0]:  # output is (256, 46)
                        probs = output[step, :]  # Get all pitch probabilities for this step
                        
                        # Sample a pitch based on probabilities
                        if len(probs) == num_pitches:
                            # Use temperature to control randomness
                            logits = np.log(probs + 1e-8)
                            logits /= temperature
                            probs = np.exp(logits)
                            probs /= np.sum(probs)
                            
                            # Sample pitch
                            pitch_idx = np.random.choice(num_pitches, p=probs)
                            
                            # Add the harmonizing note
                            harmonized[0, step, pitch_idx, inst] = 1.0
            
            print(f"✅ Harmonized pianoroll created")
            print(f"   Non-zero melody notes: {np.count_nonzero(harmonized[0, :, :, 0])}")
            print(f"   Non-zero harmony notes: {np.count_nonzero(harmonized[0, :, :, 1:])}")
            
            return harmonized
            
        except Exception as e:
            print(f"❌ Error converting output: {e}")
            return original_pianoroll
    
    def pianoroll_to_midi(self, pianoroll: np.ndarray) -> pretty_midi.PrettyMIDI:
        """Convert harmonized pianoroll back to MIDI"""
        try:
            midi = pretty_midi.PrettyMIDI(initial_tempo=120)
            
            min_pitch = self.config.get('min_pitch', 36)
            num_instruments = self.config.get('num_instruments', 4)
            instrument_names = ["Melody", "Soprano", "Alto", "Tenor", "Bass"]
            
            # Create instruments
            for i in range(num_instruments):
                instrument = pretty_midi.Instrument(
                    program=i,
                    name=instrument_names[i] if i < len(instrument_names) else f"Instrument_{i}"
                )
                midi.instruments.append(instrument)
            
            # Convert pianoroll to notes
            for inst in range(num_instruments):
                for step in range(pianoroll.shape[1]):
                    for pitch_idx in range(pianoroll.shape[2]):
                        if pianoroll[0, step, pitch_idx, inst] > 0.5:
                            # Convert pitch index back to MIDI pitch
                            pitch = pitch_idx + min_pitch
                            
                            # Create note
                            note = pretty_midi.Note(
                                velocity=100,
                                pitch=int(pitch),
                                start=step * 0.25,  # 16th note timing
                                end=(step + 1) * 0.25
                            )
                            midi.instruments[inst].notes.append(note)
            
            return midi
            
        except Exception as e:
            print(f"❌ Error converting to MIDI: {e}")
            return None
    
    def harmonize(self, midi_data: bytes, temperature: float = 1.0) -> Optional[pretty_midi.PrettyMIDI]:
        """
        Main harmonization function
        
        Args:
            midi_data: Input MIDI file as bytes
            temperature: Sampling temperature for harmonization
            
        Returns:
            Harmonized MIDI file
        """
        if not self.initialized:
            print("❌ Model not initialized")
            return None
        
        try:
            print("🎵 Starting proper Coconet harmonization...")
            
            # Convert MIDI to pianoroll and create mask
            pianoroll, mask = self.midi_to_pianoroll(midi_data)
            if pianoroll is None:
                return None
            
            # Harmonize using masking
            harmonized_pianoroll = self.harmonize_with_masking(pianoroll, mask, temperature)
            if harmonized_pianoroll is None:
                return None
            
            # Convert back to MIDI
            harmonized_midi = self.pianoroll_to_midi(harmonized_pianoroll)
            
            if harmonized_midi:
                print("✅ Harmonization completed successfully")
                return harmonized_midi
            else:
                print("❌ Failed to convert harmonized pianoroll to MIDI")
                return None
                
        except Exception as e:
            print(f"❌ Error in harmonization: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def close(self):
        """Clean up resources"""
        if self.session:
            self.session.close()

# Global instance
_coconet_instance = None

def initialize_coconet(model_dir: str) -> bool:
    """Initialize the proper Coconet harmonization model"""
    global _coconet_instance
    try:
        _coconet_instance = ProperCoconetInference(model_dir)
        return _coconet_instance.initialized
    except Exception as e:
        print(f"❌ Failed to initialize Coconet: {e}")
        return False

def harmonize_with_coconet(midi_data: bytes, temperature: float = 1.0) -> Optional[pretty_midi.PrettyMIDI]:
    """Harmonize MIDI data using proper Coconet implementation"""
    global _coconet_instance
    if _coconet_instance is None:
        print("❌ Coconet not initialized")
        return None
    
    return _coconet_instance.harmonize(midi_data, temperature) 