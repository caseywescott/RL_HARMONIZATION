#!/usr/bin/env python3
"""
Tunable RL Harmonizer - Dynamic Music Theory Rule Adjustment

This implementation allows real-time tuning of RL model behavior based on
music theory rules, similar to Figure 2 of "Style Modeling for N-Part Automatic Harmonization".

Features:
- Dynamic weight adjustment for music theory rules
- Real-time style switching
- Controllable contrary vs parallel motion
- Adjustable harmonic complexity
- Voice leading optimization
"""

import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import mido
import pretty_midi

class TunableMusicTheoryRewards:
    """Reward system with dynamically adjustable weights for music theory rules"""
    
    def __init__(self):
        # Default weights (can be adjusted in real-time)
        self.weights = {
            # Motion types
            'contrary_motion': 1.0,
            'parallel_motion': 0.3,
            'oblique_motion': 0.7,
            
            # Harmonic rules
            'consonance': 1.0,
            'dissonance': 0.2,
            'chord_progression': 0.8,
            'cadence': 1.2,
            
            # Voice leading
            'voice_leading': 0.9,
            'voice_crossing': 0.1,
            'voice_spacing': 0.8,
            
            # Style characteristics
            'harmonic_complexity': 0.6,
            'melodic_interest': 0.7,
            'rhythmic_variety': 0.5,
            
            # Advanced rules
            'preparation_resolution': 0.8,
            'suspension': 0.6,
            'passing_tones': 0.4,
            'neighbor_tones': 0.4
        }
        
        # Style presets
        self.style_presets = {
            'classical': {
                'contrary_motion': 1.2,
                'parallel_motion': 0.2,
                'consonance': 1.1,
                'voice_leading': 1.0,
                'chord_progression': 0.9,
                'harmonic_complexity': 0.7
            },
            'jazz': {
                'contrary_motion': 0.8,
                'parallel_motion': 0.6,
                'consonance': 0.7,
                'dissonance': 0.8,
                'harmonic_complexity': 1.2,
                'melodic_interest': 1.1
            },
            'pop': {
                'contrary_motion': 0.5,
                'parallel_motion': 0.8,
                'consonance': 1.0,
                'chord_progression': 1.1,
                'harmonic_complexity': 0.4,
                'melodic_interest': 0.8
            },
            'baroque': {
                'contrary_motion': 1.3,
                'parallel_motion': 0.1,
                'consonance': 1.0,
                'voice_leading': 1.2,
                'counterpoint': 1.1,
                'harmonic_complexity': 0.8
            }
        }
    
    def set_weights(self, weights: Dict[str, float]):
        """Set custom weights for music theory rules"""
        self.weights.update(weights)
        print(f"🎛️ Updated weights: {weights}")
    
    def set_style(self, style_name: str):
        """Set weights based on a predefined style"""
        if style_name in self.style_presets:
            self.set_weights(self.style_presets[style_name])
            print(f"🎼 Applied {style_name} style weights")
        else:
            print(f"❌ Unknown style: {style_name}")
            print(f"Available styles: {list(self.style_presets.keys())}")
    
    def calculate_contrary_motion_reward(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate reward for contrary motion between melody and harmony"""
        if len(melody_notes) < 2 or len(harmony_notes) < 2:
            return 0.0
        
        contrary_motion_count = 0
        total_motions = 0
        
        for i in range(1, min(len(melody_notes), len(harmony_notes))):
            melody_direction = melody_notes[i] - melody_notes[i-1]
            harmony_direction = harmony_notes[i] - harmony_notes[i-1]
            
            # Contrary motion: opposite directions
            if (melody_direction > 0 and harmony_direction < 0) or \
               (melody_direction < 0 and harmony_direction > 0):
                contrary_motion_count += 1
            total_motions += 1
        
        if total_motions == 0:
            return 0.0
        
        contrary_ratio = contrary_motion_count / total_motions
        return contrary_ratio * self.weights['contrary_motion']
    
    def calculate_parallel_motion_reward(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate reward for parallel motion (usually penalized)"""
        if len(melody_notes) < 2 or len(harmony_notes) < 2:
            return 0.0
        
        parallel_motion_count = 0
        total_motions = 0
        
        for i in range(1, min(len(melody_notes), len(harmony_notes))):
            melody_direction = melody_notes[i] - melody_notes[i-1]
            harmony_direction = harmony_notes[i] - harmony_notes[i-1]
            
            # Parallel motion: same direction
            if (melody_direction > 0 and harmony_direction > 0) or \
               (melody_direction < 0 and harmony_direction < 0):
                parallel_motion_count += 1
            total_motions += 1
        
        if total_motions == 0:
            return 0.0
        
        parallel_ratio = parallel_motion_count / total_motions
        return parallel_ratio * self.weights['parallel_motion']
    
    def calculate_consonance_reward(self, melody_note: int, harmony_note: int) -> float:
        """Calculate reward for consonant intervals"""
        interval = abs(melody_note - harmony_note) % 12
        
        # Consonant intervals
        if interval in [0, 3, 4, 7, 8]:  # Unison, minor/major third, perfect fourth/fifth, minor sixth
            return self.weights['consonance']
        # Dissonant intervals
        elif interval in [1, 2, 5, 6, 9, 10, 11]:  # Seconds, tritone, sevenths
            return self.weights['dissonance']
        else:
            return 0.5
    
    def calculate_voice_leading_reward(self, prev_harmony: int, current_harmony: int) -> float:
        """Calculate reward for smooth voice leading"""
        interval = abs(current_harmony - prev_harmony)
        
        # Prefer small intervals (stepwise motion)
        if interval <= 2:
            return self.weights['voice_leading']
        elif interval <= 4:
            return self.weights['voice_leading'] * 0.7
        elif interval <= 7:
            return self.weights['voice_leading'] * 0.4
        else:
            return self.weights['voice_leading'] * 0.1
    
    def calculate_chord_progression_reward(self, chord_notes: List[int]) -> float:
        """Calculate reward for good chord progressions"""
        if len(chord_notes) < 3:
            return 0.0
        
        # Simple chord quality assessment
        intervals = []
        for i in range(len(chord_notes)):
            for j in range(i+1, len(chord_notes)):
                interval = abs(chord_notes[i] - chord_notes[j]) % 12
                intervals.append(interval)
        
        # Count consonant intervals
        consonant_count = sum(1 for interval in intervals if interval in [0, 3, 4, 7, 8])
        total_intervals = len(intervals)
        
        if total_intervals == 0:
            return 0.0
        
        consonance_ratio = consonant_count / total_intervals
        return consonance_ratio * self.weights['chord_progression']
    
    def calculate_total_reward(self, 
                             melody_notes: List[int], 
                             harmony_notes: List[int],
                             chord_notes: List[int] = None) -> float:
        """Calculate total reward based on all music theory rules"""
        total_reward = 0.0
        
        # Motion rewards
        total_reward += self.calculate_contrary_motion_reward(melody_notes, harmony_notes)
        total_reward += self.calculate_parallel_motion_reward(melody_notes, harmony_notes)
        
        # Harmonic rewards
        if len(melody_notes) > 0 and len(harmony_notes) > 0:
            total_reward += self.calculate_consonance_reward(melody_notes[-1], harmony_notes[-1])
        
        # Voice leading rewards
        if len(harmony_notes) >= 2:
            total_reward += self.calculate_voice_leading_reward(harmony_notes[-2], harmony_notes[-1])
        
        # Chord progression rewards
        if chord_notes:
            total_reward += self.calculate_chord_progression_reward(chord_notes)
        
        return total_reward

class TunableRLHarmonizer:
    """RL harmonizer with tunable music theory rules"""
    
    def __init__(self, reward_system: TunableMusicTheoryRewards):
        self.reward_system = reward_system
        self.q_table = {}  # Simple Q-table for demonstration
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # Exploration rate
        
        # Harmonization state
        self.current_melody = []
        self.current_harmony = []
        self.current_chord = []
        
        print("🎵 Tunable RL Harmonizer initialized")
        print(f"🎛️ Current weights: {self.reward_system.weights}")
    
    def set_style(self, style_name: str):
        """Set harmonization style"""
        self.reward_system.set_style(style_name)
    
    def adjust_weights(self, weight_updates: Dict[str, float]):
        """Dynamically adjust music theory rule weights"""
        self.reward_system.set_weights(weight_updates)
    
    def get_state_key(self, melody_note: int, context_notes: List[int]) -> str:
        """Create state key for Q-table"""
        context_str = "_".join(map(str, context_notes[-3:]))  # Last 3 context notes
        return f"{melody_note}_{context_str}"
    
    def choose_action(self, state: str, available_actions: List[int]) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            # Exploration: random action
            return np.random.choice(available_actions)
        else:
            # Exploitation: best action
            if state in self.q_table:
                q_values = [self.q_table[state].get(action, 0.0) for action in available_actions]
                best_action_idx = np.argmax(q_values)
                return available_actions[best_action_idx]
            else:
                return np.random.choice(available_actions)
    
    def update_q_value(self, state: str, action: int, reward: float, next_state: str):
        """Update Q-value using Q-learning"""
        if state not in self.q_table:
            self.q_table[state] = {}
        
        current_q = self.q_table[state].get(action, 0.0)
        
        # Q-learning update
        if next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        else:
            max_next_q = 0.0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def generate_harmonization(self, melody_notes: List[int], 
                             style: str = None,
                             custom_weights: Dict[str, float] = None) -> List[int]:
        """Generate harmonization with specified style or custom weights"""
        
        # Apply style or custom weights
        if style:
            self.set_style(style)
        elif custom_weights:
            self.adjust_weights(custom_weights)
        
        print(f"🎼 Generating harmonization...")
        print(f"🎛️ Active weights: {self.reward_system.weights}")
        
        harmonization = []
        context_notes = []
        
        for i, melody_note in enumerate(melody_notes):
            # Create state
            state = self.get_state_key(melody_note, context_notes)
            
            # Available harmony actions (simplified)
            available_actions = [
                melody_note - 3,   # Minor third below
                melody_note - 7,   # Perfect fifth below
                melody_note + 5,   # Perfect fourth above
                melody_note - 10,  # Minor seventh below
                melody_note - 12,  # Octave below
            ]
            
            # Filter valid MIDI notes
            available_actions = [note for note in available_actions if 21 <= note <= 108]
            
            # Choose action
            harmony_note = self.choose_action(state, available_actions)
            
            # Calculate reward
            test_melody = melody_notes[:i+1]
            test_harmony = harmonization + [harmony_note]
            test_chord = [melody_note, harmony_note]
            
            reward = self.reward_system.calculate_total_reward(
                test_melody, test_harmony, test_chord
            )
            
            # Update Q-value
            next_context = context_notes + [harmony_note]
            next_state = self.get_state_key(
                melody_notes[i+1] if i+1 < len(melody_notes) else melody_note,
                next_context
            )
            self.update_q_value(state, harmony_note, reward, next_state)
            
            # Store result
            harmonization.append(harmony_note)
            context_notes.append(harmony_note)
            
            # Keep context manageable
            if len(context_notes) > 5:
                context_notes = context_notes[-5:]
        
        print(f"✅ Generated harmonization with {len(harmonization)} notes")
        return harmonization
    
    def save_model(self, filename: str):
        """Save the trained model"""
        model_data = {
            'q_table': self.q_table,
            'weights': self.reward_system.weights,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'save_date': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        print(f"💾 Model saved to: {filename}")
    
    def load_model(self, filename: str):
        """Load a trained model"""
        with open(filename, 'r') as f:
            model_data = json.load(f)
        
        self.q_table = model_data['q_table']
        self.reward_system.weights = model_data['weights']
        self.learning_rate = model_data.get('learning_rate', 0.1)
        self.discount_factor = model_data.get('discount_factor', 0.9)
        self.epsilon = model_data.get('epsilon', 0.1)
        
        print(f"📂 Model loaded from: {filename}")
        print(f"🎛️ Weights: {self.reward_system.weights}")

def create_tunable_harmonizer() -> TunableRLHarmonizer:
    """Create and configure a tunable RL harmonizer"""
    reward_system = TunableMusicTheoryRewards()
    harmonizer = TunableRLHarmonizer(reward_system)
    return harmonizer

def demonstrate_tunable_harmonization():
    """Demonstrate the tunable harmonization capabilities"""
    print("🎵 TURNABLE RL HARMONIZATION DEMONSTRATION")
    print("=" * 60)
    
    # Create harmonizer
    harmonizer = create_tunable_harmonizer()
    
    # Sample melody (C major scale)
    melody_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C, D, E, F, G, A, B, C
    
    print(f"🎼 Input melody: {melody_notes}")
    print(f"🎵 Melody notes: {[chr(ord('A') + (note % 12)) for note in melody_notes]}")
    
    # Demonstrate different styles
    styles = ['classical', 'jazz', 'pop', 'baroque']
    
    for style in styles:
        print(f"\n🎼 Generating {style.upper()} style harmonization...")
        
        # Generate harmonization
        harmony_notes = harmonizer.generate_harmonization(melody_notes, style=style)
        
        # Analyze results
        print(f"   Harmony notes: {harmony_notes}")
        print(f"   Harmony names: {[chr(ord('A') + (note % 12)) for note in harmony_notes]}")
        
        # Calculate motion statistics
        contrary_count = 0
        parallel_count = 0
        total_motions = 0
        
        for i in range(1, min(len(melody_notes), len(harmony_notes))):
            melody_dir = melody_notes[i] - melody_notes[i-1]
            harmony_dir = harmony_notes[i] - harmony_notes[i-1]
            
            if (melody_dir > 0 and harmony_dir < 0) or (melody_dir < 0 and harmony_dir > 0):
                contrary_count += 1
            elif (melody_dir > 0 and harmony_dir > 0) or (melody_dir < 0 and harmony_dir < 0):
                parallel_count += 1
            total_motions += 1
        
        if total_motions > 0:
            print(f"   Contrary motion: {contrary_count}/{total_motions} ({contrary_count/total_motions*100:.1f}%)")
            print(f"   Parallel motion: {parallel_count}/{total_motions} ({parallel_count/total_motions*100:.1f}%)")
    
    # Demonstrate custom weight adjustment
    print(f"\n🎛️ DEMONSTRATING CUSTOM WEIGHT ADJUSTMENT")
    print("-" * 40)
    
    # High contrary motion preference
    high_contrary_weights = {
        'contrary_motion': 2.0,
        'parallel_motion': 0.1,
        'consonance': 1.0
    }
    
    print(f"🎛️ Setting high contrary motion weights: {high_contrary_weights}")
    harmony_notes = harmonizer.generate_harmonization(
        melody_notes, custom_weights=high_contrary_weights
    )
    
    print(f"   Result: {harmony_notes}")
    
    # High parallel motion preference
    high_parallel_weights = {
        'contrary_motion': 0.2,
        'parallel_motion': 1.5,
        'consonance': 1.0
    }
    
    print(f"🎛️ Setting high parallel motion weights: {high_parallel_weights}")
    harmony_notes = harmonizer.generate_harmonization(
        melody_notes, custom_weights=high_parallel_weights
    )
    
    print(f"   Result: {harmony_notes}")
    
    print(f"\n✅ Demonstration complete!")
    print(f"🎛️ You can now tune the harmonizer with any combination of weights")

if __name__ == "__main__":
    demonstrate_tunable_harmonization() 