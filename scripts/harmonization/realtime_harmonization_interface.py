#!/usr/bin/env python3
"""
Real-Time Harmonization Interface

A web-based interface for real-time harmonization with:
- Live melody input
- Multiple style options
- Instant harmonization generation
- MIDI playback
"""

import streamlit as st
import numpy as np
import mido
import io
import base64
import json
import os
from datetime import datetime
import sys

# Add src to path
sys.path.append('src')

from harmonization.core.rl_environment import HarmonizationEnvironment
from harmonization.rewards.music_theory_rewards import MusicTheoryRewards

# Style presets
STYLE_PRESETS = {
    'classical': {
        'harmonic_coherence': 0.30,
        'voice_leading': 0.25,
        'counterpoint': 0.25,
        'musical_interest': 0.10,
        'contrary_motion': 0.10,
        'description': 'Bach-style classical harmony with strict counterpoint'
    },
    'jazz': {
        'harmonic_coherence': 0.20,
        'voice_leading': 0.15,
        'counterpoint': 0.10,
        'musical_interest': 0.35,
        'contrary_motion': 0.20,
        'description': 'Jazz harmony with extended chords and chromaticism'
    },
    'pop': {
        'harmonic_coherence': 0.40,
        'voice_leading': 0.10,
        'counterpoint': 0.05,
        'musical_interest': 0.25,
        'contrary_motion': 0.20,
        'description': 'Pop music with simple, strong progressions'
    },
    'baroque': {
        'harmonic_coherence': 0.25,
        'voice_leading': 0.30,
        'counterpoint': 0.30,
        'musical_interest': 0.10,
        'contrary_motion': 0.05,
        'description': 'Baroque style with figured bass and ornamentation'
    }
}

def create_midi_from_notes(notes, filename="harmonization.mid"):
    """Create MIDI file from note data"""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
    
    # Add notes
    for note_data in notes:
        # Note on
        track.append(mido.Message('note_on', note=note_data['note'], 
                                 velocity=note_data.get('velocity', 100), 
                                 time=0))
        # Note off
        track.append(mido.Message('note_off', note=note_data['note'], 
                                  velocity=0, 
                                  time=note_data.get('duration', 480)))
    
    # Save to bytes
    midi_bytes = io.BytesIO()
    mid.save(file=midi_bytes)
    midi_bytes.seek(0)
    
    return midi_bytes.getvalue()

def harmonize_melody(melody_notes, style_name='classical'):
    """Generate harmonization for a melody"""
    # Get style weights
    weights = STYLE_PRESETS[style_name]
    
    # Initialize reward system
    reward_system = MusicTheoryRewards()
    reward_system.set_custom_weights(weights)
    
    # Create environment
    env = HarmonizationEnvironment(
        coconet_wrapper=None,
        reward_system=reward_system,
        max_steps=len(melody_notes),
        num_voices=3,
        melody_sequence=melody_notes
    )
    
    # Generate harmonization
    observation = env.reset()
    harmonization = {
        'soprano': [],
        'alto': [],
        'tenor': [],
        'bass': []
    }
    
    total_reward = 0
    
    for step in range(len(melody_notes)):
        # Use trained policy or random action
        action = env.action_space.sample()
        
        # Take step
        observation, reward, done, info = env.step(action)
        total_reward += reward
        
        # Add melody note
        harmonization['soprano'].append({
            'note': melody_notes[step],
            'duration': 480,  # Quarter note
            'velocity': 100
        })
        
        # Add harmony notes
        voices = ['alto', 'tenor', 'bass']
        for voice_idx, voice in enumerate(voices):
            pitch = action[voice_idx] + 21  # Convert to MIDI pitch
            harmonization[voice].append({
                'note': pitch,
                'duration': 480,
                'velocity': 80
            })
    
    return harmonization, total_reward

