#!/usr/bin/env python3
"""
Test Coconet model loading step by step
"""

import os
import tensorflow as tf
import sys

# Set TensorFlow compatibility
tf.compat.v1.disable_eager_execution()

def test_model_loading():
    """Test loading the Coconet model step by step"""
    try:
        print("🤖 Starting Coconet model loading test...")
        
        model_dir = "/app/coconet-64layers-128filters"
        print(f"📁 Model directory: {model_dir}")
        
        # Check if files exist
        files = os.listdir(model_dir)
        print(f"📄 Model files: {files}")
        
        # Create session
        print("🔧 Creating TensorFlow session...")
        session = tf.compat.v1.Session()
        
        # Load the model graph
        meta_path = os.path.join(model_dir, "best_model.ckpt.meta")
        print(f"📦 Loading meta graph from: {meta_path}")
        
        saver = tf.compat.v1.train.import_meta_graph(meta_path)
        print("✅ Meta graph loaded successfully")
        
        # Get the graph
        graph = tf.compat.v1.get_default_graph()
        print("✅ Graph retrieved")
        
        # Try to get input placeholder
        print("🔍 Looking for input placeholder...")
        try:
            input_placeholder = graph.get_tensor_by_name("Placeholder:0")
            print(f"✅ Input placeholder found: {input_placeholder}")
            print(f"   Shape: {input_placeholder.shape}")
        except Exception as e:
            print(f"❌ Error getting input placeholder: {e}")
        
        # Try to get output tensor
        print("🔍 Looking for output tensor...")
        try:
            output_tensor = graph.get_tensor_by_name("model/Softmax:0")
            print(f"✅ Output tensor found: {output_tensor}")
            print(f"   Shape: {output_tensor.shape}")
        except Exception as e:
            print(f"❌ Error getting output tensor: {e}")
        
        # Try to restore weights
        print("🔧 Restoring model weights...")
        try:
            checkpoint_path = os.path.join(model_dir, "best_model.ckpt")
            saver.restore(session, checkpoint_path)
            print("✅ Model weights restored successfully")
        except Exception as e:
            print(f"❌ Error restoring weights: {e}")
            import traceback
            traceback.print_exc()
        
        session.close()
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_loading() 