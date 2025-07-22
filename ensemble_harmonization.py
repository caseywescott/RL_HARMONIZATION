#!/usr/bin/env python3
"""
Ensemble Harmonization System

Combines multiple harmonization approaches:
1. Coconet Neural Network
2. Trained RL Rules Model
3. Style-specific models
4. Rule-based fallback

Uses voting and weighted averaging for optimal results.
"""

import numpy as np
import mido
import json
import os
from datetime import datetime
import sys
from typing import Dict, List, Tuple, Optional

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

class EnsembleHarmonizer:
    """Ensemble harmonization system combining multiple approaches"""
    
    def __init__(self, coconet_available: bool = True):
        self.coconet_available = coconet_available
        self.models = {}
        self.weights = {}
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize all available harmonization models"""
        print("🎵 Initializing Ensemble Harmonization System")
        
        # 1. Coconet Neural Network (if available)
        if self.coconet_available:
            try:
                from harmonization.core.coconet_wrapper import CoconetWrapper
                self.models['coconet'] = CoconetWrapper("coconet-64layers-128filters")
                self.weights['coconet'] = 0.35
                print("✅ Coconet neural model loaded")
            except Exception as e:
                print(f"❌ Coconet model not available: {e}")
                self.coconet_available = False
        
        # 2. Trained RL Rules Model
        try:
            self.models['rl_rules'] = self.load_rl_rules_model()
            self.weights['rl_rules'] = 0.30
            print("✅ RL rules model loaded")
        except Exception as e:
            print(f"❌ RL rules model not available: {e}")
        
        # 3. Style-specific models
        style_models = self.load_style_models()
        for style_name, model in style_models.items():
            self.models[f'style_{style_name}'] = model
            self.weights[f'style_{style_name}'] = 0.15
            print(f"✅ {style_name} style model loaded")
        
        # 4. Rule-based fallback
        self.models['rule_based'] = self.create_rule_based_model()
        self.weights['rule_based'] = 0.20
        print("✅ Rule-based fallback model loaded")
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        for model_name in self.weights:
            self.weights[model_name] /= total_weight
        
        print(f"🎛️ Ensemble weights: {self.weights}")
    
    def load_rl_rules_model(self):
        """Load the trained RL rules model"""
        try:
            with open("simple_contrary_motion_model_metadata.json", "r") as f:
                metadata = json.load(f)
            return metadata
        except FileNotFoundError:
            return None
    
    def load_style_models(self):
        """Load all available style-specific models"""
        style_models = {}
        style_dir = "style_models"
        
        if os.path.exists(style_dir):
            for style_name in os.listdir(style_dir):
                style_path = os.path.join(style_dir, style_name)
                if os.path.isdir(style_path):
                    metadata_file = os.path.join(style_path, "model_metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file, "r") as f:
                            style_models[style_name] = json.load(f)
        
        return style_models
    
    def create_rule_based_model(self):
        """Create a simple rule-based harmonization model"""
        return {
            'type': 'rule_based',
            'description': 'Simple music theory rules'
        }
    
    def harmonize_with_coconet(self, melody_notes: List[int]) -> Optional[Dict]:
        """Generate harmonization using Coconet"""
        if not self.coconet_available or 'coconet' not in self.models:
            return None
        
        try:
            # Convert melody to NoteSequence format
            import note_seq
            from note_seq import NoteSequence
            
            sequence = NoteSequence()
            sequence.ticks_per_quarter = 480
            
            for i, note in enumerate(melody_notes):
                note_seq_note = sequence.notes.add()
                note_seq_note.pitch = note
                note_seq_note.start_time = i * 0.5  # Half second per note
                note_seq_note.end_time = (i + 1) * 0.5
                note_seq_note.velocity = 100
                note_seq_note.instrument = 0
            
            # Generate harmonization
            harmonized_sequence = self.models['coconet'].generate_completion(
                primer_sequence=sequence,
                temperature=1.0,
                num_steps=len(melody_notes)
            )
            
            # Convert back to our format
            harmonization = {
                'soprano': [],
                'alto': [],
                'tenor': [],
                'bass': []
            }
            
            # Extract notes from harmonized sequence
            for note in harmonized_sequence.notes:
                if note.instrument < 4:  # Limit to 4 voices
                    voice_names = ['soprano', 'alto', 'tenor', 'bass']
                    voice = voice_names[note.instrument]
                    
                    harmonization[voice].append({
                        'note': note.pitch,
                        'start_time': int(note.start_time * 480),
                        'duration': int((note.end_time - note.start_time) * 480),
                        'velocity': note.velocity
                    })
            
            return harmonization
            
        except Exception as e:
            print(f"❌ Coconet harmonization failed: {e}")
            return None
    
    def harmonize_with_rl_rules(self, melody_notes: List[int]) -> Optional[Dict]:
        """Generate harmonization using trained RL rules"""
        if 'rl_rules' not in self.models:
            return None
        
        try:
            # Initialize reward system
            reward_system = MusicTheoryRewards()
            
            # Create environment
            env = HarmonizationEnvironment(
                coconet_wrapper=None,
                reward_system=reward_system,
                max_steps=len(melody_notes),
                num_voices=3,
                melody_sequence=melody_notes
            )
            
            # Generate harmonization
            observation = env.reset()
            harmonization = {
                'soprano': [],
                'alto': [],
                'tenor': [],
                'bass': []
            }
            
            for step in range(len(melody_notes)):
                action = env.action_space.sample()
                observation, reward, done, info = env.step(action)
                
                # Add melody
                harmonization['soprano'].append({
                    'note': melody_notes[step],
                    'start_time': step * 480,
                    'duration': 480,
                    'velocity': 100
                })
                
                # Add harmony
                voices = ['alto', 'tenor', 'bass']
                for voice_idx, voice in enumerate(voices):
                    pitch = action[voice_idx] + 21
                    harmonization[voice].append({
                        'note': pitch,
                        'start_time': step * 480,
                        'duration': 480,
                        'velocity': 80
                    })
            
            return harmonization
            
        except Exception as e:
            print(f"❌ RL rules harmonization failed: {e}")
            return None
    
    def harmonize_with_style(self, melody_notes: List[int], style_name: str) -> Optional[Dict]:
        """Generate harmonization using style-specific model"""
        model_key = f'style_{style_name}'
        if model_key not in self.models:
            return None
        
        try:
            # Get style weights
            weights = self.models[model_key]['reward_weights']
            
            # Initialize reward system with style weights
            reward_system = MusicTheoryRewards()
            reward_system.set_custom_weights(weights)
            
            # Create environment
            env = HarmonizationEnvironment(
                coconet_wrapper=None,
                reward_system=reward_system,
                max_steps=len(melody_notes),
                num_voices=3,
                melody_sequence=melody_notes
            )
            
            # Generate harmonization
            observation = env.reset()
            harmonization = {
                'soprano': [],
                'alto': [],
                'tenor': [],
                'bass': []
            }
            
            for step in range(len(melody_notes)):
                action = env.action_space.sample()
                observation, reward, done, info = env.step(action)
                
                # Add melody
                harmonization['soprano'].append({
                    'note': melody_notes[step],
                    'start_time': step * 480,
                    'duration': 480,
                    'velocity': 100
                })
                
                # Add harmony
                voices = ['alto', 'tenor', 'bass']
                for voice_idx, voice in enumerate(voices):
                    pitch = action[voice_idx] + 21
                    harmonization[voice].append({
                        'note': pitch,
                        'start_time': step * 480,
                        'duration': 480,
                        'velocity': 80
                    })
            
            return harmonization
            
        except Exception as e:
            print(f"❌ {style_name} style harmonization failed: {e}")
            return None
    
    def harmonize_with_rules(self, melody_notes: List[int]) -> Dict:
        """Generate harmonization using simple rules"""
        harmonization = {
            'soprano': [],
            'alto': [],
            'tenor': [],
            'bass': []
        }
        
        for i, melody_note in enumerate(melody_notes):
            # Add melody
            harmonization['soprano'].append({
                'note': melody_note,
                'start_time': i * 480,
                'duration': 480,
                'velocity': 100
            })
            
            # Simple rule-based harmony
            alto_note = melody_note - 3  # Minor third
            tenor_note = melody_note - 7  # Perfect fifth
            bass_note = melody_note - 12  # Octave below
            
            # Ensure notes are in valid range
            alto_note = max(50, min(69, alto_note))
            tenor_note = max(40, min(62, tenor_note))
            bass_note = max(36, min(60, bass_note))
            
            harmonization['alto'].append({
                'note': alto_note,
                'start_time': i * 480,
                'duration': 480,
                'velocity': 80
            })
            
            harmonization['tenor'].append({
                'note': tenor_note,
                'start_time': i * 480,
                'duration': 480,
                'velocity': 80
            })
            
            harmonization['bass'].append({
                'note': bass_note,
                'start_time': i * 480,
                'duration': 480,
                'velocity': 80
            })
        
        return harmonization
    
    def ensemble_harmonize(self, melody_notes: List[int], 
                          style_preference: str = None) -> Dict:
        """Generate harmonization using ensemble approach"""
        print(f"🎵 Generating ensemble harmonization for {len(melody_notes)} notes")
        
        harmonizations = {}
        scores = {}
        
        # Generate harmonizations with each model
        for model_name in self.models:
            print(f"🤖 Using {model_name}...")
            
            if model_name == 'coconet':
                harmonizations[model_name] = self.harmonize_with_coconet(melody_notes)
            elif model_name == 'rl_rules':
                harmonizations[model_name] = self.harmonize_with_rl_rules(melody_notes)
            elif model_name.startswith('style_'):
                style_name = model_name.replace('style_', '')
                harmonizations[model_name] = self.harmonize_with_style(melody_notes, style_name)
            elif model_name == 'rule_based':
                harmonizations[model_name] = self.harmonize_with_rules(melody_notes)
            
            # Score the harmonization
            if harmonizations[model_name]:
                scores[model_name] = self.score_harmonization(harmonizations[model_name], melody_notes)
            else:
                scores[model_name] = 0.0
        
        # Weighted ensemble combination
        final_harmonization = self.combine_harmonizations(harmonizations, scores, style_preference)
        
        return final_harmonization
    
    def score_harmonization(self, harmonization: Dict, melody_notes: List[int]) -> float:
        """Score a harmonization based on music theory criteria"""
        score = 0.0
        
        # Check harmonic coherence
        for i in range(len(melody_notes)):
            if i < len(harmonization['soprano']):
                soprano = harmonization['soprano'][i]['note']
                alto = harmonization['alto'][i]['note'] if i < len(harmonization['alto']) else soprano - 3
                tenor = harmonization['tenor'][i]['note'] if i < len(harmonization['tenor']) else alto - 4
                bass = harmonization['bass'][i]['note'] if i < len(harmonization['bass']) else tenor - 4
                
                # Check for consonant intervals
                notes = [soprano, alto, tenor, bass]
                consonant_intervals = 0
                for j in range(len(notes)):
                    for k in range(j+1, len(notes)):
                        interval = abs(notes[j] - notes[k]) % 12
                        if interval in [0, 3, 4, 7, 8]:
                            consonant_intervals += 1
                
                score += consonant_intervals / 6.0  # Normalize
        
        return score / max(len(melody_notes), 1)
    
    def combine_harmonizations(self, harmonizations: Dict, scores: Dict, 
                              style_preference: str = None) -> Dict:
        """Combine multiple harmonizations using weighted voting"""
        print(f"🎛️ Combining harmonizations with scores: {scores}")
        
        # Adjust weights based on scores and style preference
        adjusted_weights = {}
        for model_name in self.weights:
            base_weight = self.weights[model_name]
            score_multiplier = scores.get(model_name, 0.5)
            
            # Boost weight for preferred style
            if style_preference and model_name == f'style_{style_preference}':
                score_multiplier *= 1.5
            
            adjusted_weights[model_name] = base_weight * score_multiplier
        
        # Normalize weights
        total_weight = sum(adjusted_weights.values())
        for model_name in adjusted_weights:
            adjusted_weights[model_name] /= total_weight
        
        print(f"🎛️ Adjusted weights: {adjusted_weights}")
        
        # Combine harmonizations
        final_harmonization = {
            'soprano': [],
            'alto': [],
            'tenor': [],
            'bass': []
        }
        
        # For each note position, combine notes from all models
        max_length = max(len(h.get('soprano', [])) for h in harmonizations.values() if h)
        
        for i in range(max_length):
            # Collect notes from all models for this position
            soprano_notes = []
            alto_notes = []
            tenor_notes = []
            bass_notes = []
            
            for model_name, harmonization in harmonizations.items():
                if harmonization and i < len(harmonization['soprano']):
                    weight = adjusted_weights[model_name]
                    
                    soprano_notes.append((harmonization['soprano'][i]['note'], weight))
                    if i < len(harmonization['alto']):
                        alto_notes.append((harmonization['alto'][i]['note'], weight))
                    if i < len(harmonization['tenor']):
                        tenor_notes.append((harmonization['tenor'][i]['note'], weight))
                    if i < len(harmonization['bass']):
                        bass_notes.append((harmonization['bass'][i]['note'], weight))
            
            # Weighted average for each voice
            if soprano_notes:
                final_soprano = int(sum(note * weight for note, weight in soprano_notes) / 
                                  sum(weight for _, weight in soprano_notes))
                final_harmonization['soprano'].append({
                    'note': final_soprano,
                    'start_time': i * 480,
                    'duration': 480,
                    'velocity': 100
                })
            
            if alto_notes:
                final_alto = int(sum(note * weight for note, weight in alto_notes) / 
                               sum(weight for _, weight in alto_notes))
                final_harmonization['alto'].append({
                    'note': final_alto,
                    'start_time': i * 480,
                    'duration': 480,
                    'velocity': 80
                })
            
            if tenor_notes:
                final_tenor = int(sum(note * weight for note, weight in tenor_notes) / 
                                sum(weight for _, weight in tenor_notes))
                final_harmonization['tenor'].append({
                    'note': final_tenor,
                    'start_time': i * 480,
                    'duration': 480,
                    'velocity': 80
                })
            
            if bass_notes:
                final_bass = int(sum(note * weight for note, weight in bass_notes) / 
                               sum(weight for _, weight in bass_notes))
                final_harmonization['bass'].append({
                    'note': final_bass,
                    'start_time': i * 480,
                    'duration': 480,
                    'velocity': 80
                })
        
        return final_harmonization

def main():
    """Example usage of ensemble harmonization"""
    print("🎵 Ensemble Harmonization System")
    print("=" * 50)
    
    # Initialize ensemble
    ensemble = EnsembleHarmonizer(coconet_available=True)
    
    # Example melody
    melody_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
    
    # Generate ensemble harmonization
    harmonization = ensemble.ensemble_harmonize(melody_notes, style_preference='classical')
    
    print(f"\n✅ Ensemble harmonization generated!")
    print(f"📊 Voice ranges:")
    for voice in ['soprano', 'alto', 'tenor', 'bass']:
        notes = [note['note'] for note in harmonization[voice]]
        if notes:
            print(f"  {voice.title()}: {min(notes)}-{max(notes)}")
    
    return harmonization

if __name__ == "__main__":
    main() 