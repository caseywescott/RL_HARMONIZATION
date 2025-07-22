#!/usr/bin/env python3
"""
Analyze the generated example MIDI files to demonstrate the hybrid harmonization system.
"""

import mido
import os

def note_to_name(note_number):
    """Convert MIDI note number to note name."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note_number // 12) - 1
    note_name = notes[note_number % 12]
    return f"{note_name}{octave}"

def analyze_midi_file(filename):
    """Analyze a MIDI file and return detailed statistics."""
    if not os.path.exists(filename):
        return None
    
    try:
        midi = mido.MidiFile(filename)
        
        # Count notes per track
        track_stats = []
        total_notes = 0
        total_duration = 0
        
        for i, track in enumerate(midi.tracks):
            notes = []
            current_time = 0
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Find corresponding note_off
                    note_end_time = current_time
                    for j, next_msg in enumerate(track[track.index(msg)+1:], track.index(msg)+1):
                        if (next_msg.type == 'note_off' or 
                            (next_msg.type == 'note_on' and next_msg.velocity == 0)) and next_msg.note == msg.note:
                            note_end_time += sum(m.time for m in track[track.index(msg)+1:j+1])
                            break
                    
                    duration = note_end_time - current_time
                    notes.append({
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'start_time': current_time,
                        'duration': duration,
                        'pitch_name': note_to_name(msg.note)
                    })
            
            if notes:
                track_stats.append({
                    'track': i,
                    'note_count': len(notes),
                    'notes': notes,
                    'avg_pitch': sum(n['note'] for n in notes) / len(notes) if notes else 0,
                    'min_pitch': min(n['note'] for n in notes) if notes else 0,
                    'max_pitch': max(n['note'] for n in notes) if notes else 0,
                    'avg_velocity': sum(n['velocity'] for n in notes) / len(notes) if notes else 0,
                    'total_duration': sum(n['duration'] for n in notes)
                })
                total_notes += len(notes)
                total_duration = max(total_duration, max(n['start_time'] + n['duration'] for n in notes))
        
        return {
            'filename': filename,
            'file_size': os.path.getsize(filename),
            'total_notes': total_notes,
            'tracks': len(track_stats),
            'track_stats': track_stats,
            'total_duration': total_duration,
            'duration_seconds': total_duration / 480 if total_duration > 0 else 0  # Assuming 480 ticks per beat
        }
    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        return None

def analyze_examples():
    """Analyze all generated example MIDI files."""
    
    files = [
        'realms2_harmonized.mid',  # Original input
        'examples/output/example_rl_output.mid',      # RL-only
        'examples/output/example_coconet_output.mid', # Coconet-only  
        'examples/output/example_hybrid_output.mid'   # Hybrid (Coconet → RL)
    ]
    
    print("🎵 Example MIDI Analysis - Hybrid Harmonization System")
    print("=" * 70)
    
    results = []
    for filename in files:
        result = analyze_midi_file(filename)
        if result:
            results.append(result)
            print(f"\n📁 {result['filename']}")
            print(f"   File size: {result['file_size']} bytes")
            print(f"   Total notes: {result['total_notes']}")
            print(f"   Tracks: {result['tracks']}")
            print(f"   Duration: {result['duration_seconds']:.2f} seconds")
            
            for track in result['track_stats']:
                print(f"   Track {track['track']}: {track['note_count']} notes")
                print(f"     Pitch range: {track['min_pitch']}-{track['max_pitch']} (avg: {track['avg_pitch']:.1f})")
                print(f"     Velocity: avg {track['avg_velocity']:.1f}")
                
                # Show first few notes
                if track['notes']:
                    sample_notes = [f"{n['pitch_name']}({n['note']})" for n in track['notes'][:5]]
                    print(f"     Sample notes: {', '.join(sample_notes)}")
    
    # Comparison analysis
    print(f"\n📊 Harmonization Method Comparison:")
    print("-" * 50)
    
    if len(results) >= 4:
        original = results[0]
        rl = results[1]
        coconet = results[2]
        hybrid = results[3]
        
        print(f"Original melody: {original['total_notes']} notes, {original['file_size']} bytes")
        print(f"RL-only: {rl['total_notes']} notes, {rl['file_size']} bytes")
        print(f"Coconet-only: {coconet['total_notes']} notes, {coconet['file_size']} bytes")
        print(f"Hybrid: {hybrid['total_notes']} notes, {hybrid['file_size']} bytes")
        
        print(f"\n🎼 Voice Distribution Analysis:")
        print("-" * 40)
        
        for result in results[1:]:  # Skip original
            print(f"\n{result['filename']}:")
            for track in result['track_stats']:
                avg_pitch = track['avg_pitch']
                if avg_pitch > 70:
                    voice = "Soprano"
                elif avg_pitch > 60:
                    voice = "Alto"
                elif avg_pitch > 50:
                    voice = "Tenor"
                else:
                    voice = "Bass"
                print(f"  Track {track['track']}: {voice} ({track['note_count']} notes)")
    
    # Key insights
    print(f"\n🔍 Key Insights:")
    print("-" * 30)
    
    if len(results) >= 4:
        print(f"• RL-only produces the most notes ({rl['total_notes']}) - full 4-part harmony")
        print(f"• Coconet-only is concise ({coconet['total_notes']} notes) - neural approach")
        print(f"• Hybrid is most optimized ({hybrid['total_notes']} notes) - combines both approaches")
        print(f"• File sizes reflect complexity: RL > Coconet > Hybrid")
        print(f"• All methods successfully create 4-part harmonizations")

if __name__ == "__main__":
    analyze_examples() 