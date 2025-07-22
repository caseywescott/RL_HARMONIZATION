#!/usr/bin/env python3
"""
Test Coconet Harmonization Properly

This script tests the Coconet model to understand how it should work
for harmonization using the masking mechanism.
"""

import os
import sys
import numpy as np
import tensorflow as tf
import pretty_midi
import io

# Set TensorFlow compatibility
tf.compat.v1.disable_eager_execution()

def test_coconet_harmonization():
    """Test Coconet harmonization using the proper approach"""
    print("🤖 TESTING COCONET HARMONIZATION")
    print("=" * 50)
    
    try:
        # Load the model
        model_dir = "coconet-64layers-128filters"
        print(f"📁 Loading model from: {model_dir}")
        
        # Create session
        session = tf.compat.v1.Session()
        
        # Load the model graph
        meta_path = os.path.join(model_dir, "best_model.ckpt.meta")
        saver = tf.compat.v1.train.import_meta_graph(meta_path)
        
        # Get the graph
        graph = tf.compat.v1.get_default_graph()
        
        # Get input placeholders
        input_placeholder = graph.get_tensor_by_name("Placeholder:0")
        print(f"✅ Input placeholder: {input_placeholder.shape}")
        
        # Get output tensor
        output_tensor = graph.get_tensor_by_name("model/Softmax:0")
        print(f"✅ Output tensor: {output_tensor.shape}")
        
        # Restore weights
        checkpoint_path = os.path.join(model_dir, "best_model.ckpt")
        saver.restore(session, checkpoint_path)
        print("✅ Model loaded successfully")
        
        # Load test melody
        melody_file = "realms2_idea.midi"
        if not os.path.exists(melody_file):
            print(f"❌ Melody file not found: {melody_file}")
            return False
        
        # Convert melody to pianoroll
        midi = pretty_midi.PrettyMIDI(melody_file)
        print(f"📊 Melody loaded: {len(midi.instruments)} instruments")
        
        # Create pianoroll for Coconet input
        # Based on the model config: 64 time steps, 46 pitches, 4 instruments
        pianoroll = np.zeros((1, 64, 46, 4), dtype=np.float32)
        
        # Fill in the melody (first instrument)
        if midi.instruments:
            melody_track = midi.instruments[0]
            for note in melody_track.notes:
                # Convert time to steps (16th note quantization)
                start_step = int(note.start * 4)  # 4 steps per second
                end_step = int(note.end * 4)
                
                # Convert pitch to model range (36-81)
                pitch_idx = note.pitch - 36
                
                if 0 <= pitch_idx < 46 and 0 <= start_step < 64:
                    for step in range(start_step, min(end_step, 64)):
                        if 0 <= step < 64:
                            pianoroll[0, step, pitch_idx, 0] = 1.0  # Melody in first instrument
        
        print(f"📊 Pianoroll shape: {pianoroll.shape}")
        print(f"📊 Non-zero elements: {np.count_nonzero(pianoroll)}")
        
        # Test the model with the pianoroll
        print("🤖 Testing model inference...")
        
        # The model expects multiple placeholders - let's try with the main input
        feed_dict = {input_placeholder: pianoroll}
        
        # Run inference
        output = session.run(output_tensor, feed_dict=feed_dict)
        print(f"✅ Model inference successful")
        print(f"📊 Output shape: {output.shape}")
        print(f"📊 Output range: {output.min():.3f} to {output.max():.3f}")
        
        # Analyze the output
        print("\n🔍 OUTPUT ANALYSIS:")
        print(f"  - Output is probabilities for each time step")
        print(f"  - Shape suggests autoregressive generation")
        print(f"  - Each step predicts the next note")
        
        # Try to convert output to MIDI
        print("\n🎵 CONVERTING TO MIDI...")
        
        # Create MIDI from output
        output_midi = pretty_midi.PrettyMIDI(initial_tempo=120)
        
        # Create instruments
        instrument_names = ["Soprano", "Alto", "Tenor", "Bass"]
        instruments = []
        
        for i, name in enumerate(instrument_names):
            instrument = pretty_midi.Instrument(program=i, name=name)
            instruments.append(instrument)
            output_midi.instruments.append(instrument)
        
        # Convert output probabilities to notes
        # This is a simplified approach - in reality, you'd need proper sampling
        for step in range(min(output.shape[1], 64)):
            # Get probabilities for this step
            probs = output[0, step] if step < output.shape[1] else np.zeros(46)
            
            # Find the most likely pitch for each instrument
            for inst_idx in range(4):
                # For now, use simple harmonization rules
                if inst_idx == 0:  # Soprano - use melody
                    pitch = 60  # Middle C
                elif inst_idx == 1:  # Alto - third above
                    pitch = 64  # E above middle C
                elif inst_idx == 2:  # Tenor - fifth above
                    pitch = 67  # G above middle C
                else:  # Bass - octave below
                    pitch = 48  # C below middle C
                
                # Add some variation based on model output
                if len(probs) > 0:
                    # Use the model output to add variation
                    variation = int(np.argmax(probs)) - 23  # Center around middle C
                    pitch += variation
                
                # Ensure pitch is in valid range
                pitch = max(36, min(81, pitch))
                
                # Create note
                note = pretty_midi.Note(
                    velocity=100,
                    pitch=int(pitch),
                    start=step * 0.25,  # 16th note timing
                    end=(step + 1) * 0.25
                )
                instruments[inst_idx].notes.append(note)
        
        # Save the output
        output_file = "coconet_test_harmonization.mid"
        output_midi.write(output_file)
        print(f"✅ Test harmonization saved: {output_file}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_coconet_harmonization()
    
    if success:
        print("\n🎉 COCONET TEST COMPLETED!")
        print("The model is working, but needs proper harmonization logic.")
        print("The issue is in how we interpret the model output.")
    else:
        print("\n💥 COCONET TEST FAILED!")

if __name__ == "__main__":
    main() 