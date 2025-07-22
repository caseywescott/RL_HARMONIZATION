#!/usr/bin/env python3
"""
Coconet-Based RL Training

This approach trains the RL model to score and improve Coconet harmonizations,
rather than generating harmonies from scratch. This addresses the issue that
the current RL model produces poor harmonization quality.

Training Process:
1. Generate harmonizations using Coconet
2. Score them using music theory rules
3. Train RL model to predict/improve these scores
4. Use RL model to optimize Coconet output
"""

import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import mido
import pretty_midi
from tunable_rl_harmonizer import TunableMusicTheoryRewards, TunableRLHarmonizer

class CoconetBasedRLTrainer:
    """Trainer that uses Coconet harmonizations as training data"""
    
    def __init__(self, coconet_server_url: str = "http://localhost:8000"):
        self.coconet_server_url = coconet_server_url
        self.reward_system = TunableMusicTheoryRewards()
        self.training_data = []
        
    def generate_coconet_training_data(self, 
                                     melody_files: List[str], 
                                     num_samples_per_melody: int = 5,
                                     temperature_range: Tuple[float, float] = (0.5, 1.5)) -> List[Dict]:
        """Generate training data using Coconet harmonizations"""
        
        print(f"🎵 Generating Coconet training data...")
        print(f"📁 Melody files: {len(melody_files)}")
        print(f"🎛️ Samples per melody: {num_samples_per_melody}")
        
        training_data = []
        
        for melody_file in melody_files:
            if not os.path.exists(melody_file):
                print(f"⚠️ Skipping {melody_file} - file not found")
                continue
                
            print(f"🎼 Processing {melody_file}...")
            
            # Load melody
            melody_notes = self.load_melody_from_midi(melody_file)
            if not melody_notes:
                continue
            
            # Generate multiple Coconet harmonizations with different temperatures
            for i in range(num_samples_per_melody):
                temperature = np.random.uniform(*temperature_range)
                
                try:
                    # Generate Coconet harmonization
                    coconet_harmony = self.generate_coconet_harmonization(melody_file, temperature)
                    
                    if coconet_harmony:
                        # Calculate music theory scores
                        scores = self.calculate_music_theory_scores(melody_notes, coconet_harmony)
                        
                        # Create training example
                        training_example = {
                            'melody_file': melody_file,
                            'melody_notes': melody_notes,
                            'coconet_harmony': coconet_harmony,
                            'temperature': temperature,
                            'music_theory_scores': scores,
                            'overall_score': np.mean(list(scores.values())),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        training_data.append(training_example)
                        print(f"   Sample {i+1}: Score = {training_example['overall_score']:.3f}")
                        
                except Exception as e:
                    print(f"   ❌ Error generating sample {i+1}: {e}")
        
        print(f"✅ Generated {len(training_data)} training examples")
        return training_data
    
    def load_melody_from_midi(self, midi_file: str) -> List[int]:
        """Extract melody notes from MIDI file"""
        try:
            mid = mido.MidiFile(midi_file)
            melody_notes = []
            
            for track in mid.tracks:
                current_time = 0
                for msg in track:
                    current_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        melody_notes.append(msg.note)
                        if len(melody_notes) >= 32:  # Limit length
                            break
                if melody_notes:
                    break
            
            return melody_notes[:32]  # Ensure consistent length
            
        except Exception as e:
            print(f"❌ Error loading melody from {midi_file}: {e}")
            return []
    
    def generate_coconet_harmonization(self, melody_file: str, temperature: float) -> List[int]:
        """Generate harmonization using Coconet server"""
        try:
            import requests
            
            # Prepare the request
            with open(melody_file, 'rb') as f:
                files = {'file': f}
                params = {
                    'method': 'coconet',
                    'temperature': temperature
                }
                
                # Send request to Coconet server
                response = requests.post(
                    f"{self.coconet_server_url}/harmonize",
                    files=files,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Save the response to a temporary file
                    temp_output = f"/tmp/coconet_output_{datetime.now().timestamp()}.mid"
                    with open(temp_output, 'wb') as f:
                        f.write(response.content)
                    
                    # Extract harmony notes from the output MIDI
                    harmony_notes = self.extract_harmony_from_midi(temp_output)
                    
                    # Clean up
                    os.remove(temp_output)
                    
                    return harmony_notes
                else:
                    print(f"❌ Coconet server error: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error calling Coconet server: {e}")
            return []
    
    def extract_harmony_from_midi(self, midi_file: str) -> List[int]:
        """Extract harmony notes from MIDI file (non-melody tracks)"""
        try:
            mid = mido.MidiFile(midi_file)
            harmony_notes = []
            
            # Skip the first track (usually melody) and get harmony from other tracks
            for track_idx, track in enumerate(mid.tracks[1:], 1):
                current_time = 0
                for msg in track:
                    current_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        harmony_notes.append(msg.note)
                        if len(harmony_notes) >= 32:  # Limit length
                            break
                if harmony_notes:
                    break
            
            return harmony_notes[:32]  # Ensure consistent length
            
        except Exception as e:
            print(f"❌ Error extracting harmony from {midi_file}: {e}")
            return []
    
    def calculate_music_theory_scores(self, melody_notes: List[int], harmony_notes: List[int]) -> Dict[str, float]:
        """Calculate comprehensive music theory scores"""
        scores = {}
        
        # Motion analysis
        scores['contrary_motion'] = self.calculate_contrary_motion_ratio(melody_notes, harmony_notes)
        scores['parallel_motion'] = self.calculate_parallel_motion_ratio(melody_notes, harmony_notes)
        scores['oblique_motion'] = self.calculate_oblique_motion_ratio(melody_notes, harmony_notes)
        
        # Harmonic analysis
        scores['consonance'] = self.calculate_consonance_ratio(melody_notes, harmony_notes)
        scores['voice_leading'] = self.calculate_voice_leading_quality(harmony_notes)
        scores['chord_progression'] = self.calculate_chord_progression_quality(melody_notes, harmony_notes)
        
        # Overall quality
        scores['overall_quality'] = np.mean([
            scores['contrary_motion'],
            scores['consonance'],
            scores['voice_leading'],
            scores['chord_progression']
        ])
        
        return scores
    
    def calculate_contrary_motion_ratio(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate ratio of contrary motion"""
        if len(melody_notes) < 2 or len(harmony_notes) < 2:
            return 0.0
        
        contrary_count = 0
        total_motions = 0
        
        for i in range(1, min(len(melody_notes), len(harmony_notes))):
            melody_dir = melody_notes[i] - melody_notes[i-1]
            harmony_dir = harmony_notes[i] - harmony_notes[i-1]
            
            if (melody_dir > 0 and harmony_dir < 0) or (melody_dir < 0 and harmony_dir > 0):
                contrary_count += 1
            total_motions += 1
        
        return contrary_count / total_motions if total_motions > 0 else 0.0
    
    def calculate_parallel_motion_ratio(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate ratio of parallel motion"""
        if len(melody_notes) < 2 or len(harmony_notes) < 2:
            return 0.0
        
        parallel_count = 0
        total_motions = 0
        
        for i in range(1, min(len(melody_notes), len(harmony_notes))):
            melody_dir = melody_notes[i] - melody_notes[i-1]
            harmony_dir = harmony_notes[i] - harmony_notes[i-1]
            
            if (melody_dir > 0 and harmony_dir > 0) or (melody_dir < 0 and harmony_dir < 0):
                parallel_count += 1
            total_motions += 1
        
        return parallel_count / total_motions if total_motions > 0 else 0.0
    
    def calculate_oblique_motion_ratio(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate ratio of oblique motion"""
        if len(melody_notes) < 2 or len(harmony_notes) < 2:
            return 0.0
        
        oblique_count = 0
        total_motions = 0
        
        for i in range(1, min(len(melody_notes), len(harmony_notes))):
            melody_dir = melody_notes[i] - melody_notes[i-1]
            harmony_dir = harmony_notes[i] - harmony_notes[i-1]
            
            if melody_dir == 0 or harmony_dir == 0:
                oblique_count += 1
            total_motions += 1
        
        return oblique_count / total_motions if total_motions > 0 else 0.0
    
    def calculate_consonance_ratio(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate ratio of consonant intervals"""
        if len(melody_notes) == 0 or len(harmony_notes) == 0:
            return 0.0
        
        consonant_count = 0
        total_intervals = 0
        
        for i in range(min(len(melody_notes), len(harmony_notes))):
            interval = abs(melody_notes[i] - harmony_notes[i]) % 12
            
            # Consonant intervals: unison, thirds, fourths, fifths, sixths
            if interval in [0, 3, 4, 7, 8]:
                consonant_count += 1
            total_intervals += 1
        
        return consonant_count / total_intervals if total_intervals > 0 else 0.0
    
    def calculate_voice_leading_quality(self, harmony_notes: List[int]) -> float:
        """Calculate voice leading quality (smoothness)"""
        if len(harmony_notes) < 2:
            return 0.0
        
        smooth_intervals = 0
        total_intervals = 0
        
        for i in range(1, len(harmony_notes)):
            interval = abs(harmony_notes[i] - harmony_notes[i-1])
            
            # Prefer small intervals (stepwise motion)
            if interval <= 2:
                smooth_intervals += 1
            elif interval <= 4:
                smooth_intervals += 0.7
            elif interval <= 7:
                smooth_intervals += 0.4
            else:
                smooth_intervals += 0.1
            
            total_intervals += 1
        
        return smooth_intervals / total_intervals if total_intervals > 0 else 0.0
    
    def calculate_chord_progression_quality(self, melody_notes: List[int], harmony_notes: List[int]) -> float:
        """Calculate chord progression quality"""
        if len(melody_notes) < 3 or len(harmony_notes) < 3:
            return 0.0
        
        # Simple chord quality assessment
        chord_qualities = []
        
        for i in range(min(len(melody_notes), len(harmony_notes))):
            # Create a simple chord (melody + harmony)
            chord_notes = [melody_notes[i], harmony_notes[i]]
            
            # Count consonant intervals within the chord
            consonant_intervals = 0
            total_intervals = 0
            
            for j in range(len(chord_notes)):
                for k in range(j+1, len(chord_notes)):
                    interval = abs(chord_notes[j] - chord_notes[k]) % 12
                    if interval in [0, 3, 4, 7, 8]:
                        consonant_intervals += 1
                    total_intervals += 1
            
            if total_intervals > 0:
                chord_qualities.append(consonant_intervals / total_intervals)
        
        return np.mean(chord_qualities) if chord_qualities else 0.0
    
    def train_rl_on_coconet_data(self, training_data: List[Dict], episodes: int = 5000) -> TunableRLHarmonizer:
        """Train RL model on Coconet harmonization data"""
        
        print(f"🎵 Training RL model on Coconet data...")
        print(f"📊 Training examples: {len(training_data)}")
        print(f"🎯 Episodes: {episodes}")
        
        # Create RL harmonizer
        harmonizer = TunableRLHarmonizer(self.reward_system)
        
        # Training variables
        episode_rewards = []
        best_reward = float('-inf')
        
        print(f"🚀 Starting training...")
        print(f"📝 Progress: ", end="", flush=True)
        
        for episode in range(episodes):
            # Select random training example
            example = np.random.choice(training_data)
            melody_notes = example['melody_notes']
            coconet_harmony = example['coconet_harmony']
            target_scores = example['music_theory_scores']
            
            # Generate RL harmonization
            rl_harmony = harmonizer.generate_harmonization(melody_notes)
            
            # Calculate RL scores
            rl_scores = self.calculate_music_theory_scores(melody_notes, rl_harmony)
            
            # Calculate reward based on improvement over Coconet
            improvement_reward = 0.0
            for metric in ['contrary_motion', 'consonance', 'voice_leading', 'chord_progression']:
                if metric in rl_scores and metric in target_scores:
                    improvement = rl_scores[metric] - target_scores[metric]
                    improvement_reward += improvement
            
            # Additional reward for overall quality
            if 'overall_quality' in rl_scores:
                improvement_reward += rl_scores['overall_quality'] * 2
            
            episode_rewards.append(improvement_reward)
            
            # Track best performance
            if improvement_reward > best_reward:
                best_reward = improvement_reward
            
            # Progress indicator
            if (episode + 1) % 500 == 0:
                recent_avg = np.mean(episode_rewards[-500:])
                print(f"\nEpisode {episode + 1}: Avg improvement = {recent_avg:.3f}, Best = {best_reward:.3f}")
                print("Progress: ", end="", flush=True)
            elif (episode + 1) % 100 == 0:
                print(".", end="", flush=True)
        
        # Calculate final statistics
        final_avg_reward = np.mean(episode_rewards[-1000:])
        final_std_reward = np.std(episode_rewards[-1000:])
        
        print(f"\n✅ Training completed!")
        print(f"📊 Final average improvement: {final_avg_reward:.3f}")
        print(f"🏆 Best improvement: {best_reward:.3f}")
        
        # Save training results
        training_results = {
            'training_examples': len(training_data),
            'episodes': episodes,
            'final_avg_reward': final_avg_reward,
            'final_std_reward': final_std_reward,
            'best_reward': best_reward,
            'episode_rewards': episode_rewards,
            'training_date': datetime.now().isoformat()
        }
        
        # Save model and results
        model_filename = f"coconet_trained_models/coconet_based_rl_model.json"
        results_filename = f"coconet_trained_models/training_results.json"
        
        os.makedirs("coconet_trained_models", exist_ok=True)
        
        harmonizer.save_model(model_filename)
        
        with open(results_filename, 'w') as f:
            json.dump(training_results, f, indent=2)
        
        print(f"💾 Model saved to: {model_filename}")
        print(f"📊 Results saved to: {results_filename}")
        
        return harmonizer
    
    def compare_coconet_vs_rl(self, test_melodies: List[str], trained_harmonizer: TunableRLHarmonizer):
        """Compare Coconet vs RL harmonization quality"""
        
        print(f"\n🎼 COMPARING COCONET VS RL HARMONIZATION")
        print("=" * 60)
        
        results = []
        
        for melody_file in test_melodies:
            if not os.path.exists(melody_file):
                continue
                
            print(f"🎵 Testing {melody_file}...")
            
            # Load melody
            melody_notes = self.load_melody_from_midi(melody_file)
            if not melody_notes:
                continue
            
            # Generate Coconet harmonization
            coconet_harmony = self.generate_coconet_harmonization(melody_file, temperature=0.8)
            coconet_scores = self.calculate_music_theory_scores(melody_notes, coconet_harmony)
            
            # Generate RL harmonization
            rl_harmony = trained_harmonizer.generate_harmonization(melody_notes)
            rl_scores = self.calculate_music_theory_scores(melody_notes, rl_harmony)
            
            # Calculate improvements
            improvements = {}
            for metric in coconet_scores:
                if metric in rl_scores:
                    improvements[metric] = rl_scores[metric] - coconet_scores[metric]
            
            result = {
                'melody_file': melody_file,
                'coconet_scores': coconet_scores,
                'rl_scores': rl_scores,
                'improvements': improvements,
                'overall_improvement': np.mean(list(improvements.values()))
            }
            
            results.append(result)
            
            print(f"   Coconet overall: {coconet_scores.get('overall_quality', 0):.3f}")
            print(f"   RL overall: {rl_scores.get('overall_quality', 0):.3f}")
            print(f"   Improvement: {result['overall_improvement']:.3f}")
        
        # Summary
        if results:
            avg_improvement = np.mean([r['overall_improvement'] for r in results])
            print(f"\n📊 SUMMARY:")
            print(f"   Average improvement: {avg_improvement:.3f}")
            print(f"   Tests performed: {len(results)}")
            
            if avg_improvement > 0:
                print(f"   ✅ RL model improves over Coconet!")
            else:
                print(f"   ⚠️ RL model needs more training")
        
        return results

def main():
    """Main function for Coconet-based RL training"""
    print("🎵 COCONET-BASED RL TRAINING")
    print("=" * 60)
    print("This approach trains the RL model on Coconet harmonizations")
    print("to improve harmonization quality over the current RL approach")
    
    # Initialize trainer
    trainer = CoconetBasedRLTrainer()
    
    # Define melody files for training
    melody_files = [
        "realms2_harmonized.mid",
        "realms2_idea.midi",
        # Add more melody files as needed
    ]
    
    # Filter existing files
    existing_melody_files = [f for f in melody_files if os.path.exists(f)]
    
    if not existing_melody_files:
        print("❌ No melody files found for training!")
        print("Please ensure the melody files exist in the current directory")
        return
    
    print(f"📁 Found {len(existing_melody_files)} melody files for training")
    
    # Generate Coconet training data
    training_data = trainer.generate_coconet_training_data(
        existing_melody_files,
        num_samples_per_melody=3,
        temperature_range=(0.5, 1.2)
    )
    
    if not training_data:
        print("❌ No training data generated!")
        print("Please ensure the Coconet server is running and accessible")
        return
    
    # Train RL model on Coconet data
    trained_harmonizer = trainer.train_rl_on_coconet_data(training_data, episodes=3000)
    
    # Compare Coconet vs RL
    comparison_results = trainer.compare_coconet_vs_rl(existing_melody_files, trained_harmonizer)
    
    print(f"\n✅ Coconet-based RL training complete!")
    print(f"🎛️ The trained model should now produce better harmonizations")
    print(f"📊 Check the comparison results above for performance analysis")

if __name__ == "__main__":
    main() 