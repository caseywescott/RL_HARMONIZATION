"""
RL Environment for harmonization system.

This module provides a gym-compatible environment that wraps the Coconet model
and reward system for reinforcement learning.
"""

import gym
import numpy as np
from typing import Tuple, Dict, Any, Optional
import mido
from mido import MidiFile, Message, MidiTrack

from ..rewards.music_theory_rewards import MusicTheoryRewards

class HarmonizationEnvironment(gym.Env):
    """
    RL Environment for n-part harmonization.
    
    This environment provides a gym-compatible interface for training
    harmonization agents using Coconet and tunable music theory rewards.
    """
    
    def __init__(self, 
                 coconet_wrapper=None,
                 reward_system: Optional[MusicTheoryRewards] = None,
                 max_steps: int = 32,
                 num_voices: int = 4,
                 melody_sequence: Optional[list] = None):
        """
        Initialize the harmonization environment.
        
        Args:
            coconet_wrapper: Coconet model wrapper (optional for now)
            reward_system: Music theory reward system
            max_steps: Maximum number of steps per episode
            num_voices: Number of voices in the harmonization
            melody_sequence: Optional melody sequence to harmonize
        """
        super().__init__()
        
        self.coconet_wrapper = coconet_wrapper
        self.reward_system = reward_system or MusicTheoryRewards()
        self.max_steps = max_steps
        self.num_voices = num_voices
        self.melody_sequence = melody_sequence
        
        # Define action and observation spaces
        # Action space: pitch selection for each voice (88 pitches per voice)
        self.action_space = gym.spaces.MultiDiscrete([88] * num_voices)
        
        # Observation space: current harmony state + melody context
        # (time_steps, pitches, voices + melody) + additional features
        self.observation_space = gym.spaces.Box(
            low=0, high=1, 
            shape=(max_steps, 88, num_voices + 2),  # +1 for melody, +1 for features
            dtype=np.float32
        )
        
        # Environment state
        self.current_step = 0
        self.current_sequence = []
        self.episode_rewards = []
        self.melody_context = []
        
        # Musical constants
        self.MIDI_MIN_PITCH = 21  # A0
        self.MIDI_MAX_PITCH = 108  # C8
        self.NOTE_DURATION = 0.25  # 16th note duration
        
    def reset(self) -> np.ndarray:
        """
        Reset the environment for a new episode.
        
        Returns:
            Initial observation
        """
        self.current_step = 0
        self.current_sequence = []
        self.episode_rewards = []
        
        # Initialize melody context if provided
        if self.melody_sequence:
            self.melody_context = self.melody_sequence[:self.max_steps]
        else:
            # Generate random melody context
            self.melody_context = self._generate_random_melody()
        
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
        new_notes = self._action_to_notes(action)
        
        # Add new notes to sequence
        self.current_sequence.extend(new_notes)
        
        # Calculate reward
        reward = self.reward_system.calculate_reward_simple(
            self.current_sequence, 
            action, 
            self.melody_context[self.current_step] if self.current_step < len(self.melody_context) else None
        )
        
        # Update state
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
            'average_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0.0,
            'melody_note': self.melody_context[self.current_step - 1] if self.current_step > 0 else None
        }
        
        return observation, reward, done, info
    
    def _action_to_notes(self, action: np.ndarray) -> list:
        """
        Convert action array to list of note dictionaries.
        
        Args:
            action: Array of pitch selections for each voice
            
        Returns:
            List of note dictionaries
        """
        notes = []
        current_time = self.current_step * self.NOTE_DURATION
        
        for voice_idx, pitch_idx in enumerate(action):
            # Convert pitch index to MIDI pitch
            midi_pitch = pitch_idx + self.MIDI_MIN_PITCH
            
            # Create note dictionary
            note = {
                'pitch': midi_pitch,
                'start_time': current_time,
                'end_time': current_time + self.NOTE_DURATION,
                'velocity': 80,
                'voice': voice_idx
            }
            notes.append(note)
        
        return notes
    
    def _get_observation(self) -> np.ndarray:
        """
        Get current observation.
        
        Returns:
            Observation array
        """
        # Create observation array
        obs = np.zeros((self.max_steps, 88, self.num_voices + 2), dtype=np.float32)
        
        # Fill in current sequence data
        for note in self.current_sequence:
            time_step = int(note['start_time'] / self.NOTE_DURATION)
            pitch_idx = note['pitch'] - self.MIDI_MIN_PITCH
            voice_idx = note['voice']
            
            if 0 <= time_step < self.max_steps and 0 <= pitch_idx < 88:
                obs[time_step, pitch_idx, voice_idx] = 1.0
        
        # Fill in melody context
        for step in range(min(len(self.melody_context), self.max_steps)):
            if self.melody_context[step] is not None:
                melody_pitch = self.melody_context[step]
                pitch_idx = melody_pitch - self.MIDI_MIN_PITCH
                if 0 <= pitch_idx < 88:
                    obs[step, pitch_idx, self.num_voices] = 1.0
        
        # Add additional features
        for step in range(self.max_steps):
            obs[step, :, self.num_voices + 1] = step / self.max_steps  # Normalized step
        
        return obs
    
    def _generate_random_melody(self) -> list:
        """
        Generate a random melody for training.
        
        Returns:
            List of MIDI pitches
        """
        melody = []
        # C major scale pitches (C4 to C5)
        scale_pitches = [60, 62, 64, 65, 67, 69, 71, 72]
        
        for _ in range(self.max_steps):
            pitch = np.random.choice(scale_pitches)
            melody.append(pitch)
        
        return melody
    
    def render(self, mode='human'):
        """
        Render the current state.
        
        Args:
            mode: Rendering mode
        """
        if mode == 'human':
            print(f"Step: {self.current_step}/{self.max_steps}")
            print(f"Current sequence length: {len(self.current_sequence)}")
            print(f"Episode rewards: {self.episode_rewards}")
            if self.melody_context and self.current_step < len(self.melody_context):
                print(f"Melody note: {self.melody_context[self.current_step]}")
    
    def get_final_sequence(self) -> list:
        """
        Get the final sequence from the episode.
        
        Returns:
            Final sequence as list of note dictionaries
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
    
    def set_melody_sequence(self, melody_sequence: list):
        """
        Set a specific melody sequence to harmonize.
        
        Args:
            melody_sequence: List of MIDI pitches
        """
        self.melody_sequence = melody_sequence
        self.melody_context = melody_sequence[:self.max_steps] 