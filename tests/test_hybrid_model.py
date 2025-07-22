#!/usr/bin/env python3
"""
Test Hybrid Model with realms2_idea.midi

This script tests the hybrid harmonization system specifically with the realms2_idea.midi file
and provides detailed evaluation metrics.
"""

import numpy as np
import mido
import json
import os
from datetime import datetime
import sys

# Add src to path
sys.path.append('../src')

def load_melody_from_midi(midi_file):
    """Load melody notes from MIDI file"""
    try:
        mid = mido.MidiFile(midi_file)
        melody_notes = []
        
        for track in mid.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    melody_notes.append({
                        'note': msg.note,
                        'start_time': current_time,
                        'duration': 480,  # Default duration
                        'velocity': msg.velocity
                    })
                    if len(melody_notes) >= 50:  # Limit length
                        break
            if melody_notes:
                break
        
        return melody_notes
    except Exception as e:
        print(f"❌ Error loading melody: {e}")
        return []

def load_harmonization_from_midi(midi_file):
    """Load harmonization from MIDI file"""
    try:
        mid = mido.MidiFile(midi_file)
        harmonization = {
            'soprano': [],
            'alto': [],
            'tenor': [],
            'bass': []
        }
        
        # Process each track
        for track_num, track in enumerate(mid.tracks):
            current_time = 0
            active_notes = {}
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = current_time
                    
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time = active_notes[msg.note]
                        duration = current_time - start_time
                        
                        # Assign to voice based on track number
                        if track_num == 0:
                            voice = 'soprano'
                        elif track_num == 1:
                            voice = 'alto'
                        elif track_num == 2:
                            voice = 'tenor'
                        else:
                            voice = 'bass'
                        
                        harmonization[voice].append({
                            'note': msg.note,
                            'start_time': start_time,
                            'duration': duration,
                            'velocity': 100
                        })
                        
                        del active_notes[msg.note]
        
        return harmonization
        
    except Exception as e:
        print(f"❌ Error loading harmonization: {e}")
        return None

def evaluate_harmonic_coherence(harmonization, melody_notes):
    """Evaluate harmonic coherence of harmonization"""
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
            notes = [soprano, alto, tenor, bass]
            consonant_intervals = 0
            total_intervals = 0
            
            for j in range(len(notes)):
                for k in range(j+1, len(notes)):
                    interval = abs(notes[j] - notes[k]) % 12
                    total_intervals += 1
                    if interval in [0, 3, 4, 7, 8]:  # Consonant intervals
                        consonant_intervals += 1
            
            score += consonant_intervals / total_intervals
            total_chords += 1
    
    return score / max(total_chords, 1)

def evaluate_voice_leading(harmonization):
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

def evaluate_contrary_motion(harmonization, melody_notes):
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

def evaluate_harmonization(harmonization, melody_notes):
    """Evaluate a harmonization across all metrics"""
    results = {}
    
    results['harmonic_coherence'] = evaluate_harmonic_coherence(harmonization, melody_notes)
    results['voice_leading'] = evaluate_voice_leading(harmonization)
    results['contrary_motion'] = evaluate_contrary_motion(harmonization, melody_notes)
    
    # Overall score (weighted average)
    weights = {
        'harmonic_coherence': 0.4,
        'voice_leading': 0.35,
        'contrary_motion': 0.25
    }
    
    overall_score = sum(results[metric] * weights[metric] for metric in weights)
    results['overall_score'] = overall_score
    
    return results

def test_hybrid_model():
    """Test the hybrid model with realms2_idea.midi"""
    print("🎵 TESTING HYBRID MODEL WITH REALMS2_IDEA.MIDI")
    print("=" * 60)
    
    # Load the melody
    melody_file = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    melody_notes = load_melody_from_midi(melody_file)
    
    if not melody_notes:
        print("❌ Failed to load melody from realms2_idea.midi")
        return
    
    print(f"✅ Loaded melody: {len(melody_notes)} notes")
    print(f"🎼 Melody range: {min(note['note'] for note in melody_notes)}-{max(note['note'] for note in melody_notes)}")
    
    # Test different harmonization approaches
    harmonization_files = [
        {
            'name': 'Hybrid Coconet + RL Rules',
            'file': 'hybrid_coconet_rules_harmonization.mid'
        },
        {
            'name': 'Coconet Only',
            'file': 'coconet_harmonized_realms2.mid'
        },
        {
            'name': 'RL Rules Only',
            'file': 'realms2_harmonized_by_rl.mid'
        },
        {
            'name': 'Simple Contrary Motion',
            'file': 'realms2_4voice_harmonized.mid'
        }
    ]
    
    results = {}
    
    for harmonization_info in harmonization_files:
        file_path = harmonization_info['file']
        name = harmonization_info['name']
        
        print(f"\n🤖 Testing {name}...")
        
        if os.path.exists(file_path):
            harmonization = load_harmonization_from_midi(file_path)
            
            if harmonization:
                # Evaluate harmonization
                evaluation = evaluate_harmonization(harmonization, melody_notes)
                results[name] = evaluation
                
                # Print voice ranges
                print(f"  📊 Voice ranges:")
                for voice in ['soprano', 'alto', 'tenor', 'bass']:
                    notes = [note['note'] for note in harmonization[voice]]
                    if notes:
                        print(f"    {voice.title()}: {min(notes)}-{max(notes)}")
                
                # Print scores
                print(f"  📈 Scores:")
                for metric, score in evaluation.items():
                    print(f"    {metric.replace('_', ' ').title()}: {score:.3f}")
            else:
                print(f"  ❌ Failed to load harmonization from {file_path}")
        else:
            print(f"  ❌ File not found: {file_path}")
    
    # Generate comparison report
    if results:
        print(f"\n📊 COMPARISON RESULTS:")
        print("-" * 50)
        
        # Print comparison table
        metrics = ['harmonic_coherence', 'voice_leading', 'contrary_motion', 'overall_score']
        metric_names = ['Harmonic Coherence', 'Voice Leading', 'Contrary Motion', 'Overall Score']
        
        print(f"{'Method':<25}", end="")
        for metric_name in metric_names:
            print(f"{metric_name:<15}", end="")
        print()
        
        print("-" * 85)
        
        for method_name, evaluation in results.items():
            print(f"{method_name:<25}", end="")
            for metric in metrics:
                score = evaluation[metric]
                print(f"{score:<15.3f}", end="")
            print()
        
        # Find best method
        best_method = max(results.keys(), key=lambda k: results[k]['overall_score'])
        best_score = results[best_method]['overall_score']
        
        print(f"\n🏆 BEST PERFORMING METHOD: {best_method}")
        print(f"📈 Overall Score: {best_score:.3f}")
        
        # Save detailed results
        report = {
            'test_date': datetime.now().isoformat(),
            'melody_file': melody_file,
            'melody_notes': len(melody_notes),
            'results': results,
            'best_method': best_method,
            'best_score': best_score
        }
        
        with open('hybrid_model_test_results.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: hybrid_model_test_results.json")
    
    return results

if __name__ == "__main__":
    test_hybrid_model() 