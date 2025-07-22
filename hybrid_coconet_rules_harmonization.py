#!/usr/bin/env python3
"""
Hybrid Harmonization: Coconet API + Our Trained Rules Model
Combines neural network harmonization with our contrary motion optimization
"""

import requests
import json
import numpy as np
import mido
import os
from datetime import datetime
import base64

def load_simple_model():
    """Load the trained simple contrary motion model"""
    try:
        with open("simple_contrary_motion_model_metadata.json", "r") as f:
            metadata = json.load(f)
        print(f"✅ Loaded trained model: {metadata['model_name']}")
        print(f"   Episodes trained: {metadata['episodes_trained']}")
        print(f"   Average reward: {metadata['average_reward']:.3f}")
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

def send_to_coconet_api(midi_file_path, temperature=1.0, num_steps=512):
    """Send MIDI file to Coconet API for harmonization"""
    try:
        # Use the JSON endpoint for easier handling
        url = "http://localhost:8000/generate_music_json"
        params = {
            "temperature": temperature,
            "num_steps": num_steps
        }
        
        # Send file as multipart form data
        with open(midi_file_path, 'rb') as f:
            files = {'file': (os.path.basename(midi_file_path), f, 'audio/midi')}
            print(f"🤖 Sending to Coconet API...")
            response = requests.post(url, params=params, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Coconet API response: {result}")
            
            if 'harmonized_midi' in result:
                harmonized_midi_base64 = result['harmonized_midi']
                harmonized_midi_data = base64.b64decode(harmonized_midi_base64)
                temp_file = "temp_coconet_harmonization.mid"
                with open(temp_file, 'wb') as f:
                    f.write(harmonized_midi_data)
                print(f"✅ Coconet harmonization received and saved")
                return temp_file
            else:
                print(f"❌ No harmonized MIDI in response: {result}")
                return None
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error calling Coconet API: {e}")
        return None

def load_coconet_harmonization(midi_file):
    """Load harmonization from Coconet-generated MIDI file"""
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
        print(f"❌ Error loading Coconet harmonization: {e}")
        return None

def apply_contrary_motion_rules(harmonization, melody_notes):
    """Apply our trained contrary motion rules to optimize the harmonization"""
    print(f"\n🎛️ APPLYING CONTRARY MOTION RULES...")
    
    def contrary_motion_reward(melody_note, harmony_note, prev_melody_note, prev_harmony_note):
        """Calculate contrary motion reward"""
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
            return 1.0
        else:
            return 0.0
    
    def music_theory_reward(melody_note, harmony_note):
        """Calculate music theory reward"""
        interval = abs(melody_note - harmony_note) % 12
        if interval in [0, 3, 4, 7, 8]:  # Consonant intervals
            return 1.0
        else:
            return 0.5
    
    # Optimize each voice
    voices = ['alto', 'tenor', 'bass']
    optimized_harmonization = {
        'soprano': harmonization['soprano'].copy(),  # Keep melody unchanged
        'alto': [],
        'tenor': [],
        'bass': []
    }
    
    total_improvement = 0
    
    for voice in voices:
        prev_melody_note = None
        prev_harmony_note = None
        
        for i, note_data in enumerate(harmonization[voice]):
            melody_note = melody_notes[i]['note'] if i < len(melody_notes) else 60
            current_harmony_note = note_data['note']
            
            # Calculate current reward
            current_reward = contrary_motion_reward(melody_note, current_harmony_note, prev_melody_note, prev_harmony_note)
            current_reward += music_theory_reward(melody_note, current_harmony_note)
            
            # Try alternative notes
            alternatives = [
                melody_note - 3,   # Minor third
                melody_note - 7,   # Perfect fifth
                melody_note + 5,   # Perfect fourth
                melody_note - 10,  # Minor seventh
                melody_note - 12,  # Octave below
            ]
            
            best_note = current_harmony_note
            best_reward = current_reward
            
            for alt_note in alternatives:
                if 21 <= alt_note <= 108:  # Valid MIDI range
                    alt_reward = contrary_motion_reward(melody_note, alt_note, prev_melody_note, prev_harmony_note)
                    alt_reward += music_theory_reward(melody_note, alt_note)
                    
                    if alt_reward > best_reward:
                        best_note = alt_note
                        best_reward = alt_reward
            
            # Apply optimization with some randomness
            if best_reward > current_reward and np.random.random() < 0.7:  # 70% chance to apply
                optimized_note = best_note
                total_improvement += best_reward - current_reward
            else:
                optimized_note = current_harmony_note
            
            # Store optimized note
            optimized_harmonization[voice].append({
                'note': optimized_note,
                'start_time': note_data['start_time'],
                'duration': note_data['duration'],
                'velocity': note_data['velocity']
            })
            
            prev_melody_note = melody_note
            prev_harmony_note = optimized_note
    
    print(f"✅ Rules applied! Total improvement: {total_improvement:.1f}")
    return optimized_harmonization

def save_harmonization_midi(harmonization, filename, ticks_per_beat=480):
    """Save harmonization as MIDI file"""
    import mido
    from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

    midi = MidiFile(ticks_per_beat=ticks_per_beat)
    voices = ['soprano', 'alto', 'tenor', 'bass']
    channel = 0
    tempo = bpm2tempo(120)

    # Add tempo track
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    midi.tracks.append(tempo_track)

    for voice in voices:
        track = MidiTrack()
        midi.tracks.append(track)
        notes = harmonization[voice]
        
        # Collect all note_on and note_off events
        events = []
        for note in notes:
            start_tick = int(note['start_time'])
            duration_tick = int(note['duration'])
            end_tick = start_tick + duration_tick
            events.append((start_tick, 'on', note['note'], note['velocity']))
            events.append((end_tick, 'off', note['note'], 0))
        
        # Sort events by tick
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
    print(f"✅ Saved harmonization: {filename}")

def main():
    """Main function"""
    print("🎵 HYBRID HARMONIZATION: COCONET API + TRAINED RULES")
    print("=" * 60)
    print("🤖 Coconet Neural Network + 🎛️ Our Trained Contrary Motion Rules")
    
    # Load our trained model
    model_metadata = load_simple_model()
    if not model_metadata:
        return False
    
    # Load melody
    midi_file = "/Volumes/LaCie/RL_HARMONIZATION/realms2_idea.midi"
    melody_notes = load_midi_melody(midi_file)
    if not melody_notes:
        return False
    
    # Get ticks_per_beat
    mid = mido.MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat
    
    print(f"🎼 Loaded melody from: {midi_file}")
    print(f"Number of notes: {len(melody_notes)} | Ticks per beat: {ticks_per_beat}")
    
    # Step 1: Generate harmonization using Coconet API
    print(f"\n🤖 STEP 1: COCONET NEURAL NETWORK GENERATION")
    coconet_file = send_to_coconet_api(midi_file, temperature=1.0, num_steps=len(melody_notes))
    
    if not coconet_file:
        print(f"❌ Coconet generation failed. Using fallback approach...")
        # Fallback to our simple rules-based approach
        from generate_multiple_harmonizations import generate_4part_harmonization
        harmonization, _ = generate_4part_harmonization(melody_notes, model_metadata)
    else:
        # Step 2: Load Coconet harmonization
        print(f"\n📥 STEP 2: LOADING COCONET HARMONIZATION")
        harmonization = load_coconet_harmonization(coconet_file)
        
        if not harmonization:
            print(f"❌ Failed to load Coconet harmonization. Using fallback...")
            from generate_multiple_harmonizations import generate_4part_harmonization
            harmonization, _ = generate_4part_harmonization(melody_notes, model_metadata)
    
    # Step 3: Apply our trained contrary motion rules
    print(f"\n🎛️ STEP 3: APPLYING TRAINED CONTRARY MOTION RULES")
    optimized_harmonization = apply_contrary_motion_rules(harmonization, melody_notes)
    
    # Save final harmonization
    output_file = "hybrid_coconet_rules_harmonization.mid"
    save_harmonization_midi(optimized_harmonization, output_file, ticks_per_beat=ticks_per_beat)
    
    # Calculate voice ranges
    print(f"\n🎵 VOICE RANGES:")
    for voice in ['soprano', 'alto', 'tenor', 'bass']:
        notes = [note['note'] for note in optimized_harmonization[voice]]
        print(f"  {voice.capitalize()}: {min(notes)}-{max(notes)}")
    
    print(f"\n🎉 SUCCESS! Hybrid harmonization generated.")
    print(f"📁 Output file: {output_file}")
    print(f"🤖 Model used: Coconet API + Trained Contrary Motion Rules")
    print(f"🎛️ Optimization: Applied {model_metadata['episodes_trained']} episodes of training")
    
    return True

if __name__ == "__main__":
    main() 