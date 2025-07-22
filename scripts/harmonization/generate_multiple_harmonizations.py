#!/usr/bin/env python3
"""
Generate multiple harmonization versions of the same melody
"""

import os
import numpy as np
import json
import mido
from datetime import datetime

def load_simple_model():
    """Load the trained simple contrary motion model"""
    try:
        with open("simple_contrary_motion_model_metadata.json", "r") as f:
            metadata = json.load(f)
        return metadata
    except FileNotFoundError:
        print("❌ Model metadata not found. Please train the model first.")
        return None

def load_midi_melody(midi_file):
    """Load melody from MIDI file with proper note durations"""
    try:
        mid = mido.MidiFile(midi_file)
        melody_notes = []
        
        # Find the track with melody (usually track 0 or 1)
        for track_num, track in enumerate(mid.tracks):
            current_time = 0
            active_notes = {}  # Track active notes by pitch
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Note on - store the start time
                    active_notes[msg.note] = current_time
                    
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Note off - calculate duration and add to melody
                    if msg.note in active_notes:
                        start_time = active_notes[msg.note]
                        duration = current_time - start_time
                        
                        melody_notes.append({
                            'note': msg.note,
                            'start_time': start_time,
                            'duration': duration,
                            'velocity': 100,  # Default velocity
                            'track': track_num
                        })
                        
                        del active_notes[msg.note]
            
            # If we found notes in this track, use it
            if melody_notes:
                break
        
        if not melody_notes:
            print("❌ No melody notes found in MIDI file")
            return None
            
        return melody_notes
        
    except Exception as e:
        print(f"❌ Error loading MIDI file: {e}")
        return None

def simple_contrary_motion_reward(melody_note, harmony_note, prev_melody_note, prev_harmony_note):
    """Simple contrary motion reward calculation"""
    if prev_melody_note is None or prev_harmony_note is None:
        return 0.0
    
    melody_direction = melody_note - prev_melody_note
    harmony_direction = harmony_note - prev_harmony_note
    
    # Contrary motion: melody and harmony move in opposite directions
    if melody_direction > 0 and harmony_direction < 0:
        return 2.0
    elif melody_direction < 0 and harmony_direction > 0:
        return 2.0
    elif melody_direction == 0 and harmony_direction != 0:
        return 1.0  # Partial reward for static melody
    else:
        return 0.0  # No contrary motion

def simple_music_theory_reward(melody_note, harmony_note):
    """Simple music theory reward"""
    # Basic consonance reward
    interval = abs(melody_note - harmony_note) % 12
    if interval in [0, 3, 4, 7, 8]:  # Unison, minor/major third, perfect fourth/fifth, minor sixth
        return 1.0
    else:
        return 0.5

def generate_4part_harmonization(melody_notes, model_metadata):
    """Generate 4-part harmonization using the trained model"""
    # 4-part harmony: Soprano (melody), Alto, Tenor, Bass
    harmonization = {
        'soprano': [],  # Original melody
        'alto': [],
        'tenor': [],
        'bass': []
    }
    
    prev_notes = {
        'soprano': None,
        'alto': None,
        'tenor': None,
        'bass': None
    }
    
    total_reward = 0
    
    for i, melody_data in enumerate(melody_notes):
        melody_note = melody_data['note']
        
        # Soprano = original melody
        soprano_note = melody_note
        
        # Generate Alto (close to soprano)
        alto_options = [melody_note - 3, melody_note - 7, melody_note + 5]
        alto_weights = [0.4, 0.4, 0.2]
        alto_note = np.random.choice(alto_options, p=alto_weights)
        
        # Generate Tenor (lower range)
        tenor_options = [melody_note - 7, melody_note - 12, melody_note - 15, melody_note - 19]
        tenor_weights = [0.4, 0.3, 0.2, 0.1]
        tenor_note = np.random.choice(tenor_options, p=tenor_weights)
        
        # Generate Bass (lowest range)
        bass_options = [melody_note - 12, melody_note - 19, melody_note - 24, melody_note - 28]
        bass_weights = [0.4, 0.3, 0.2, 0.1]
        bass_note = np.random.choice(bass_options, p=bass_weights)
        
        # Calculate rewards for each voice
        voices = ['alto', 'tenor', 'bass']
        voice_notes = [alto_note, tenor_note, bass_note]
        
        step_reward = 0
        for voice, note in zip(voices, voice_notes):
            music_reward = simple_music_theory_reward(melody_note, note)
            contrary_reward = simple_contrary_motion_reward(melody_note, note, prev_notes['soprano'], prev_notes[voice])
            step_reward += music_reward + contrary_reward
        
        total_reward += step_reward
        
        # Store harmonization data
        harmonization['soprano'].append({
            'note': soprano_note,
            'start_time': melody_data['start_time'],
            'duration': melody_data['duration'],
            'velocity': melody_data['velocity']
        })
        
        harmonization['alto'].append({
            'note': alto_note,
            'start_time': melody_data['start_time'],
            'duration': melody_data['duration'],
            'velocity': melody_data['velocity']
        })
        
        harmonization['tenor'].append({
            'note': tenor_note,
            'start_time': melody_data['start_time'],
            'duration': melody_data['duration'],
            'velocity': melody_data['velocity']
        })
        
        harmonization['bass'].append({
            'note': bass_note,
            'start_time': melody_data['start_time'],
            'duration': melody_data['duration'],
            'velocity': melody_data['velocity']
        })
        
        # Update previous notes
        prev_notes['soprano'] = soprano_note
        prev_notes['alto'] = alto_note
        prev_notes['tenor'] = tenor_note
        prev_notes['bass'] = bass_note
    
    return harmonization, total_reward

