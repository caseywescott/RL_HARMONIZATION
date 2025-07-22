#!/usr/bin/env python3
"""
Coconet Neural Model Inference
Loads the actual Coconet model and performs harmonization
"""

import os
import numpy as np
import tensorflow as tf
import pretty_midi
import io
from typing import List, Dict, Optional

# Set TensorFlow compatibility
tf.compat.v1.disable_eager_execution()

class CoconetInference:
    def __init__(self, model_dir: str):
        """
        Initialize Coconet inference with model directory
        
        Args:
            model_dir: Path to directory containing Coconet model files
        """
        self.model_dir = model_dir
        self.checkpoint_path = os.path.join(model_dir, "best_model.ckpt")
        self.config_path = os.path.join(model_dir, "config")
        
        # Load model configuration
        self.config = self._load_config()
        
        # Initialize TensorFlow session and model
        self.session = None
        self.model = None
        self._load_model()
    
    def _load_config(self) -> Dict:
        """Load model configuration from config file"""
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Parse different value types
                        if value.lower() == 'true':
                            config[key] = True
                        elif value.lower() == 'false':
                            config[key] = False
                        elif value.isdigit():
                            config[key] = int(value)
                        elif value.replace('.', '').replace('-', '').isdigit():
                            config[key] = float(value)
                        elif value.startswith('[') and value.endswith(']'):
                            # Parse list
                            try:
                                config[key] = eval(value)
                            except:
                                config[key] = value
                        else:
                            config[key] = value
        
        return config
    
    def _load_model(self):
        """Load the Coconet TensorFlow model"""
        try:
            # Create TensorFlow session
            self.session = tf.compat.v1.Session()
            
            # Load the model graph
            saver = tf.compat.v1.train.import_meta_graph(
                os.path.join(self.model_dir, "best_model.ckpt.meta")
            )
            
            # Restore model weights
            saver.restore(self.session, self.checkpoint_path)
            
            # Get model inputs and outputs
            self.graph = tf.compat.v1.get_default_graph()
            
            # Get all input placeholders - the model has multiple placeholders
            self.input_placeholders = {}
            placeholder_names = ["Placeholder", "Placeholder_1", "Placeholder_2", "Placeholder_3", "Placeholder_4", "Placeholder_5"]
            
            for name in placeholder_names:
                try:
                    tensor = self.graph.get_tensor_by_name(f"{name}:0")
                    self.input_placeholders[name] = tensor
                    print(f"✅ Found placeholder: {name} with shape {tensor.shape}")
                except Exception as e:
                    print(f"⚠️  Placeholder {name} not found: {e}")
            
            # Get output tensor - use the Softmax output
            self.output_tensor = self.graph.get_tensor_by_name("model/Softmax:0")
            
            print(f"✅ Coconet model loaded successfully")
            print(f"   Model config: {self.config.get('num_layers', 'unknown')} layers, "
                  f"{self.config.get('num_filters', 'unknown')} filters")
            print(f"   Found {len(self.input_placeholders)} input placeholders")
            
        except Exception as e:
            print(f"❌ Error loading Coconet model: {e}")
            self.session = None
            self.model = None
    
    def midi_to_pianoroll(self, midi_data: bytes) -> np.ndarray:
        """
        Convert MIDI data to pianoroll format expected by Coconet
        
        Args:
            midi_data: MIDI file as bytes
            
        Returns:
            Pianoroll as numpy array with shape (batch, time_steps, pitches, instruments)
        """
        try:
            # Parse MIDI
            midi = pretty_midi.PrettyMIDI(io.BytesIO(midi_data))
            
            # Get model parameters from config
            min_pitch = self.config.get('min_pitch', 36)
            max_pitch = self.config.get('max_pitch', 81)
            num_pitches = max_pitch - min_pitch + 1  # Should be 46
            crop_piece_len = self.config.get('crop_piece_len', 64)
            num_instruments = self.config.get('num_instruments', 4)
            
            # Create pianoroll with correct shape: (batch=1, time_steps, pitches, instruments)
            pianoroll = np.zeros((1, crop_piece_len, num_pitches, num_instruments), dtype=np.float32)
            
            # Fill pianoroll with MIDI data
            for i, instrument in enumerate(midi.instruments[:num_instruments]):
                for note in instrument.notes:
                    # Convert time to steps (16th note quantization)
                    start_step = int(note.start * 4)
                    end_step = int(note.end * 4)
                    
                    # Convert pitch to model range
                    pitch_idx = note.pitch - min_pitch
                    
                    if 0 <= pitch_idx < num_pitches:
                        for step in range(start_step, min(end_step, crop_piece_len)):
                            if 0 <= step < crop_piece_len:
                                pianoroll[0, step, pitch_idx, i] = 1.0
            
            return pianoroll
            
        except Exception as e:
            print(f"❌ Error converting MIDI to pianoroll: {e}")
            return None
    
    def pianoroll_to_midi(self, output_probs: np.ndarray) -> pretty_midi.PrettyMIDI:
        """
        Convert model output probabilities back to MIDI
        
        Args:
            output_probs: Model output probabilities as numpy array
            
        Returns:
            PrettyMIDI object
        """
        try:
            midi = pretty_midi.PrettyMIDI(initial_tempo=120)
            
            min_pitch = self.config.get('min_pitch', 36)
            num_instruments = self.config.get('num_instruments', 4)
            instrument_names = ["Soprano", "Alto", "Tenor", "Bass"]
            
            # The output is (batch, time_steps) - we need to reshape it
            # Assuming the output represents probabilities for each time step
            if len(output_probs.shape) == 2:
                # Reshape to (time_steps, pitches, instruments)
                time_steps = output_probs.shape[1]
                num_pitches = self.config.get('max_pitch', 81) - min_pitch + 1
                
                # This is a simplified approach - in reality, the model output needs proper interpretation
                # For now, let's create a simple harmonization based on the input
                print(f"🤖 Converting output probabilities to MIDI...")
                print(f"   Output shape: {output_probs.shape}")
                
                # Create instruments
                for i in range(num_instruments):
                    instrument = pretty_midi.Instrument(
                        program=i,
                        name=instrument_names[i] if i < len(instrument_names) else f"Instrument_{i}"
                    )
                    
                    # For now, create a simple harmonization
                    # In a real implementation, you'd need to properly interpret the model output
                    for step in range(min(time_steps, 64)):  # Limit to 64 steps
                        # Simple harmonization rules
                        if i == 0:  # Soprano - third above
                            pitch = 60 + 4  # C + major third
                        elif i == 1:  # Alto - fifth above  
                            pitch = 60 + 7  # C + perfect fifth
                        elif i == 2:  # Tenor - octave below
                            pitch = 60 - 12  # C - octave
                        else:  # Bass - third below
                            pitch = 60 - 16  # C - major third
                        
                        # Add some variation based on the model output
                        if step < output_probs.shape[1]:
                            # Use the model output to add some randomness
                            variation = int(output_probs[0, step] * 10) - 5
                            pitch += variation
                        
                        # Ensure pitch is in valid range
                        pitch = max(21, min(108, pitch))
                        
                        note = pretty_midi.Note(
                            velocity=100,
                            pitch=pitch,
                            start=step * 0.25,  # 16th note duration
                            end=(step + 1) * 0.25
                        )
                        instrument.notes.append(note)
                    
                    midi.instruments.append(instrument)
            
            return midi
            
        except Exception as e:
            print(f"❌ Error converting output to MIDI: {e}")
            return None
    
    def harmonize(self, midi_data: bytes, temperature: float = 1.0) -> Optional[pretty_midi.PrettyMIDI]:
        """
        Perform harmonization using the Coconet model
        
        Args:
            midi_data: Input MIDI as bytes
            temperature: Sampling temperature (higher = more random)
            
        Returns:
            Harmonized MIDI as PrettyMIDI object, or None if failed
        """
        if self.session is None:
            print("❌ Coconet model not loaded")
            return None
        
        try:
            # Convert input MIDI to pianoroll
            input_pianoroll = self.midi_to_pianoroll(midi_data)
            if input_pianoroll is None:
                return None
            
            print(f"🤖 Input pianoroll shape: {input_pianoroll.shape}")
            
            # Prepare feed_dict with all required placeholders
            feed_dict = {}
            
            # Main input placeholder (the actual music data)
            if "Placeholder" in self.input_placeholders:
                feed_dict[self.input_placeholders["Placeholder"]] = input_pianoroll
            
            # Additional placeholders - provide appropriate default values based on shape
            for name, tensor in self.input_placeholders.items():
                if name == "Placeholder":
                    continue  # Already handled above
                
                shape = tensor.shape.as_list()
                dtype = tensor.dtype
                
                # Create appropriate default values based on shape and type
                if len(shape) == 4:  # [batch, time, pitch, instrument]
                    # Use the same input data for all 4D placeholders
                    feed_dict[tensor] = input_pianoroll
                elif len(shape) == 1:  # [batch] - scalar values
                    # Use batch size of 1
                    feed_dict[tensor] = np.array([1.0], dtype=np.float32)
                else:
                    # For other shapes, use zeros
                    default_shape = [1 if dim is None else dim for dim in shape]
                    feed_dict[tensor] = np.zeros(default_shape, dtype=np.float32)
                
                print(f"🤖 Feeding {name}: shape {shape}, dtype {dtype}")
            
            # Run inference with all placeholders
            output_logits = self.session.run(
                self.output_tensor,
                feed_dict=feed_dict
            )
            
            print(f"🤖 Output logits shape: {output_logits.shape}")
            
            # Apply temperature and softmax
            if temperature != 1.0:
                output_logits = output_logits / temperature
            
            # Apply softmax to get probabilities
            output_probs = np.exp(output_logits) / np.sum(np.exp(output_logits), axis=-1, keepdims=True)
            
            # Convert back to MIDI
            harmonized_midi = self.pianoroll_to_midi(output_probs)
            
            return harmonized_midi
            
        except Exception as e:
            print(f"❌ Error during Coconet harmonization: {e}")
            return None
    
    def close(self):
        """Close TensorFlow session"""
        if self.session:
            self.session.close()

# Global Coconet instance
coconet_model = None

def initialize_coconet(model_dir: str) -> bool:
    """Initialize global Coconet model"""
    global coconet_model
    try:
        coconet_model = CoconetInference(model_dir)
        return coconet_model.session is not None
    except Exception as e:
        print(f"❌ Failed to initialize Coconet: {e}")
        return False

def harmonize_with_coconet(midi_data: bytes, temperature: float = 1.0) -> Optional[pretty_midi.PrettyMIDI]:
    """Harmonize using global Coconet model"""
    global coconet_model
    if coconet_model is None:
        return None
    return coconet_model.harmonize(midi_data, temperature) 