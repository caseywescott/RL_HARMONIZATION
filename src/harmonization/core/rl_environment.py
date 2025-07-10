"""
RL Environment for harmonization system.

This module provides a gym-compatible environment that wraps the Coconet model
and reward system for reinforcement learning.
"""

import gym
import numpy as np
from typing import Tuple, Dict, Any, Optional
import note_seq
from note_seq import NoteSequence

from ..rewards.music_theory_rewards import MusicTheoryRewards

class HarmonizationEnvironment(gym.Env):
    """
    RL Environment for n-part harmonization.
    
    This environment provides a gym-compatible interface for training
    harmonization agents using Coconet and tunable music theory rewards.
    """
    
    def __init__(self, 
                 coconet_wrapper,
                 reward_system: MusicTheoryRewards,
                 max_steps: int = 32,
                 num_voices: int = 4):
        """
        Initialize the harmonization environment.
        
        Args:
            coconet_wrapper: Coconet model wrapper
            reward_system: Music theory reward system
            max_steps: Maximum number of steps per episode
            num_voices: Number of voices in the harmonization
        """
        super().__init__()
        
        self.coconet_wrapper = coconet_wrapper
        self.reward_system = reward_system
        self.max_steps = max_steps
        self.num_voices = num_voices
        
        # Define action and observation spaces
        # Action space: pitch selection for each voice (88 pitches per voice)
        self.action_space = gym.spaces.MultiDiscrete([88] * num_voices)
        
        # Observation space: current harmony state
        # (time_steps, pitches, voices) + additional features
        self.observation_space = gym.spaces.Box(
            low=0, high=1, 
            shape=(max_steps, 88, num_voices + 1),  # +1 for additional features
            dtype=np.float32
        )
        
        # Environment state
        self.current_step = 0
        self.current_sequence = None
        self.episode_rewards = []
        
    def reset(self) -> np.ndarray:
        """
        Reset the environment for a new episode.
        
        Returns:
            Initial observation
        """
        self.current_step = 0
        self.current_sequence = NoteSequence()
        self.current_sequence.ticks_per_quarter = 220
        self.episode_rewards = []
        
        # Return initial observation
        return self._get_observation()
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Take a step in the environment.
        
        Args:
            action: Array of pitch selections for each voice
            
        Returns:
            (observation, reward, done, info)
        """
        # Convert action to notes
        next_sequence = self._action_to_sequence(action)
        
        # Calculate reward
        reward = self.reward_system.calculate_reward(
            self.current_sequence, 
            action, 
            next_sequence
        )
        
        # Update state
        self.current_sequence = next_sequence
        self.current_step += 1
        self.episode_rewards.append(reward)
        
        # Check if episode is done
        done = self.current_step >= self.max_steps
        
        # Get observation
        observation = self._get_observation()
        
        # Additional info
        info = {
            'step': self.current_step,
            'total_reward': sum(self.episode_rewards),
            'average_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0.0
        }
        
        return observation, reward, done, info
    
    def _action_to_sequence(self, action: np.ndarray) -> NoteSequence:
        """
        Convert action array to NoteSequence.
        
        Args:
            action: Array of pitch selections for each voice
            
        Returns:
            NoteSequence with the new notes added
        """
        # Create a copy of current sequence
        new_sequence = NoteSequence()
        new_sequence.CopyFrom(self.current_sequence)
        
        # Add new notes for each voice
        current_time = self.current_step * 0.25  # 16th note quantization
        
        for voice_idx, pitch_idx in enumerate(action):
            # Convert pitch index to MIDI pitch
            midi_pitch = pitch_idx + 21  # MIDI pitch 21 (A0) to 108 (C8)
            
            # Create note
            note = new_sequence.notes.add()
            note.pitch = midi_pitch
            note.start_time = current_time
            note.end_time = current_time + 0.25  # 16th note duration
            note.velocity = 80
            note.instrument = voice_idx
        
        return new_sequence
    
    def _get_observation(self) -> np.ndarray:
        """
        Get current observation.
        
        Returns:
            Observation array
        """
        # Create observation array
        obs = np.zeros((self.max_steps, 88, self.num_voices + 1), dtype=np.float32)
        
        # Fill in current sequence data
        for note in self.current_sequence.notes:
            time_step = int(note.start_time * 4)  # 16th note quantization
            pitch_idx = note.pitch - 21  # MIDI pitch offset
            voice_idx = note.instrument
            
            if 0 <= time_step < self.max_steps and 0 <= pitch_idx < 88:
                obs[time_step, pitch_idx, voice_idx] = 1.0
        
        # Add additional features (e.g., current step, voice ranges, etc.)
        for step in range(self.max_steps):
            obs[step, :, self.num_voices] = step / self.max_steps  # Normalized step
        
        return obs
    
    def render(self, mode='human'):
        """
        Render the current state.
        
        Args:
            mode: Rendering mode
        """
        if mode == 'human':
            print(f"Step: {self.current_step}/{self.max_steps}")
            print(f"Current sequence length: {len(self.current_sequence.notes)}")
            print(f"Episode rewards: {self.episode_rewards}")
    
    def get_final_sequence(self) -> NoteSequence:
        """
        Get the final sequence from the episode.
        
        Returns:
            Final NoteSequence
        """
        return self.current_sequence
    
    def set_reward_weights(self, weights: Dict[str, float]):
        """
        Update reward weights.
        
        Args:
            weights: New reward weights
        """
        self.reward_system.set_custom_weights(weights)
    
    def set_style_preset(self, style: str):
        """
        Set reward style preset.
        
        Args:
            style: Style name
        """
        self.reward_system.set_style_preset(style) 