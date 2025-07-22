#!/usr/bin/env python3
"""
Simple Proper Harmonization

A straightforward approach that creates consonant harmonies
"""

import pretty_midi
import io

def create_simple_harmonization(midi_data: bytes):
    """
    Create a simple but proper 4-part harmonization
    """
    try:
        # Parse MIDI data
        midi = pretty_midi.PrettyMIDI(io.BytesIO(midi_data))
        
        if not midi.instruments:
            return None
        
        # Extract melody (first track)
        melody_track = midi.instruments[0]
        melody_notes = []
        
        for note in melody_track.notes:
            melody_notes.append({
                'pitch': note.pitch,
                'start': note.start,
                'end': note.end,
                'velocity': note.velocity
            })
        
        # Create harmonized MIDI
        harmonized_midi = pretty_midi.PrettyMIDI(initial_tempo=120)
        
        # Add melody track (Soprano)
        soprano_instrument = pretty_midi.Instrument(program=0, name="Soprano")
        for note_data in melody_notes:
            note = pretty_midi.Note(
                velocity=note_data['velocity'],
                pitch=note_data['pitch'],
                start=note_data['start'],
                end=note_data['end']
            )
            soprano_instrument.notes.append(note)
        harmonized_midi.instruments.append(soprano_instrument)
        
        # Create harmony voices with simple rules
        alto_instrument = pretty_midi.Instrument(program=48, name="Alto")
        tenor_instrument = pretty_midi.Instrument(program=49, name="Tenor")
        bass_instrument = pretty_midi.Instrument(program=50, name="Bass")
        
        for note_data in melody_notes:
            melody_pitch = note_data['pitch']
            
            # Simple harmonization rules that avoid dissonance
            # Alto: Third below melody (major or minor third)
            alto_pitch = melody_pitch - 4  # Major third below
            if alto_pitch < 55:  # If too low, use minor third
                alto_pitch = melody_pitch - 3
            alto_pitch = max(55, min(77, alto_pitch))  # Alto range
            
            # Tenor: Fifth below melody
            tenor_pitch = melody_pitch - 7  # Perfect fifth below
            tenor_pitch = max(43, min(65, tenor_pitch))  # Tenor range
            
            # Bass: Octave below melody
            bass_pitch = melody_pitch - 12  # Octave below
            bass_pitch = max(28, min(55, bass_pitch))  # Bass range
            
            # Create notes
            alto_note = pretty_midi.Note(
                velocity=note_data['velocity'],
                pitch=int(alto_pitch),
                start=note_data['start'],
                end=note_data['end']
            )
            alto_instrument.notes.append(alto_note)
            
            tenor_note = pretty_midi.Note(
                velocity=note_data['velocity'],
                pitch=int(tenor_pitch),
                start=note_data['start'],
                end=note_data['end']
            )
            tenor_instrument.notes.append(tenor_note)
            
            bass_note = pretty_midi.Note(
                velocity=note_data['velocity'],
                pitch=int(bass_pitch),
                start=note_data['start'],
                end=note_data['end']
            )
            bass_instrument.notes.append(bass_note)
        
        # Add harmony instruments
        harmonized_midi.instruments.append(alto_instrument)
        harmonized_midi.instruments.append(tenor_instrument)
        harmonized_midi.instruments.append(bass_instrument)
        
        return harmonized_midi
        
    except Exception as e:
        print(f"Error in simple harmonization: {e}")
        return None

def harmonize_midi_file(input_path: str, output_path: str):
    """
    Harmonize a MIDI file and save the result
    """
    try:
        with open(input_path, 'rb') as f:
            midi_data = f.read()
        
        harmonized_midi = create_simple_harmonization(midi_data)
        if harmonized_midi:
            harmonized_midi.write(output_path)
            print(f"✅ Simple harmonization saved to: {output_path}")
            return True
        else:
            print("❌ Failed to create harmonization")
            return False
    except Exception as e:
        print(f"❌ Error harmonizing file: {e}")
        return False

if __name__ == "__main__":
    # Test with the realms2 melody
    success = harmonize_midi_file(
        "realms2_idea.midi", 
        "simple_proper_harmonization.mid"
    )
    
    if success:
        print("🎵 Simple proper harmonization completed!")
    else:
        print("💥 Harmonization failed!") 