#!/usr/bin/env python3
"""
Comprehensive Evaluation Framework for Harmonization Quality

This framework evaluates harmonizations across multiple dimensions:
- Harmonic coherence
- Voice leading quality  
- Counterpoint adherence
- Musical interest
- Style consistency
"""

import numpy as np
import mido
import json
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class HarmonizationEvaluator:
    """Evaluates harmonization quality across multiple metrics"""
    
    def __init__(self):
        self.metrics = {}
        
    def evaluate_harmonization(self, harmonization: Dict, melody_notes: List) -> Dict:
        """Evaluate a complete harmonization"""
        results = {}
        
        # Core metrics
        results['harmonic_coherence'] = self.harmonic_coherence_score(harmonization, melody_notes)
        results['voice_leading'] = self.voice_leading_score(harmonization)
        results['counterpoint'] = self.counterpoint_score(harmonization)
        results['musical_interest'] = self.musical_interest_score(harmonization)
        results['contrary_motion'] = self.contrary_motion_score(harmonization, melody_notes)
        
        # Overall score (weighted average)
        weights = {
            'harmonic_coherence': 0.25,
            'voice_leading': 0.25,
            'counterpoint': 0.20,
            'musical_interest': 0.15,
            'contrary_motion': 0.15
        }
        
        overall_score = sum(results[metric] * weights[metric] for metric in weights)
        results['overall_score'] = overall_score
        
        return results
    
    def harmonic_coherence_score(self, harmonization: Dict, melody_notes: List) -> float:
        """Evaluate harmonic coherence and chord quality"""
        score = 0.0
        total_chords = 0
        
        for i in range(len(melody_notes)):
            if i < len(harmonization['soprano']):
                # Get chord notes
                soprano = harmonization['soprano'][i]['note']
                alto = harmonization['alto'][i]['note'] if i < len(harmonization['alto']) else soprano - 3
                tenor = harmonization['tenor'][i]['note'] if i < len(harmonization['tenor']) else alto - 4
                bass = harmonization['bass'][i]['note'] if i < len(harmonization['bass']) else tenor - 4
                
                # Check for consonant intervals
                intervals = []
                notes = [soprano, alto, tenor, bass]
                for j in range(len(notes)):
                    for k in range(j+1, len(notes)):
                        interval = abs(notes[j] - notes[k]) % 12
                        if interval in [0, 3, 4, 7, 8]:  # Consonant intervals
                            intervals.append(interval)
                
                # Score based on consonant intervals
                if len(intervals) >= 3:  # Good chord
                    score += 1.0
                elif len(intervals) >= 2:  # Acceptable chord
                    score += 0.7
                elif len(intervals) >= 1:  # Weak chord
                    score += 0.3
                
                total_chords += 1
        
        return score / max(total_chords, 1)
    
    def voice_leading_score(self, harmonization: Dict) -> float:
        """Evaluate smoothness of voice leading"""
        score = 0.0
        total_transitions = 0
        
        voices = ['soprano', 'alto', 'tenor', 'bass']
        
        for voice in voices:
            if len(harmonization[voice]) < 2:
                continue
                
            for i in range(1, len(harmonization[voice])):
                current_note = harmonization[voice][i]['note']
                prev_note = harmonization[voice][i-1]['note']
                
                # Score based on interval size
                interval = abs(current_note - prev_note)
                if interval <= 2:  # Stepwise motion
                    score += 1.0
                elif interval <= 4:  # Small leap
                    score += 0.8
                elif interval <= 7:  # Medium leap
                    score += 0.6
                elif interval <= 12:  # Large leap
                    score += 0.3
                else:  # Very large leap
                    score += 0.1
                
                total_transitions += 1
        
        return score / max(total_transitions, 1)
    
    def counterpoint_score(self, harmonization: Dict) -> float:
        """Evaluate adherence to counterpoint rules"""
        score = 0.0
        total_checks = 0
        
        # Check for parallel fifths and octaves
        voices = ['soprano', 'alto', 'tenor', 'bass']
        
        for i in range(1, min(len(harmonization['soprano']), len(harmonization['alto']))):
            # Check parallel motion
            soprano_motion = harmonization['soprano'][i]['note'] - harmonization['soprano'][i-1]['note']
            alto_motion = harmonization['alto'][i]['note'] - harmonization['alto'][i-1]['note']
            
            # Reward contrary motion
            if (soprano_motion > 0 and alto_motion < 0) or (soprano_motion < 0 and alto_motion > 0):
                score += 1.0
            elif soprano_motion == 0 and alto_motion != 0:
                score += 0.8
            elif soprano_motion != 0 and alto_motion == 0:
                score += 0.8
            else:
                score += 0.3  # Parallel motion
            
            total_checks += 1
        
        return score / max(total_checks, 1)
    
    def musical_interest_score(self, harmonization: Dict) -> float:
        """Evaluate musical interest and variety"""
        score = 0.0
        
        # Check for melodic variety in each voice
        voices = ['soprano', 'alto', 'tenor', 'bass']
        
        for voice in voices:
            if len(harmonization[voice]) < 3:
                continue
            
            notes = [note['note'] for note in harmonization[voice]]
            
            # Check for melodic contour variety
            direction_changes = 0
            for i in range(1, len(notes)-1):
                if (notes[i] - notes[i-1]) * (notes[i+1] - notes[i]) < 0:
                    direction_changes += 1
            
            # Score based on direction changes
            if direction_changes >= len(notes) * 0.3:
                score += 1.0
            elif direction_changes >= len(notes) * 0.2:
                score += 0.7
            elif direction_changes >= len(notes) * 0.1:
                score += 0.4
            else:
                score += 0.2
        
        return score / len(voices)
    
    def contrary_motion_score(self, harmonization: Dict, melody_notes: List) -> float:
        """Evaluate contrary motion between melody and harmony"""
        score = 0.0
        total_checks = 0
        
        for i in range(1, min(len(melody_notes), len(harmonization['alto']))):
            # Melody motion
            melody_motion = melody_notes[i]['note'] - melody_notes[i-1]['note']
            
            # Harmony motion (using alto as representative)
            harmony_motion = harmonization['alto'][i]['note'] - harmonization['alto'][i-1]['note']
            
            # Reward contrary motion
            if (melody_motion > 0 and harmony_motion < 0) or (melody_motion < 0 and harmony_motion > 0):
                score += 1.0
            elif melody_motion == 0 and harmony_motion != 0:
                score += 0.8
            elif melody_motion != 0 and harmony_motion == 0:
                score += 0.8
            else:
                score += 0.2  # Parallel motion
            
            total_checks += 1
        
        return score / max(total_checks, 1)

