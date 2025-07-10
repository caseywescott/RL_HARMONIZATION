#!/usr/bin/env python3
"""
Generate 4-voice harmonization maximizing contrary motion
"""

import mido
from midiutil import MIDIFile
import os

def load_midi_with_correct_timing(midi_file):
    mid = mido.MidiFile(midi_file)
    print(f"Loading {midi_file}")
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    
    # Find tempo (default to 160 BPM if not found)
    tempo = 500000  # microseconds per beat (120 BPM)
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
    bpm = mido.tempo2bpm(tempo)
    print(f"Tempo: {bpm} BPM")
    
    notes = []
    for track_num, track in enumerate(mid.tracks):
        current_time = 0
        track_notes = []
        for msg in track:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                track_notes.append({
                    'note': msg.note,
                    'start_time': current_time,
                    'velocity': msg.velocity,
                    'duration': 0
                })
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                for note in reversed(track_notes):
                    if note['note'] == msg.note and note['duration'] == 0:
                        note['duration'] = current_time - note['start_time']
                        break
        track_notes = [note for note in track_notes if note['duration'] > 0]
        if track_notes:
            print(f"Track {track_num}: {len(track_notes)} notes")
            notes.extend(track_notes)
    notes.sort(key=lambda x: x['start_time'])
    print(f"Total notes: {len(notes)}")
    for i, note in enumerate(notes[:3]):
        start_seconds = mido.tick2second(note['start_time'], mid.ticks_per_beat, tempo)
        duration_seconds = mido.tick2second(note['duration'], mid.ticks_per_beat, tempo)
        print(f"  Note {i}: MIDI {note['note']} at {start_seconds:.2f}s for {duration_seconds:.2f}s")
    return notes, mid.ticks_per_beat, tempo

def contrary_motion_harmony(melody_notes):
    print("Generating 4-voice harmony (contrary motion)...")
    # Voice ranges
    soprano_range = (60, 84)
    alto_range = (48, 72)
    tenor_range = (36, 60)
    bass_range = (24, 48)
    
    soprano_notes = []
    alto_notes = []
    tenor_notes = []
    bass_notes = []
    
    # Start each voice at a reasonable interval from the melody
    prev = {
        'soprano': None,
        'alto': None,
        'tenor': None,
        'bass': None
    }
    for i, melody_note in enumerate(melody_notes):
        m = melody_note['note']
        # Soprano follows melody
        soprano = m
        # Determine melody direction
        if i == 0:
            direction = 0
        else:
            direction = m - melody_notes[i-1]['note']
        # Alto contrary motion
        if prev['alto'] is None:
            alto = m - 3
        else:
            if direction > 0:
                alto = prev['alto'] - 1  # move down
            elif direction < 0:
                alto = prev['alto'] + 1  # move up
            else:
                alto = prev['alto']  # stay
        # Tenor contrary motion
        if prev['tenor'] is None:
            tenor = m - 7
        else:
            if direction > 0:
                tenor = prev['tenor'] - 2
            elif direction < 0:
                tenor = prev['tenor'] + 2
            else:
                tenor = prev['tenor']
        # Bass contrary motion
        if prev['bass'] is None:
            bass = m - 12
        else:
            if direction > 0:
                bass = prev['bass'] - 3
            elif direction < 0:
                bass = prev['bass'] + 3
            else:
                bass = prev['bass']
        # Clamp to voice ranges
        if soprano < soprano_range[0]: soprano += 12
        if soprano > soprano_range[1]: soprano -= 12
        if alto < alto_range[0]: alto += 12
        if alto > alto_range[1]: alto -= 12
        if tenor < tenor_range[0]: tenor += 12
        if tenor > tenor_range[1]: tenor -= 12
        if bass < bass_range[0]: bass += 12
        if bass > bass_range[1]: bass -= 12
        # Store
        soprano_notes.append({
            'note': soprano,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        alto_notes.append({
            'note': alto,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        tenor_notes.append({
            'note': tenor,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        bass_notes.append({
            'note': bass,
            'start_time': melody_note['start_time'],
            'duration': melody_note['duration'],
            'velocity': melody_note['velocity']
        })
        prev['soprano'] = soprano
        prev['alto'] = alto
        prev['tenor'] = tenor
        prev['bass'] = bass
        print(f"Note {i}: S{soprano} A{alto} T{tenor} B{bass} (melody {m}, dir {direction})")
    return {
        'soprano': soprano_notes,
        'alto': alto_notes,
        'tenor': tenor_notes,
        'bass': bass_notes
    }

def save_4_voice_harmonization_with_correct_timing(melody_notes, voices, output_file, ticks_per_beat):
    print(f"Saving 4-voice harmonization to {output_file}")
    midi = MIDIFile(4)
    # Soprano
    midi.addTempo(0, 0, 160)
    for note in voices['soprano']:
        start_beat = note['start_time'] / ticks_per_beat
        duration_beat = note['duration'] / ticks_per_beat
        midi.addNote(0, 0, note['note'], start_beat, duration_beat, 90)
    # Alto
    midi.addTempo(1, 0, 160)
    for note in voices['alto']:
        start_beat = note['start_time'] / ticks_per_beat
        duration_beat = note['duration'] / ticks_per_beat
        midi.addNote(1, 0, note['note'], start_beat, duration_beat, 85)
    # Tenor
    midi.addTempo(2, 0, 160)
    for note in voices['tenor']:
        start_beat = note['start_time'] / ticks_per_beat
        duration_beat = note['duration'] / ticks_per_beat
        midi.addNote(2, 0, note['note'], start_beat, duration_beat, 80)
    # Bass
    midi.addTempo(3, 0, 160)
    for note in voices['bass']:
        start_beat = note['start_time'] / ticks_per_beat
        duration_beat = note['duration'] / ticks_per_beat
        midi.addNote(3, 0, note['note'], start_beat, duration_beat, 75)
    with open(output_file, 'wb') as f:
        midi.writeFile(f)
    print(f"✅ 4-voice harmonization saved: {output_file}")
    print(f"   - Track 0: Soprano")
    print(f"   - Track 1: Alto")
    print(f"   - Track 2: Tenor")
    print(f"   - Track 3: Bass")
    print(f"   - All voices maximize contrary motion with melody")

def main():
    print("🎵 4-VOICE CONTRARY MOTION HARMONIZATION")
    print("=" * 50)
    melody_file = "realms2_idea.midi"
    if not os.path.exists(melody_file):
        print(f"❌ Melody file not found: {melody_file}")
        return
    melody_notes, ticks_per_beat, tempo = load_midi_with_correct_timing(melody_file)
    if not melody_notes:
        print("❌ Failed to load melody")
        return
    voices = contrary_motion_harmony(melody_notes)
    output_file = "realms2_4voice_contrary_motion.mid"
    save_4_voice_harmonization_with_correct_timing(melody_notes, voices, output_file, ticks_per_beat)
    print(f"\n🎉 CONTRARY MOTION HARMONIZATION COMPLETE!")
    print(f"Input: {melody_file}")
    print(f"Output: {output_file}")
    print(f"Voices: Soprano, Alto, Tenor, Bass (contrary motion)")
    print(f"\nYou can now play {output_file} to hear the result!")

if __name__ == "__main__":
    main() 