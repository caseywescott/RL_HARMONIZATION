#!/usr/bin/env python3
"""
Debug script to examine Coconet model structure
"""

import os
import tensorflow as tf

# Set TensorFlow compatibility
tf.compat.v1.disable_eager_execution()

def examine_model(model_dir):
    """Examine the Coconet model structure"""
    try:
        # Create session
        session = tf.compat.v1.Session()
        
        # Load the model graph
        meta_path = os.path.join(model_dir, "best_model.ckpt.meta")
        print(f"Loading model from: {meta_path}")
        
        saver = tf.compat.v1.train.import_meta_graph(meta_path)
        
        # Get the graph
        graph = tf.compat.v1.get_default_graph()
        
        # List all operations in the graph
        print("\n=== ALL OPERATIONS ===")
        operations = graph.get_operations()
        for op in operations[:50]:  # Show first 50
            print(f"  {op.name}")
        
        print(f"\n... and {len(operations) - 50} more operations")
        
        # Look for input placeholders
        print("\n=== INPUT PLACEHOLDERS ===")
        placeholders = [op for op in operations if 'placeholder' in op.name.lower()]
        for ph in placeholders:
            print(f"  {ph.name}")
            # Get the tensor and examine its shape
            tensor = graph.get_tensor_by_name(f"{ph.name}:0")
            print(f"    Shape: {tensor.shape}")
            print(f"    Dtype: {tensor.dtype}")
        
        # Look for output tensors
        print("\n=== OUTPUT TENSORS ===")
        outputs = [op for op in operations if any(x in op.name.lower() for x in ['output', 'logits', 'softmax', 'predict'])]
        for out in outputs:
            print(f"  {out.name}")
            # Get the tensor and examine its shape
            tensor = graph.get_tensor_by_name(f"{out.name}:0")
            print(f"    Shape: {tensor.shape}")
            print(f"    Dtype: {tensor.dtype}")
        
        # Look for variables
        print("\n=== VARIABLES ===")
        variables = [op for op in operations if 'variable' in op.name.lower()]
        for var in variables[:20]:  # Show first 20
            print(f"  {var.name}")
        
        session.close()
        
    except Exception as e:
        print(f"Error examining model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    model_dir = "/app/coconet-64layers-128filters"
    examine_model(model_dir) 