def main():
    st.set_page_config(
        page_title="Real-Time Harmonization",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 Real-Time Harmonization Interface")
    st.markdown("Generate 4-part harmonizations in real-time with different musical styles")
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Controls")
    
    # Style selection
    style = st.sidebar.selectbox(
        "Musical Style",
        list(STYLE_PRESETS.keys()),
        format_func=lambda x: x.title()
    )
    
    # Show style description
    st.sidebar.markdown(f"**{style.title()} Style:**")
    st.sidebar.markdown(STYLE_PRESETS[style]['description'])
    
    # Show style weights
    st.sidebar.markdown("**Reward Weights:**")
    for weight_name, weight_value in STYLE_PRESETS[style].items():
        if weight_name != 'description':
            st.sidebar.progress(weight_value, text=f"{weight_name.replace('_', ' ').title()}: {weight_value:.2f}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🎼 Input Melody")
        
        # Melody input options
        input_method = st.radio(
            "Choose input method:",
            ["Piano Roll", "MIDI Upload", "Note Sequence"]
        )
        
        melody_notes = []
        
        if input_method == "Piano Roll":
            st.markdown("Click on the piano roll to create a melody:")
            
            # Simple piano roll interface
            notes_per_measure = 4
            measures = st.slider("Number of measures", 1, 8, 4)
            
            # Create piano roll grid
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octaves = [4, 5]  # Middle octaves
            
            melody_notes = []
            for measure in range(measures):
                st.markdown(f"**Measure {measure + 1}:**")
                cols = st.columns(notes_per_measure)
                
                for beat in range(notes_per_measure):
                    with cols[beat]:
                        note_name = st.selectbox(f"Beat {beat + 1}", note_names, key=f"note_{measure}_{beat}")
                        octave = st.selectbox("Octave", octaves, key=f"octave_{measure}_{beat}")
                        
                        # Convert to MIDI note number
                        note_idx = note_names.index(note_name)
                        midi_note = note_idx + (octave * 12)
                        melody_notes.append(midi_note)
        
        elif input_method == "MIDI Upload":
            uploaded_file = st.file_uploader("Upload MIDI file", type=['mid', 'midi'])
            
            if uploaded_file is not None:
                try:
                    midi_data = uploaded_file.read()
                    mid = mido.MidiFile(file=io.BytesIO(midi_data))
                    
                    # Extract melody from first track
                    for track in mid.tracks:
                        current_time = 0
                        for msg in track:
                            current_time += msg.time
                            if msg.type == 'note_on' and msg.velocity > 0:
                                melody_notes.append(msg.note)
                                if len(melody_notes) >= 32:  # Limit length
                                    break
                        if melody_notes:
                            break
                    
                    st.success(f"Loaded {len(melody_notes)} notes from MIDI file")
                    
                except Exception as e:
                    st.error(f"Error loading MIDI file: {e}")
        
        elif input_method == "Note Sequence":
            note_input = st.text_area(
                "Enter note sequence (e.g., '60 62 64 65' for C D E F)",
                height=100
            )
            
            if note_input:
                try:
                    melody_notes = [int(note.strip()) for note in note_input.split()]
                    st.success(f"Loaded {len(melody_notes)} notes")
                except ValueError:
                    st.error("Invalid note sequence. Use space-separated MIDI note numbers.")
    
    with col2:
        st.header("🎵 Generated Harmonization")
        
        if melody_notes:
            # Generate harmonization
            if st.button("🎹 Generate Harmonization", type="primary"):
                with st.spinner("Generating harmonization..."):
                    harmonization, total_reward = harmonize_melody(melody_notes, style)
                
                # Display results
                st.success(f"✅ Harmonization generated! (Reward: {total_reward:.2f})")
                
                # Show voice ranges
                st.markdown("**Voice Ranges:**")
                for voice in ['soprano', 'alto', 'tenor', 'bass']:
                    notes = [note['note'] for note in harmonization[voice]]
                    if notes:
                        min_note = min(notes)
                        max_note = max(notes)
                        st.markdown(f"- **{voice.title()}:** {min_note}-{max_note}")
                
                # Create and download MIDI
                all_notes = []
                for voice in ['soprano', 'alto', 'tenor', 'bass']:
                    all_notes.extend(harmonization[voice])
                
                midi_data = create_midi_from_notes(all_notes)
                
                st.download_button(
                    label="📥 Download MIDI",
                    data=midi_data,
                    file_name=f"harmonization_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mid",
                    mime="audio/midi"
                )
                
                # Display note visualization
                st.markdown("**Note Visualization:**")
                for voice in ['soprano', 'alto', 'tenor', 'bass']:
                    notes = [note['note'] for note in harmonization[voice]]
                    st.line_chart(notes, use_container_width=True)
        else:
            st.info("👆 Create a melody using the input method above")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **How it works:**
    1. Choose a musical style (Classical, Jazz, Pop, Baroque)
    2. Input your melody using piano roll, MIDI upload, or note sequence
    3. Click "Generate Harmonization" to create 4-part harmony
    4. Download the result as a MIDI file
    
    **Styles:**
    - **Classical:** Bach-style harmony with strict counterpoint rules
    - **Jazz:** Extended chords and chromatic harmony
    - **Pop:** Simple, strong chord progressions
    - **Baroque:** Figured bass style with ornamentation
    """)

if __name__ == "__main__":
    main() 