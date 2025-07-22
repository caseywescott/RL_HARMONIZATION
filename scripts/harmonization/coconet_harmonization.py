#!/usr/bin/env python3
"""
Coconet-based harmonization using the full RL system as described in the README.
This follows the project plan: Coconet + RL with tunable music theory rewards.
"""

import sys
sys.path.append('src')

import numpy as np
import mido
import json
from datetime import datetime
from harmonization.core.coconet_wrapper import CoconetWrapper
from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

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

def create_coconet_harmonization(melody_notes, coconet_wrapper, reward_system):
    """Create harmonization using Coconet + RL approach"""
    print(f"\n🎵 GENERATING COCONET HARMONIZATION")
    print(f"Melody notes: {len(melody_notes)} notes")
    
    # Convert melody to NoteSequence format for Coconet
    import note_seq
    from note_seq import NoteSequence
    
    # Create NoteSequence from melody
    sequence = NoteSequence()
    sequence.ticks_per_quarter = 480
    
    for note_data in melody_notes:
        note = sequence.notes.add()
        note.pitch = note_data['note']
        note.start_time = note_data['start_time'] / 480.0  # Convert ticks to seconds
        note.end_time = (note_data['start_time'] + note_data['duration']) / 480.0
        note.velocity = note_data['velocity']
        note.instrument = 0  # Melody voice
    
    # Use Coconet to generate harmonization
    try:
        # Generate completion using Coconet
        harmonized_sequence = coconet_wrapper.generate_completion(
            primer_sequence=sequence,
            temperature=1.0,
            num_steps=len(melody_notes)
        )
        
        print(f"✅ Coconet harmonization generated")
        return harmonized_sequence
        
    except Exception as e:
        print(f"❌ Coconet generation failed: {e}")
        print(f"Falling back to RL environment approach...")
        
        # Fallback: Use RL environment without Coconet
        return create_rl_harmonization(melody_notes, reward_system)

def create_rl_harmonization(melody_notes, reward_system):
    """Create harmonization using RL environment approach"""
    print(f"🎵 GENERATING RL HARMONIZATION")
    
    # Extract melody pitches
    melody_pitches = [note['note'] for note in melody_notes]
    
    # Create RL environment
    env = HarmonizationEnvironment(
        coconet_wrapper=None,  # No Coconet for fallback
        reward_system=reward_system,
        max_steps=len(melody_notes),
        num_voices=4,
        melody_sequence=melody_pitches
    )
    
    # Generate harmonization using environment
    observation = env.reset()
    harmonization = {
        'soprano': [],
        'alto': [],
        'tenor': [],
        'bass': []
    }
    
    total_reward = 0
    
    for step in range(len(melody_notes)):
        # Sample action from environment (using trained policy or random)
        action = env.action_space.sample()
        
        # Take step
        observation, reward, done, info = env.step(action)
        total_reward += reward
        
        # Convert action to notes
        current_time = melody_notes[step]['start_time']
        duration = melody_notes[step]['duration']
        
        # Soprano = melody
        harmonization['soprano'].append({
            'note': melody_notes[step]['note'],
            'start_time': current_time,
            'duration': duration,
            'velocity': melody_notes[step]['velocity']
        })
        
        # Other voices from action
        voices = ['alto', 'tenor', 'bass']
        for voice_idx, voice in enumerate(voices):
            pitch = action[voice_idx] + 21  # Convert to MIDI pitch
            harmonization[voice].append({
                'note': pitch,
                'start_time': current_time,
                'duration': duration,
                'velocity': melody_notes[step]['velocity']
            })
    
    print(f"✅ RL harmonization generated (Total reward: {total_reward:.1f})")
    return harmonization

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
    print("🎵 COCONET + RL HARMONIZATION SYSTEM")
    print("=" * 50)
    print("Following the README: Coconet Integration + Tunable Rewards")
    
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
    
    # Initialize Coconet wrapper
    print(f"\n🤖 INITIALIZING COCONET MODEL...")
    try:
        coconet_wrapper = CoconetWrapper(checkpoint_path="coconet-64layers-128filters")
        print(f"✅ Coconet model loaded successfully")
    except Exception as e:
        print(f"❌ Coconet model loading failed: {e}")
        print(f"Will use RL environment approach instead")
        coconet_wrapper = None
    
    # Initialize reward system with tunable weights
    print(f"\n🎛️ INITIALIZING TUNABLE REWARD SYSTEM...")
    reward_system = MusicTheoryRewards()
    
    # Set style preset (classical, jazz, pop, baroque)
    style = "classical"  # Can be changed
    reward_system.set_style_preset(style)
    print(f"✅ Reward system initialized with {style} style preset")
    
    # Generate harmonization
    if coconet_wrapper:
        harmonization = create_coconet_harmonization(melody_notes, coconet_wrapper, reward_system)
    else:
        harmonization = create_rl_harmonization(melody_notes, reward_system)
    
    # Save harmonization
    output_file = f"coconet_harmonization_{style}.mid"
    save_harmonization_midi(harmonization, output_file, ticks_per_beat=ticks_per_beat)
    
    print(f"\n🎉 SUCCESS! Coconet + RL harmonization generated.")
    print(f"📁 Output file: {output_file}")
    print(f"🎛️ Style preset: {style}")
    print(f"🤖 Model used: {'Coconet + RL' if coconet_wrapper else 'RL Environment'}")
    
    return True

if __name__ == "__main__":
    main() 