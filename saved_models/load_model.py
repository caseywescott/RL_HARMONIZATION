#!/usr/bin/env python3
"""
Load the trained RL harmonization model
"""

import json
import os
import numpy as np

def load_model():
    """Load the trained model and metadata"""
    model_dir = "saved_models"
    
    # Load metadata
    metadata_path = os.path.join(model_dir, "model_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        print("🎵 RL Harmonization Model Loaded Successfully!")
        print(f"Model: {metadata['model_name']}")
        print(f"Version: {metadata['version']}")
        print(f"Training date: {metadata['training_date']}")
        print(f"Episodes trained: {metadata['episodes_trained']}")
        print(f"Average reward: {metadata['average_reward']}")
        print(f"Best reward: {metadata['best_reward']}")
        print(f"Improvement: {metadata['performance']['improvement']}")
        
        return metadata
    else:
        print("❌ Model metadata not found")
        return None

def get_training_history():
    """Load training history"""
    history_path = "saved_models/reward_history.npy"
    if os.path.exists(history_path):
        rewards = np.load(history_path)
        print(f"Training history loaded: {len(rewards)} episodes")
        return rewards
    else:
        print("❌ Training history not found")
        return None

if __name__ == "__main__":
    model = load_model()
    if model:
        history = get_training_history()
