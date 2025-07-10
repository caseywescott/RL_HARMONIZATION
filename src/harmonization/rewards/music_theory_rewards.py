"""
Tunable music theory reward functions for RL harmonization.

This module implements the reward functions from RL Tuner with adjustable weights
to allow different musical styles and preferences.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set

class MusicTheoryRewards:
    """
    Tunable music theory reward system.
    
    Implements the reward functions from RL Tuner with configurable weights
    to allow different musical styles and preferences.
    """
    
    def __init__(self, reward_weights: Optional[Dict[str, float]] = None):
        """
        Initialize the reward system.
        
        Args:
            reward_weights: Dictionary of reward weights for different rules
        """
        # Default weights (from RL Tuner paper)
        self.default_weights = {
            'avoid_repetition': 0.1,
            'prefer_arpeggios': 0.1,
            'prefer_scale_degrees': 0.1,
            'prefer_tonic': 0.1,
            'prefer_leading_tone': 0.1,
            'prefer_resolution': 0.1,
            'prefer_strong_beats': 0.1,
            'prefer_weak_beats': 0.1,
            'prefer_common_pitches': 0.1,
            'prefer_common_intervals': 0.1,
            'prefer_common_durations': 0.1,
            'prefer_common_rhythms': 0.1,
            'prefer_common_chords': 0.1,
            'prefer_common_progressions': 0.1,
            'prefer_common_voice_leading': 0.1,
            'prefer_common_harmony': 0.1,
            'prefer_common_melody': 0.1,
            'prefer_common_counterpoint': 0.1,
            'prefer_common_form': 0.1,
            'prefer_common_style': 0.1
        }
        
        self.weights = reward_weights or self.default_weights.copy()
        
        # Predefined style presets
        self.style_presets = {
            'classical': {
                'prefer_common_chords': 0.2,
                'prefer_common_progressions': 0.2,
                'prefer_common_voice_leading': 0.2,
                'prefer_common_harmony': 0.2,
                'prefer_common_counterpoint': 0.2
            },
            'jazz': {
                'prefer_arpeggios': 0.2,
                'prefer_common_pitches': 0.2,
                'prefer_common_intervals': 0.2,
                'prefer_common_chords': 0.2,
                'prefer_common_progressions': 0.2
            },
            'pop': {
                'prefer_common_pitches': 0.3,
                'prefer_common_chords': 0.3,
                'prefer_common_progressions': 0.3,
                'prefer_common_rhythms': 0.1
            },
            'baroque': {
                'prefer_common_counterpoint': 0.3,
                'prefer_common_voice_leading': 0.3,
                'prefer_common_harmony': 0.2,
                'prefer_common_form': 0.2
            }
        }
        
        # Musical constants
        self.CHROMATIC_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
        self.MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
        
        # Common chord progressions (Roman numerals)
        self.COMMON_PROGRESSIONS = [
            [1, 4, 5, 1],  # I-IV-V-I
            [1, 6, 4, 5],  # I-vi-IV-V
            [2, 5, 1],     # ii-V-I
            [1, 5, 6, 4],  # I-V-vi-IV
            [1, 4, 6, 5],  # I-IV-vi-V
        ]
        
        # Common intervals (in semitones)
        self.CONSONANT_INTERVALS = {0, 3, 4, 7, 8, 12}  # Unison, minor/major third, perfect fourth/fifth, octave
        self.DISSONANT_INTERVALS = {1, 2, 5, 6, 9, 10, 11}  # Minor second, major second, tritone, etc.
    
    def set_style_preset(self, style: str):
        """
        Set reward weights based on a predefined style preset.
        
        Args:
            style: Style name ('classical', 'jazz', 'pop', 'baroque')
        """
        if style in self.style_presets:
            self.weights.update(self.style_presets[style])
            print(f"✅ Applied {style} style preset")
        else:
            print(f"❌ Unknown style: {style}")
    
    def set_custom_weights(self, weights: Dict[str, float]):
        """
        Set custom reward weights.
        
        Args:
            weights: Dictionary of reward weights
        """
        self.weights.update(weights)
        print("✅ Applied custom reward weights")
    
    def calculate_reward_simple(self, 
                              current_sequence: list,
                              action: np.ndarray,
                              melody_note: Optional[int] = None) -> float:
        """
        Calculate a simplified reward for an action.
        
        Args:
            current_sequence: Current sequence as list of note dictionaries
            action: Action taken (array of pitch indices)
            melody_note: Current melody note (optional)
            
        Returns:
            Total reward value
        """
        total_reward = 0.0
        
        # Convert action to MIDI pitches
        action_pitches = [pitch_idx + 21 for pitch_idx in action]
        
        # Basic harmony rewards
        rewards = {
            'avoid_repetition': self._avoid_repetition_simple(current_sequence, action_pitches),
            'prefer_common_intervals': self._prefer_common_intervals_simple(action_pitches, melody_note),
            'prefer_common_chords': self._prefer_common_chords_simple(action_pitches),
            'prefer_scale_degrees': self._prefer_scale_degrees_simple(action_pitches),
            'prefer_voice_leading': self._prefer_voice_leading_simple(current_sequence, action_pitches)
        }
        
        # Apply weights and sum
        for rule_name, reward_value in rewards.items():
            if rule_name in self.weights:
                total_reward += self.weights[rule_name] * reward_value
        
        return total_reward
    
    def _avoid_repetition_simple(self, current_sequence: list, action_pitches: list) -> float:
        """
        Simple reward for avoiding repetitive patterns.
        """
        if len(current_sequence) == 0:
            return 0.0
        
        # Get recent pitches
        recent_pitches = [note['pitch'] for note in current_sequence[-4:]]
        
        # Check for immediate repetition
        if recent_pitches and action_pitches:
            if recent_pitches[-1] in action_pitches:
                return -0.5
        
        return 0.1  # Small positive reward for variety
    
    def _prefer_common_intervals_simple(self, action_pitches: list, melody_note: Optional[int]) -> float:
        """
        Simple reward for consonant intervals with melody.
        """
        if not melody_note or not action_pitches:
            return 0.0
        
        total_reward = 0.0
        
        for harmony_pitch in action_pitches:
            interval = abs(harmony_pitch - melody_note) % 12
            if interval in self.CONSONANT_INTERVALS:
                total_reward += 0.2
            elif interval in self.DISSONANT_INTERVALS:
                total_reward -= 0.1
        
        return total_reward / len(action_pitches) if action_pitches else 0.0
    
    def _prefer_common_chords_simple(self, action_pitches: list) -> float:
        """
        Simple reward for common chord structures.
        """
        if len(action_pitches) < 3:
            return 0.0
        
        # Check if pitches form a major or minor chord
        pitches_mod12 = [p % 12 for p in action_pitches]
        pitches_mod12.sort()
        
        # Major chord: root, major third (4 semitones), perfect fifth (7 semitones)
        if len(pitches_mod12) >= 3:
            root = pitches_mod12[0]
            third = pitches_mod12[1]
            fifth = pitches_mod12[2]
            
            # Check for major chord
            if (third - root) % 12 == 4 and (fifth - root) % 12 == 7:
                return 0.3
            # Check for minor chord
            elif (third - root) % 12 == 3 and (fifth - root) % 12 == 7:
                return 0.3
        
        return 0.0
    
    def _prefer_scale_degrees_simple(self, action_pitches: list) -> float:
        """
        Simple reward for scale degrees.
        """
        if not action_pitches:
            return 0.0
        
        total_reward = 0.0
        
        for pitch in action_pitches:
            pitch_class = pitch % 12
            if pitch_class in self.MAJOR_SCALE:
                total_reward += 0.1
        
        return total_reward / len(action_pitches)
    
    def _prefer_voice_leading_simple(self, current_sequence: list, action_pitches: list) -> float:
        """
        Simple reward for smooth voice leading.
        """
        if len(current_sequence) == 0 or not action_pitches:
            return 0.0
        
        # Get recent harmony notes
        recent_harmony = []
        for note in current_sequence[-len(action_pitches):]:
            if note['voice'] > 0:  # Harmony voices
                recent_harmony.append(note['pitch'])
        
        if len(recent_harmony) != len(action_pitches):
            return 0.0
        
        total_reward = 0.0
        
        # Check for smooth voice leading (small intervals)
        for old_pitch, new_pitch in zip(recent_harmony, action_pitches):
            interval = abs(new_pitch - old_pitch)
            if interval <= 2:  # Stepwise motion
                total_reward += 0.2
            elif interval <= 7:  # Reasonable leap
                total_reward += 0.1
            else:  # Large leap
                total_reward -= 0.1
        
        return total_reward / len(action_pitches)
    
    # Keep the original methods for compatibility (they can be implemented later)
    def calculate_reward(self, current_sequence, action, next_sequence):
        """Original reward calculation method (placeholder)."""
        return self.calculate_reward_simple([], action, None)
    
    def _avoid_repetition_reward(self, current, next_seq):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_arpeggios_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_scale_degrees_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_tonic_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_leading_tone_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_resolution_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_strong_beats_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_weak_beats_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_pitches_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_intervals_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_durations_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_rhythms_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_chords_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_progressions_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_voice_leading_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_harmony_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_melody_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_counterpoint_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_form_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0
    
    def _prefer_common_style_reward(self, sequence):
        """Original method (placeholder)."""
        return 0.0 