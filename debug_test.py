#!/usr/bin/env python3
"""
Debug test to identify import issues.
"""

import sys
import os

print("🔍 Debug test starting...")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if src exists
if os.path.exists('src'):
    print("✅ src directory exists")
else:
    print("❌ src directory not found")

# Add src to path
sys.path.append('src')
print(f"Python path: {sys.path}")

# Try importing numpy
try:
    import numpy as np
    print("✅ numpy imported successfully")
except Exception as e:
    print(f"❌ numpy import failed: {e}")

# Try importing mido
try:
    import mido
    print("✅ mido imported successfully")
except Exception as e:
    print(f"❌ mido import failed: {e}")

# Try importing gym
try:
    import gym
    print("✅ gym imported successfully")
except Exception as e:
    print(f"❌ gym import failed: {e}")

# Try importing our modules
try:
    from harmonization.rewards.music_theory_rewards import MusicTheoryRewards
    print("✅ MusicTheoryRewards imported successfully")
except Exception as e:
    print(f"❌ MusicTheoryRewards import failed: {e}")

try:
    from harmonization.core.rl_environment import HarmonizationEnvironment
    print("✅ HarmonizationEnvironment imported successfully")
except Exception as e:
    print(f"❌ HarmonizationEnvironment import failed: {e}")

print("🔍 Debug test complete!") 