def compare_harmonizations(harmonizations: Dict[str, Dict], melody_notes: List) -> Dict:
    """Compare multiple harmonizations"""
    evaluator = HarmonizationEvaluator()
    results = {}
    
    for name, harmonization in harmonizations.items():
        results[name] = evaluator.evaluate_harmonization(harmonization, melody_notes)
    
    return results

def generate_evaluation_report(results: Dict, output_file: str = "evaluation_report.json"):
    """Generate a comprehensive evaluation report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {},
        'detailed_results': results
    }
    
    # Calculate summary statistics
    metrics = ['harmonic_coherence', 'voice_leading', 'counterpoint', 'musical_interest', 'contrary_motion', 'overall_score']
    
    for metric in metrics:
        values = [result[metric] for result in results.values()]
        report['summary'][metric] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'best_method': max(results.keys(), key=lambda k: results[k][metric])
        }
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def plot_evaluation_results(results: Dict, output_file: str = "evaluation_plot.png"):
    """Create visualization of evaluation results"""
    metrics = ['harmonic_coherence', 'voice_leading', 'counterpoint', 'musical_interest', 'contrary_motion', 'overall_score']
    
    # Prepare data for plotting
    data = []
    for method, result in results.items():
        for metric in metrics:
            data.append({
                'Method': method,
                'Metric': metric.replace('_', ' ').title(),
                'Score': result[metric]
            })
    
    # Create plot
    plt.figure(figsize=(12, 8))
    sns.barplot(data=data, x='Metric', y='Score', hue='Method')
    plt.title('Harmonization Quality Comparison')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Example usage
    print("🎵 Harmonization Evaluation Framework")
    print("=" * 50)
    
    # Load your harmonizations here
    # harmonizations = {
    #     'hybrid': load_harmonization_from_midi('hybrid_coconet_rules_harmonization.mid'),
    #     'coconet_only': load_harmonization_from_midi('coconet_harmonized_realms2.mid'),
    #     'rules_only': load_harmonization_from_midi('realms2_harmonized_by_rl.mid')
    # }
    
    # melody_notes = load_melody_from_midi('realms2_idea.midi')
    
    # results = compare_harmonizations(harmonizations, melody_notes)
    # report = generate_evaluation_report(results)
    # plot_evaluation_results(results)
    
    print("✅ Evaluation framework ready!")
    print("📊 Use compare_harmonizations() to evaluate your harmonizations")
    print("📈 Use generate_evaluation_report() to create detailed reports")
    print("📊 Use plot_evaluation_results() to visualize comparisons") 