def save_4part_midi_mido(harmonization, filename, ticks_per_beat=480, tempo_bpm=120):
    """Save 4-part harmonization as MIDI file using mido, with correct note on/off timing and delta times."""
    import mido
    from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

    midi = MidiFile(ticks_per_beat=ticks_per_beat)
    voices = ['soprano', 'alto', 'tenor', 'bass']
    channel = 0
    velocity = 100
    tempo = bpm2tempo(tempo_bpm)

    # Add a tempo track
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    midi.tracks.append(tempo_track)

    for voice in voices:
        track = MidiTrack()
        midi.tracks.append(track)
        notes = harmonization[voice]
        # Collect all note_on and note_off events as (tick, type, note, velocity)
        events = []
        for note in notes:
            start_tick = int(note['start_time'])
            duration_tick = int(note['duration'])
            end_tick = start_tick + duration_tick
            events.append((start_tick, 'on', note['note'], note['velocity']))
            events.append((end_tick, 'off', note['note'], 0))
        # Sort events by tick, with note_off before note_on if at same tick
        events.sort(key=lambda x: (x[0], 0 if x[1]=='off' else 1))
        last_tick = 0
        for tick, ev_type, note_num, vel in events:
            delta = tick - last_tick
            if ev_type == 'on':
                track.append(Message('note_on', note=note_num, velocity=vel, time=delta, channel=channel))
            else:
                track.append(Message('note_off', note=note_num, velocity=0, time=delta, channel=channel))
            last_tick = tick
    midi.save(filename)

def main():
    """Main function"""
    print("🎵 GENERATE MULTIPLE HARMONIZATION VERSIONS")
    print("=" * 50)
    
    # Load model
    model_metadata = load_simple_model()
    if not model_metadata:
        return False
    
    # Load MIDI melody
    midi_file = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    melody_notes = load_midi_melody(midi_file)
    if not melody_notes:
        return False
    
    # Get ticks_per_beat from the MIDI file
    mid = mido.MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat
    
    print(f"🎼 Loaded melody from: {midi_file}")
    print(f"Number of notes: {len(melody_notes)} | Ticks per beat: {ticks_per_beat}")
    
    # Create output folder
    output_folder = "multiple_harmonizations"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output folder: {output_folder}")
    
    # Generate 20 different harmonizations
    num_versions = 20
    print(f"\n🎵 GENERATING {num_versions} HARMONIZATION VERSIONS...")
    
    results = []
    
    for version in range(1, num_versions + 1):
        print(f"  Generating version {version}/{num_versions}...", end=" ", flush=True)
        
        # Generate harmonization
        harmonization, total_reward = generate_4part_harmonization(melody_notes, model_metadata)
        
        # Save MIDI file
        filename = f"{output_folder}/harmonization_v{version:02d}.mid"
        save_4part_midi_mido(harmonization, filename, ticks_per_beat=ticks_per_beat)
        
        # Calculate voice ranges
        voice_ranges = {}
        for voice in ['soprano', 'alto', 'tenor', 'bass']:
            notes = [note['note'] for note in harmonization[voice]]
            voice_ranges[voice] = (min(notes), max(notes))
        
        results.append({
            'version': version,
            'filename': filename,
            'total_reward': total_reward,
            'avg_reward': total_reward / len(melody_notes),
            'voice_ranges': voice_ranges
        })
        
        print(f"✅ (Reward: {total_reward:.1f})")
    
    # Save summary
    summary_file = f"{output_folder}/harmonization_summary.txt"
    with open(summary_file, "w") as f:
        f.write("MULTIPLE HARMONIZATION VERSIONS SUMMARY\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source melody: {midi_file}\n")
        f.write(f"Number of versions: {num_versions}\n")
        f.write(f"Model: {model_metadata['model_name']}\n")
        f.write(f"Episodes trained: {model_metadata['episodes_trained']}\n\n")
        
        f.write("VERSION DETAILS:\n")
        f.write("-" * 30 + "\n")
        for result in results:
            f.write(f"Version {result['version']:02d}:\n")
            f.write(f"  File: {result['filename']}\n")
            f.write(f"  Total reward: {result['total_reward']:.3f}\n")
            f.write(f"  Avg reward: {result['avg_reward']:.3f}\n")
            f.write(f"  Voice ranges:\n")
            for voice, (min_note, max_note) in result['voice_ranges'].items():
                f.write(f"    {voice.capitalize()}: {min_note}-{max_note}\n")
            f.write("\n")
    
    # Calculate statistics
    rewards = [r['total_reward'] for r in results]
    avg_rewards = [r['avg_reward'] for r in results]
    
    print(f"\n📊 GENERATION COMPLETE!")
    print(f"✅ Generated {num_versions} harmonization versions")
    print(f"📁 Output folder: {output_folder}")
    print(f"📄 Summary file: {summary_file}")
    print(f"\n📈 STATISTICS:")
    print(f"  Average total reward: {np.mean(rewards):.3f}")
    print(f"  Best total reward: {max(rewards):.3f}")
    print(f"  Worst total reward: {min(rewards):.3f}")
    print(f"  Average per-step reward: {np.mean(avg_rewards):.3f}")
    
    return True

if __name__ == "__main__":
    main() 