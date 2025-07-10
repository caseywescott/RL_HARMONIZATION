"""
Tunable music theory reward functions for RL harmonization.

This module implements the reward functions from RL Tuner with adjustable weights
to allow different musical styles and preferences.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import note_seq
from note_seq import NoteSequence, constants

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
    
    def calculate_reward(self, 
                        current_sequence: NoteSequence,
                        action: int,
                        next_sequence: NoteSequence) -> float:
        """
        Calculate the total reward for an action.
        
        Args:
            current_sequence: Current state sequence
            action: Action taken
            next_sequence: Resulting sequence after action
            
        Returns:
            Total reward value
        """
        total_reward = 0.0
        
        # Calculate individual reward components
        rewards = {
            'avoid_repetition': self._avoid_repetition_reward(current_sequence, next_sequence),
            'prefer_arpeggios': self._prefer_arpeggios_reward(next_sequence),
            'prefer_scale_degrees': self._prefer_scale_degrees_reward(next_sequence),
            'prefer_tonic': self._prefer_tonic_reward(next_sequence),
            'prefer_leading_tone': self._prefer_leading_tone_reward(next_sequence),
            'prefer_resolution': self._prefer_resolution_reward(next_sequence),
            'prefer_strong_beats': self._prefer_strong_beats_reward(next_sequence),
            'prefer_weak_beats': self._prefer_weak_beats_reward(next_sequence),
            'prefer_common_pitches': self._prefer_common_pitches_reward(next_sequence),
            'prefer_common_intervals': self._prefer_common_intervals_reward(next_sequence),
            'prefer_common_durations': self._prefer_common_durations_reward(next_sequence),
            'prefer_common_rhythms': self._prefer_common_rhythms_reward(next_sequence),
            'prefer_common_chords': self._prefer_common_chords_reward(next_sequence),
            'prefer_common_progressions': self._prefer_common_progressions_reward(next_sequence),
            'prefer_common_voice_leading': self._prefer_common_voice_leading_reward(next_sequence),
            'prefer_common_harmony': self._prefer_common_harmony_reward(next_sequence),
            'prefer_common_melody': self._prefer_common_melody_reward(next_sequence),
            'prefer_common_counterpoint': self._prefer_common_counterpoint_reward(next_sequence),
            'prefer_common_form': self._prefer_common_form_reward(next_sequence),
            'prefer_common_style': self._prefer_common_style_reward(next_sequence)
        }
        
        # Apply weights and sum
        for rule_name, reward_value in rewards.items():
            if rule_name in self.weights:
                total_reward += self.weights[rule_name] * reward_value
        
        return total_reward
    
    def _avoid_repetition_reward(self, current: NoteSequence, next_seq: NoteSequence) -> float:
        """
        Reward for avoiding repetitive patterns.
        
        Penalizes immediate repetition of the same pitch or pattern.
        """
        if len(current.notes) == 0 or len(next_seq.notes) == 0:
            return 0.0
        
        # Get recent notes from current sequence
        recent_notes = [note.pitch for note in current.notes[-4:]]  # Last 4 notes
        new_notes = [note.pitch for note in next_seq.notes[-4:]]    # New notes
        
        # Check for immediate repetition
        if len(recent_notes) > 0 and len(new_notes) > 0:
            if recent_notes[-1] == new_notes[-1]:
                return -1.0
        
        # Check for pattern repetition
        if len(recent_notes) >= 2 and len(new_notes) >= 2:
            if recent_notes[-2:] == new_notes[-2:]:
                return -0.5
        
        return 0.0
    
    def _prefer_arpeggios_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for arpeggio patterns.
        
        Rewards sequences that follow chord arpeggios.
        """
        if len(sequence.notes) < 3:
            return 0.0
        
        # Group notes by time to identify chords
        time_groups = {}
        for note in sequence.notes:
            time_key = round(note.start_time, 2)
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(note.pitch)
        
        arpeggio_score = 0.0
        chord_count = 0
        
        for pitches in time_groups.values():
            if len(pitches) >= 3:
                # Check if pitches form a chord (triad or seventh)
                pitches = sorted(pitches)
                intervals = [pitches[i+1] - pitches[i] for i in range(len(pitches)-1)]
                
                # Major triad: 4, 3 semitones
                # Minor triad: 3, 4 semitones
                # Diminished triad: 3, 3 semitones
                # Augmented triad: 4, 4 semitones
                
                if len(intervals) >= 2:
                    if (intervals[0] in [3, 4] and intervals[1] in [3, 4]):
                        arpeggio_score += 1.0
                    chord_count += 1
        
        return arpeggio_score / max(chord_count, 1)
    
    def _prefer_scale_degrees_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for using scale degrees.
        
        Rewards sequences that use notes from the diatonic scale.
        """
        if len(sequence.notes) == 0:
            return 0.0
        
        # Assume C major for simplicity (can be made key-aware)
        key_center = 60  # C4
        major_scale_pitches = [(key_center + interval) % 12 for interval in self.MAJOR_SCALE]
        
        scale_notes = 0
        total_notes = len(sequence.notes)
        
        for note in sequence.notes:
            pitch_class = note.pitch % 12
            if pitch_class in major_scale_pitches:
                scale_notes += 1
        
        return scale_notes / total_notes
    
    def _prefer_tonic_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for tonic notes.
        
        Rewards sequences that emphasize the tonic (root note of the key).
        """
        if len(sequence.notes) == 0:
            return 0.0
        
        # Assume C major, tonic is C
        tonic_pitch = 60  # C4
        tonic_notes = 0
        total_notes = len(sequence.notes)
        
        for note in sequence.notes:
            if note.pitch % 12 == tonic_pitch % 12:  # Same pitch class
                tonic_notes += 1
        
        return tonic_notes / total_notes
    
    def _prefer_leading_tone_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for leading tone resolution.
        
        Rewards sequences that use leading tone (7th scale degree) resolving to tonic.
        """
        if len(sequence.notes) < 2:
            return 0.0
        
        # In C major, leading tone is B (pitch class 11)
        leading_tone_pitch = 11  # B
        tonic_pitch = 0         # C
        
        resolution_count = 0
        total_leading_tones = 0
        
        for i in range(len(sequence.notes) - 1):
            current_pitch = sequence.notes[i].pitch % 12
            next_pitch = sequence.notes[i + 1].pitch % 12
            
            if current_pitch == leading_tone_pitch:
                total_leading_tones += 1
                if next_pitch == tonic_pitch:
                    resolution_count += 1
        
        if total_leading_tones == 0:
            return 0.0
        
        return resolution_count / total_leading_tones
    
    def _prefer_resolution_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for harmonic resolution.
        
        Rewards sequences that resolve dissonances to consonances.
        """
        if len(sequence.notes) < 2:
            return 0.0
        
        resolution_score = 0.0
        total_resolutions = 0
        
        # Group notes by time to analyze harmonic intervals
        time_groups = {}
        for note in sequence.notes:
            time_key = round(note.start_time, 2)
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(note.pitch)
        
        time_keys = sorted(time_groups.keys())
        
        for i in range(len(time_keys) - 1):
            current_chord = time_groups[time_keys[i]]
            next_chord = time_groups[time_keys[i + 1]]
            
            # Check if dissonance resolves to consonance
            for pitch1 in current_chord:
                for pitch2 in current_chord:
                    if pitch1 != pitch2:
                        interval = abs(pitch1 - pitch2) % 12
                        if interval in self.DISSONANT_INTERVALS:
                            # Check if it resolves in the next chord
                            for pitch3 in next_chord:
                                for pitch4 in next_chord:
                                    if pitch3 != pitch4:
                                        next_interval = abs(pitch3 - pitch4) % 12
                                        if next_interval in self.CONSONANT_INTERVALS:
                                            resolution_score += 1.0
                                            break
                                if resolution_score > 0:
                                    break
                            total_resolutions += 1
        
        return resolution_score / max(total_resolutions, 1)
    
    def _prefer_strong_beats_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for strong beat emphasis.
        
        Rewards sequences that emphasize strong beats (1 and 3 in 4/4 time).
        """
        if len(sequence.notes) == 0:
            return 0.0
        
        strong_beat_score = 0.0
        total_notes = len(sequence.notes)
        
        for note in sequence.notes:
            # Convert time to beat position
            beat_position = (note.start_time * 4) % 4  # Assuming 4/4 time
            
            # Strong beats are at positions 0 and 2
            if beat_position < 0.1 or (1.9 < beat_position < 2.1):
                strong_beat_score += 1.0
        
        return strong_beat_score / total_notes
    
    def _prefer_weak_beats_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for weak beat treatment.
        
        Rewards sequences that use appropriate note values on weak beats.
        """
        if len(sequence.notes) == 0:
            return 0.0
        
        weak_beat_score = 0.0
        total_weak_beats = 0
        
        for note in sequence.notes:
            beat_position = (note.start_time * 4) % 4
            
            # Weak beats are at positions 1 and 3
            if (0.9 < beat_position < 1.1) or (2.9 < beat_position < 3.1):
                total_weak_beats += 1
                # Prefer shorter notes on weak beats
                note_duration = note.end_time - note.start_time
                if note_duration <= 0.5:  # Quarter note or shorter
                    weak_beat_score += 1.0
        
        return weak_beat_score / max(total_weak_beats, 1)
    
    def _prefer_common_pitches_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for common pitch usage.
        
        Rewards sequences that use commonly used pitches in the genre.
        """
        if len(sequence.notes) == 0:
            return 0.0
        
        # Common pitches in Western music (C, D, E, F, G, A, B)
        common_pitches = {60, 62, 64, 65, 67, 69, 71}  # C4 to B4
        common_notes = 0
        total_notes = len(sequence.notes)
        
        for note in sequence.notes:
            if note.pitch in common_pitches:
                common_notes += 1
        
        return common_notes / total_notes
    
    def _prefer_common_intervals_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for common interval usage.
        
        Rewards sequences that use common melodic intervals.
        """
        if len(sequence.notes) < 2:
            return 0.0
        
        # Common melodic intervals (in semitones)
        common_intervals = {0, 1, 2, 3, 4, 5, 7, 12}  # Unison, minor/major second, minor/major third, perfect fourth, perfect fifth, octave
        
        common_interval_count = 0
        total_intervals = 0
        
        for i in range(len(sequence.notes) - 1):
            interval = abs(sequence.notes[i + 1].pitch - sequence.notes[i].pitch)
            if interval in common_intervals:
                common_interval_count += 1
            total_intervals += 1
        
        return common_interval_count / total_intervals
    
    def _prefer_common_durations_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for common note durations.
        
        Rewards sequences that use common note values.
        """
        if len(sequence.notes) == 0:
            return 0.0
        
        # Common durations in 16th note units
        common_durations = {1, 2, 4, 8}  # 16th, 8th, quarter, half notes
        
        common_duration_count = 0
        total_notes = len(sequence.notes)
        
        for note in sequence.notes:
            duration = (note.end_time - note.start_time) * 4  # Convert to 16th notes
            if duration in common_durations:
                common_duration_count += 1
        
        return common_duration_count / total_notes
    
    def _prefer_common_rhythms_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for common rhythmic patterns.
        
        Rewards sequences that use common rhythmic patterns.
        """
        if len(sequence.notes) < 4:
            return 0.0
        
        # Extract rhythm pattern (simplified)
        rhythm_pattern = []
        for note in sequence.notes:
            duration = (note.end_time - note.start_time) * 4  # 16th notes
            rhythm_pattern.append(duration)
        
        # Check for common patterns (simplified)
        # This could be expanded with more sophisticated pattern matching
        if len(rhythm_pattern) >= 4:
            # Check for repeated patterns
            if rhythm_pattern[:2] == rhythm_pattern[2:4]:
                return 1.0
        
        return 0.0
    
    def _prefer_common_chords_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for common chord usage.
        
        Rewards sequences that use common chord types.
        """
        if len(sequence.notes) < 3:
            return 0.0
        
        # Group notes by time to identify chords
        time_groups = {}
        for note in sequence.notes:
            time_key = round(note.start_time, 2)
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(note.pitch)
        
        chord_score = 0.0
        chord_count = 0
        
        for pitches in time_groups.values():
            if len(pitches) >= 3:
                # Check if pitches form a common chord
                pitches = sorted(pitches)
                root = pitches[0] % 12
                
                # Check for major triad (root, major third, perfect fifth)
                major_third = (root + 4) % 12
                perfect_fifth = (root + 7) % 12
                
                if major_third in [p % 12 for p in pitches] and perfect_fifth in [p % 12 for p in pitches]:
                    chord_score += 1.0
                
                chord_count += 1
        
        return chord_score / max(chord_count, 1)
    
    def _prefer_common_progressions_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for common chord progressions.
        
        Rewards sequences that follow common chord progressions.
        """
        # This is a simplified implementation
        # A full implementation would require chord analysis and progression detection
        return 0.0
    
    def _prefer_common_voice_leading_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for good voice leading.
        
        Rewards sequences with smooth voice leading (small intervals between voices).
        """
        if len(sequence.notes) < 2:
            return 0.0
        
        # Group notes by voice/instrument
        voices = {}
        for note in sequence.notes:
            voice = note.instrument
            if voice not in voices:
                voices[voice] = []
            voices[voice].append(note)
        
        voice_leading_score = 0.0
        total_movements = 0
        
        for voice_notes in voices.values():
            if len(voice_notes) < 2:
                continue
            
            for i in range(len(voice_notes) - 1):
                interval = abs(voice_notes[i + 1].pitch - voice_notes[i].pitch)
                # Prefer small intervals (stepwise motion)
                if interval <= 2:  # Minor/major second
                    voice_leading_score += 1.0
                elif interval <= 4:  # Minor/major third
                    voice_leading_score += 0.5
                total_movements += 1
        
        return voice_leading_score / max(total_movements, 1)
    
    def _prefer_common_harmony_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for harmonic coherence.
        
        Rewards sequences with coherent harmonic structure.
        """
        # This combines several harmonic aspects
        chord_reward = self._prefer_common_chords_reward(sequence)
        voice_leading_reward = self._prefer_common_voice_leading_reward(sequence)
        resolution_reward = self._prefer_resolution_reward(sequence)
        
        return (chord_reward + voice_leading_reward + resolution_reward) / 3
    
    def _prefer_common_melody_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for melodic coherence.
        
        Rewards sequences with coherent melodic structure.
        """
        # This combines several melodic aspects
        scale_reward = self._prefer_scale_degrees_reward(sequence)
        interval_reward = self._prefer_common_intervals_reward(sequence)
        tonic_reward = self._prefer_tonic_reward(sequence)
        
        return (scale_reward + interval_reward + tonic_reward) / 3
    
    def _prefer_common_counterpoint_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for good counterpoint.
        
        Rewards sequences that follow counterpoint rules.
        """
        if len(sequence.notes) < 4:
            return 0.0
        
        # Basic counterpoint rules
        # 1. Avoid parallel fifths and octaves
        # 2. Prefer contrary motion
        # 3. Avoid dissonances on strong beats
        
        counterpoint_score = 0.0
        total_checks = 0
        
        # Group notes by time
        time_groups = {}
        for note in sequence.notes:
            time_key = round(note.start_time, 2)
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(note)
        
        time_keys = sorted(time_groups.keys())
        
        for i in range(len(time_keys) - 1):
            current_notes = time_groups[time_keys[i]]
            next_notes = time_groups[time_keys[i + 1]]
            
            if len(current_notes) >= 2 and len(next_notes) >= 2:
                # Check for parallel fifths/octaves
                for j in range(len(current_notes)):
                    for k in range(j + 1, len(current_notes)):
                        interval1 = abs(current_notes[j].pitch - current_notes[k].pitch) % 12
                        if interval1 in [0, 7]:  # Unison or perfect fifth
                            # Check if same interval occurs in next chord
                            for m in range(len(next_notes)):
                                for n in range(m + 1, len(next_notes)):
                                    interval2 = abs(next_notes[m].pitch - next_notes[n].pitch) % 12
                                    if interval2 == interval1:
                                        counterpoint_score -= 1.0  # Penalty for parallel motion
                                    else:
                                        counterpoint_score += 0.5  # Reward for contrary motion
                                    total_checks += 1
        
        return counterpoint_score / max(total_checks, 1)
    
    def _prefer_common_form_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for formal coherence.
        
        Rewards sequences with coherent formal structure.
        """
        # This is a placeholder for formal analysis
        # Could include phrase structure, repetition, contrast, etc.
        return 0.0
    
    def _prefer_common_style_reward(self, sequence: NoteSequence) -> float:
        """
        Reward for style consistency.
        
        Rewards sequences that maintain consistent style characteristics.
        """
        # This combines multiple style-related rewards
        harmony_reward = self._prefer_common_harmony_reward(sequence)
        melody_reward = self._prefer_common_melody_reward(sequence)
        rhythm_reward = self._prefer_common_rhythms_reward(sequence)
        
        return (harmony_reward + melody_reward + rhythm_reward) / 3 