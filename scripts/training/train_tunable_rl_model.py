#!/usr/bin/env python3
"""
Train Tunable RL Model with Music Theory Rules

This script implements the training approach shown in Figure 2 of 
"Style Modeling for N-Part Automatic Harmonization", allowing you to:

1. Train the RL model with different music theory rule weights
2. Compare performance across different style configurations
3. Analyze the impact of rule weights on harmonization quality
4. Save and load trained models with specific weight configurations
"""

import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from tunable_rl_harmonizer import TunableMusicTheoryRewards, TunableRLHarmonizer

class TunableRLTrainer:
    """Trainer for tunable RL harmonization models"""
    
    def __init__(self):
        self.training_results = {}
        self.model_configurations = {}
        
    def create_training_melodies(self) -> List[List[int]]:
        """Create diverse training melodies"""
        melodies = []
        
        # C major scale
        melodies.append([60, 62, 64, 65, 67, 69, 71, 72])  # C, D, E, F, G, A, B, C
        
        # G major scale
        melodies.append([67, 69, 71, 72, 74, 76, 78, 79])  # G, A, B, C, D, E, F#, G
        
        # F major scale
        melodies.append([65, 67, 69, 70, 72, 74, 76, 77])  # F, G, A, Bb, C, D, E, F
        
        # Chromatic line
        melodies.append([60, 61, 62, 63, 64, 65, 66, 67])  # C, C#, D, D#, E, F, F#, G
        
        # Arpeggio patterns
        melodies.append([60, 64, 67, 72, 67, 64, 60])      # C major arpeggio
        
        # Melodic patterns
        melodies.append([60, 62, 64, 62, 60, 67, 65, 64])  # Melodic pattern
        
        return melodies
    
    def define_rule_configurations(self) -> Dict[str, Dict[str, float]]:
        """Define different rule weight configurations for training"""
        configurations = {
            # High contrary motion preference
            'high_contrary': {
                'contrary_motion': 2.0,
                'parallel_motion': 0.1,
                'oblique_motion': 0.8,
                'consonance': 1.0,
                'voice_leading': 0.9,
                'chord_progression': 0.8
            },
            
            # High parallel motion preference
            'high_parallel': {
                'contrary_motion': 0.2,
                'parallel_motion': 1.5,
                'oblique_motion': 0.6,
                'consonance': 1.0,
                'voice_leading': 0.7,
                'chord_progression': 0.9
            },
            
            # Balanced approach
            'balanced': {
                'contrary_motion': 1.0,
                'parallel_motion': 0.5,
                'oblique_motion': 0.7,
                'consonance': 1.0,
                'voice_leading': 0.9,
                'chord_progression': 0.8
            },
            
            # High consonance preference
            'high_consonance': {
                'contrary_motion': 0.8,
                'parallel_motion': 0.4,
                'oblique_motion': 0.6,
                'consonance': 1.5,
                'dissonance': 0.1,
                'voice_leading': 0.8,
                'chord_progression': 1.0
            },
            
            # High dissonance tolerance
            'high_dissonance': {
                'contrary_motion': 0.9,
                'parallel_motion': 0.3,
                'oblique_motion': 0.7,
                'consonance': 0.6,
                'dissonance': 0.8,
                'voice_leading': 0.7,
                'chord_progression': 0.6
            },
            
            # Voice leading focused
            'voice_leading_focused': {
                'contrary_motion': 0.7,
                'parallel_motion': 0.3,
                'oblique_motion': 0.8,
                'consonance': 0.9,
                'voice_leading': 1.5,
                'voice_crossing': 0.1,
                'voice_spacing': 1.0,
                'chord_progression': 0.7
            },
            
            # Chord progression focused
            'progression_focused': {
                'contrary_motion': 0.6,
                'parallel_motion': 0.4,
                'oblique_motion': 0.7,
                'consonance': 1.0,
                'voice_leading': 0.8,
                'chord_progression': 1.5,
                'cadence': 1.3
            }
        }
        
        return configurations
    
    def train_configuration(self, 
                          config_name: str, 
                          weights: Dict[str, float], 
                          episodes: int = 5000,
                          learning_rate: float = 0.1) -> Dict:
        """Train the RL model with a specific configuration"""
        
        print(f"\n🎵 TRAINING CONFIGURATION: {config_name.upper()}")
        print(f"=" * 60)
        print(f"🎛️ Weights: {weights}")
        print(f"📊 Episodes: {episodes}")
        
        # Create reward system and harmonizer
        reward_system = TunableMusicTheoryRewards()
        reward_system.set_weights(weights)
        harmonizer = TunableRLHarmonizer(reward_system)
        
        # Set learning parameters
        harmonizer.learning_rate = learning_rate
        
        # Get training melodies
        training_melodies = self.create_training_melodies()
        
        # Training variables
        episode_rewards = []
        best_reward = float('-inf')
        motion_statistics = {
            'contrary_ratios': [],
            'parallel_ratios': [],
            'oblique_ratios': []
        }
        
        print(f"🚀 Starting training...")
        print(f"📝 Progress: ", end="", flush=True)
        
        for episode in range(episodes):
            # Select random melody for this episode
            melody = np.random.choice(training_melodies)
            
            # Generate harmonization
            harmony = harmonizer.generate_harmonization(melody, custom_weights=weights)
            
            # Calculate episode reward
            episode_reward = reward_system.calculate_total_reward(melody, harmony)
            episode_rewards.append(episode_reward)
            
            # Track best performance
            if episode_reward > best_reward:
                best_reward = episode_reward
            
            # Calculate motion statistics
            contrary_count = 0
            parallel_count = 0
            oblique_count = 0
            total_motions = 0
            
            for i in range(1, min(len(melody), len(harmony))):
                melody_dir = melody[i] - melody[i-1]
                harmony_dir = harmony[i] - harmony[i-1]
                
                if (melody_dir > 0 and harmony_dir < 0) or (melody_dir < 0 and harmony_dir > 0):
                    contrary_count += 1
                elif (melody_dir > 0 and harmony_dir > 0) or (melody_dir < 0 and harmony_dir < 0):
                    parallel_count += 1
                else:
                    oblique_count += 1
                total_motions += 1
            
            if total_motions > 0:
                motion_statistics['contrary_ratios'].append(contrary_count / total_motions)
                motion_statistics['parallel_ratios'].append(parallel_count / total_motions)
                motion_statistics['oblique_ratios'].append(oblique_count / total_motions)
            
            # Progress indicator
            if (episode + 1) % 500 == 0:
                recent_avg = np.mean(episode_rewards[-500:])
                print(f"\nEpisode {episode + 1}: Avg reward = {recent_avg:.3f}, Best = {best_reward:.3f}")
                print("Progress: ", end="", flush=True)
            elif (episode + 1) % 100 == 0:
                print(".", end="", flush=True)
        
        # Calculate final statistics
        final_avg_reward = np.mean(episode_rewards[-1000:])
        final_std_reward = np.std(episode_rewards[-1000:])
        
        # Motion statistics
        avg_contrary = np.mean(motion_statistics['contrary_ratios']) if motion_statistics['contrary_ratios'] else 0
        avg_parallel = np.mean(motion_statistics['parallel_ratios']) if motion_statistics['parallel_ratios'] else 0
        avg_oblique = np.mean(motion_statistics['oblique_ratios']) if motion_statistics['oblique_ratios'] else 0
        
        # Create results
        results = {
            'config_name': config_name,
            'weights': weights,
            'episodes': episodes,
            'final_avg_reward': final_avg_reward,
            'final_std_reward': final_std_reward,
            'best_reward': best_reward,
            'motion_statistics': {
                'avg_contrary_ratio': avg_contrary,
                'avg_parallel_ratio': avg_parallel,
                'avg_oblique_ratio': avg_oblique
            },
            'episode_rewards': episode_rewards,
            'training_date': datetime.now().isoformat()
        }
        
        print(f"\n✅ Training completed!")
        print(f"📊 Final average reward: {final_avg_reward:.3f}")
        print(f"🏆 Best reward: {best_reward:.3f}")
        print(f"🎼 Motion ratios - Contrary: {avg_contrary:.2f}, Parallel: {avg_parallel:.2f}, Oblique: {avg_oblique:.2f}")
        
        return results, harmonizer
    
    def train_all_configurations(self, episodes_per_config: int = 3000) -> Dict:
        """Train models for all configurations"""
        print("🎵 TRAINING ALL CONFIGURATIONS")
        print("=" * 60)
        
        configurations = self.define_rule_configurations()
        results = {}
        models = {}
        
        for config_name, weights in configurations.items():
            result, model = self.train_configuration(config_name, weights, episodes_per_config)
            results[config_name] = result
            models[config_name] = model
            
            # Save individual model
            model_filename = f"trained_models/{config_name}_model.json"
            os.makedirs("trained_models", exist_ok=True)
            model.save_model(model_filename)
        
        # Save comparison results
        comparison_file = "trained_models/training_comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n🎉 ALL CONFIGURATIONS TRAINED!")
        print(f"📊 Comparison saved to: {comparison_file}")
        
        return results, models
    
    def analyze_results(self, results: Dict):
        """Analyze and visualize training results"""
        print(f"\n📊 ANALYZING TRAINING RESULTS")
        print("=" * 60)
        
        # Create comparison table
        print(f"{'Configuration':<20} {'Avg Reward':<12} {'Best Reward':<12} {'Contrary':<10} {'Parallel':<10}")
        print("-" * 70)
        
        for config_name, result in results.items():
            avg_reward = result['final_avg_reward']
            best_reward = result['best_reward']
            contrary_ratio = result['motion_statistics']['avg_contrary_ratio']
            parallel_ratio = result['motion_statistics']['avg_parallel_ratio']
            
            print(f"{config_name:<20} {avg_reward:<12.3f} {best_reward:<12.3f} {contrary_ratio:<10.2f} {parallel_ratio:<10.2f}")
        
        # Find best configurations
        best_reward_config = max(results.items(), key=lambda x: x[1]['final_avg_reward'])
        best_contrary_config = max(results.items(), key=lambda x: x[1]['motion_statistics']['avg_contrary_ratio'])
        best_parallel_config = max(results.items(), key=lambda x: x[1]['motion_statistics']['avg_parallel_ratio'])
        
        print(f"\n🏆 BEST CONFIGURATIONS:")
        print(f"   Highest Reward: {best_reward_config[0]} ({best_reward_config[1]['final_avg_reward']:.3f})")
        print(f"   Most Contrary Motion: {best_contrary_config[0]} ({best_contrary_config[1]['motion_statistics']['avg_contrary_ratio']:.2f})")
        print(f"   Most Parallel Motion: {best_parallel_config[0]} ({best_parallel_config[1]['motion_statistics']['avg_parallel_ratio']:.2f})")
        
        # Create visualization
        self.create_visualization(results)
    
    def create_visualization(self, results: Dict):
        """Create visualization of training results"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            config_names = list(results.keys())
            avg_rewards = [results[name]['final_avg_reward'] for name in config_names]
            best_rewards = [results[name]['best_reward'] for name in config_names]
            contrary_ratios = [results[name]['motion_statistics']['avg_contrary_ratio'] for name in config_names]
            parallel_ratios = [results[name]['motion_statistics']['avg_parallel_ratio'] for name in config_names]
            
            # Plot 1: Average Rewards
            ax1.bar(config_names, avg_rewards, color='skyblue')
            ax1.set_title('Average Rewards by Configuration')
            ax1.set_ylabel('Average Reward')
            ax1.tick_params(axis='x', rotation=45)
            
            # Plot 2: Best Rewards
            ax2.bar(config_names, best_rewards, color='lightgreen')
            ax2.set_title('Best Rewards by Configuration')
            ax2.set_ylabel('Best Reward')
            ax2.tick_params(axis='x', rotation=45)
            
            # Plot 3: Motion Ratios
            x = np.arange(len(config_names))
            width = 0.35
            ax3.bar(x - width/2, contrary_ratios, width, label='Contrary Motion', color='orange')
            ax3.bar(x + width/2, parallel_ratios, width, label='Parallel Motion', color='red')
            ax3.set_title('Motion Ratios by Configuration')
            ax3.set_ylabel('Ratio')
            ax3.set_xticks(x)
            ax3.set_xticklabels(config_names, rotation=45)
            ax3.legend()
            
            # Plot 4: Training Curves (first 1000 episodes)
            for config_name in config_names[:3]:  # Show first 3 configurations
                rewards = results[config_name]['episode_rewards'][:1000]
                episodes = range(len(rewards))
                ax4.plot(episodes, rewards, label=config_name, alpha=0.7)
            ax4.set_title('Training Curves (First 1000 Episodes)')
            ax4.set_xlabel('Episode')
            ax4.set_ylabel('Reward')
            ax4.legend()
            
            plt.tight_layout()
            plt.savefig('trained_models/training_analysis.png', dpi=300, bbox_inches='tight')
            print(f"📈 Visualization saved to: trained_models/training_analysis.png")
            
        except ImportError:
            print("📈 Matplotlib not available, skipping visualization")
    
    def demonstrate_trained_models(self, models: Dict, results: Dict):
        """Demonstrate the trained models with sample melodies"""
        print(f"\n🎼 DEMONSTRATING TRAINED MODELS")
        print("=" * 60)
        
        # Sample melody
        test_melody = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
        print(f"🎵 Test melody: {test_melody}")
        print(f"🎼 Melody notes: {[chr(ord('A') + (note % 12)) for note in test_melody]}")
        
        # Test each configuration
        for config_name, model in models.items():
            print(f"\n🎛️ Testing {config_name.upper()} configuration...")
            
            # Generate harmonization
            harmony = model.generate_harmonization(test_melody)
            
            # Analyze motion
            contrary_count = 0
            parallel_count = 0
            total_motions = 0
            
            for i in range(1, min(len(test_melody), len(harmony))):
                melody_dir = test_melody[i] - test_melody[i-1]
                harmony_dir = harmony[i] - harmony[i-1]
                
                if (melody_dir > 0 and harmony_dir < 0) or (melody_dir < 0 and harmony_dir > 0):
                    contrary_count += 1
                elif (melody_dir > 0 and harmony_dir > 0) or (melody_dir < 0 and harmony_dir < 0):
                    parallel_count += 1
                total_motions += 1
            
            print(f"   Harmony: {harmony}")
            print(f"   Harmony notes: {[chr(ord('A') + (note % 12)) for note in harmony]}")
            if total_motions > 0:
                print(f"   Contrary motion: {contrary_count}/{total_motions} ({contrary_count/total_motions*100:.1f}%)")
                print(f"   Parallel motion: {parallel_count}/{total_motions} ({parallel_count/total_motions*100:.1f}%)")

def main():
    """Main training function"""
    print("🎵 TURNABLE RL MODEL TRAINING")
    print("=" * 60)
    print("This script trains RL models with different music theory rule weights")
    print("Similar to Figure 2 of 'Style Modeling for N-Part Automatic Harmonization'")
    
    # Create trainer
    trainer = TunableRLTrainer()
    
    # Train all configurations
    results, models = trainer.train_all_configurations(episodes_per_config=3000)
    
    # Analyze results
    trainer.analyze_results(results)
    
    # Demonstrate trained models
    trainer.demonstrate_trained_models(models, results)
    
    print(f"\n✅ Training complete!")
    print(f"📁 Models saved in: trained_models/")
    print(f"📊 Analysis saved in: trained_models/training_comparison.json")
    print(f"📈 Visualization saved in: trained_models/training_analysis.png")

if __name__ == "__main__":
    main() 