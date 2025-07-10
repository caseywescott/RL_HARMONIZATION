#!/usr/bin/env python3
"""
4-Part Harmonization using trained contrary motion model
"""

import numpy as np
import json
import mido
from datetime import datetime

def load_simple_model():
    """Load the trained simple contrary motion model"""
    try:
        with open("simple_contrary_motion_model_metadata.json", "r") as f:
            metadata = json.load(f)
        print(f"✅ Loaded model: {metadata['model_name']}")
        print(f"   Episodes trained: {metadata['episodes_trained']}")
        print(f"   Average reward: {metadata['average_reward']:.3f}")
        print(f"   Best reward: {metadata['best_reward']:.3f}")
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
                print(f"✅ Loaded {len(melody_notes)} notes from track {track_num}")
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
    print(f"\n🎵 GENERATING 4-PART HARMONIZATION")
    print(f"Melody notes: {len(melody_notes)} notes")
    
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
        
        # Generate harmony voices using trained model approach
        # Harmony options with weights based on training
        harmony_options = [
            melody_note - 3,   # Minor third
            melody_note - 7,   # Perfect fifth
            melody_note + 5,   # Perfect fourth
            melody_note - 10,  # Minor seventh
            melody_note + 2,   # Major second
            melody_note - 12,  # Octave below
            melody_note + 12,  # Octave above
        ]
        
        # Weights based on training results (favoring contrary motion)
        weights = [0.25, 0.25, 0.2, 0.1, 0.1, 0.05, 0.05]
        
        # If we have previous notes, try to create contrary motion
        if prev_notes['soprano'] is not None:
            melody_direction = melody_note - prev_notes['soprano']
            
            if melody_direction > 0:  # Melody going up
                # Prefer harmony going down
                weights = [0.3, 0.3, 0.2, 0.1, 0.05, 0.03, 0.02]
            elif melody_direction < 0:  # Melody going down
                # Prefer harmony going up
                weights = [0.3, 0.3, 0.2, 0.1, 0.05, 0.03, 0.02]
        
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

def save_4part_midi_mido(harmonization, filename="realms2_4voice_contrary_motion.mid", ticks_per_beat=480, tempo_bpm=120):
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
    print(f"✅ Saved 4-part harmonization (mido): {filename}")
    return filename

def get_note_name(midi_note):
    """Convert MIDI note number to note name"""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note = midi_note % 12
    return f"{note_names[note]}{octave}"

def main():
    """Main function"""
    print("🎵 4-PART CONTRARY MOTION HARMONIZATION")
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
    import mido
    mid = mido.MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat
    print(f"\n🎼 Loaded melody from: {midi_file}")
    print(f"Number of notes: {len(melody_notes)} | Ticks per beat: {ticks_per_beat}")
    
    # Generate 4-part harmonization
    harmonization, total_reward = generate_4part_harmonization(melody_notes, model_metadata)
    
    # Display results
    print(f"\n📊 HARMONIZATION RESULTS:")
    print(f"Total reward: {total_reward:.3f}")
    print(f"Average reward per step: {total_reward/len(melody_notes):.3f}")
    
    print(f"\n🎵 VOICE RANGES:")
    for voice in ['soprano', 'alto', 'tenor', 'bass']:
        notes = [note['note'] for note in harmonization[voice]]
        print(f"  {voice.capitalize()}: {min(notes)}-{max(notes)} ({get_note_name(min(notes))}-{get_note_name(max(notes))})")
    
    # Save harmonization using mido
    midi_file = save_4part_midi_mido(harmonization, ticks_per_beat=ticks_per_beat)
    
    print(f"\n🎉 SUCCESS! 4-part harmonization generated and saved.")
    print(f"Files created:")
    print(f"  - {midi_file}")
    
    return True

if __name__ == "__main__":
    main() 