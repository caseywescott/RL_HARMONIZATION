#!/usr/bin/env python3
"""
Debug MIDI timing to understand the actual structure
"""

import mido

def debug_midi_timing(midi_file):
    """Debug the MIDI file timing"""
    print(f"=== DEBUGGING MIDI TIMING: {midi_file} ===")
    
    mid = mido.MidiFile(midi_file)
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    print(f"Length: {mid.length} seconds")
    print(f"Number of tracks: {len(mid.tracks)}")
    
    for track_num, track in enumerate(mid.tracks):
        print(f"\n--- Track {track_num} ---")
        print(f"Number of messages: {len(track)}")
        
        current_time = 0
        note_events = []
        
        for i, msg in enumerate(track):
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                note_events.append({
                    'note': msg.note,
                    'time': current_time,
                    'velocity': msg.velocity,
                    'message_index': i
                })
                print(f"  Note ON:  {msg.note} at {current_time} ticks (velocity: {msg.velocity})")
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                print(f"  Note OFF: {msg.note} at {current_time} ticks")
            elif msg.type == 'set_tempo':
                tempo = mido.tempo2bpm(msg.tempo)
                print(f"  Tempo: {tempo} BPM")
            elif msg.type == 'time_signature':
                print(f"  Time signature: {msg.numerator}/{msg.denominator}")
            elif msg.type == 'key_signature':
                print(f"  Key signature: {msg.key}")
        
        # Calculate note durations
        print(f"\nNote durations in track {track_num}:")
        for i, note in enumerate(note_events):
            # Find corresponding note_off
            note_off_time = None
            current_time = 0
            for msg in track:
                current_time += msg.time
                if ((msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) 
                    and msg.note == note['note'] and current_time > note['time']):
                    note_off_time = current_time
                    break
            
            if note_off_time:
                duration = note_off_time - note['time']
                duration_seconds = mido.tick2second(duration, mid.ticks_per_beat, mido.MetaMessage('set_tempo', tempo=500000))
                print(f"  Note {note['note']}: {duration} ticks = {duration_seconds:.3f} seconds")
            else:
                print(f"  Note {note['note']}: No note_off found!")

if __name__ == "__main__":
    debug_midi_timing("realms2_idea.midi") 