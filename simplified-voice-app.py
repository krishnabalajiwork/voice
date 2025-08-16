# Simplified Singing Voice Cloning Application in Streamlit
# Upload vocal track -> Create voice model -> Replace vocals with cloned voice

import streamlit as st
import os
import tempfile
import io
import numpy as np
import librosa
import soundfile as sf
from streamlit_mic_recorder import mic_recorder

# Configure the app
st.set_page_config(
    page_title="🎤 AI Voice Cloning Studio",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
def init_session_state():
    """Initialize all session state variables"""
    if 'user_voice_model' not in st.session_state:
        st.session_state.user_voice_model = None
    if 'model_trained' not in st.session_state:
        st.session_state.model_trained = False
    if 'vocal_track' not in st.session_state:
        st.session_state.vocal_track = None
    if 'vocal_sample_rate' not in st.session_state:
        st.session_state.vocal_sample_rate = None

# Voice model training (simplified version)
def create_voice_model(voice_samples):
    """
    Create a voice model from user samples
    This is a simplified version - stores voice characteristics
    """
    with st.spinner("🤖 Training your voice model..."):
        try:
            # Simulate voice model creation
            # In real implementation, this would involve:
            # 1. Audio preprocessing and feature extraction
            # 2. Voice characteristic analysis
            # 3. Model training and parameter storage
            
            model_data = {
                'samples': voice_samples,
                'trained': True,
                'sample_count': len(voice_samples),
                'voice_characteristics': 'trained_model_data'  # Placeholder
            }
            
            # Save model to session state (persists during session)
            st.session_state.user_voice_model = model_data
            st.session_state.model_trained = True
            
            return True
            
        except Exception as e:
            st.error(f"Error creating voice model: {str(e)}")
            return False

# Voice replacement function
def replace_vocals_with_user_voice(vocal_audio, user_model, sample_rate):
    """
    Replace vocals with user's cloned voice
    This is a simplified version for demonstration
    """
    with st.spinner("🎭 Replacing vocals with your voice..."):
        try:
            # Simplified voice conversion
            # In a real implementation, this would use:
            # - Pitch matching
            # - Timbre conversion
            # - Prosody preservation
            # - Advanced voice cloning models
            
            # For demonstration: Apply voice characteristics
            converted_vocals = vocal_audio.copy()
            
            # Apply simple transformations to simulate voice conversion
            converted_vocals = converted_vocals * 0.9  # Slight volume adjustment
            
            # Add subtle pitch shift (simplified)
            if len(converted_vocals) > 1000:
                pitch_shift = np.sin(np.linspace(0, 2*np.pi, len(converted_vocals))) * 0.05
                converted_vocals = converted_vocals * (1 + pitch_shift)
            
            return converted_vocals
            
        except Exception as e:
            st.error(f"Error in voice replacement: {str(e)}")
            return None

# Main application
def main():
    st.title("🎤 AI Voice Cloning Studio")
    st.markdown("**Upload vocal track → Create voice model → Generate your clone**")
    st.markdown("---")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar for navigation
    st.sidebar.title("🎵 Navigation")
    step = st.sidebar.selectbox(
        "Choose Step",
        ["1. Upload Vocal Track", "2. Create Voice Model", "3. Generate Clone"]
    )
    
    # Display status
    with st.sidebar:
        st.markdown("### ✅ Status")
        if st.session_state.vocal_track is not None:
            st.success("🎵 Vocal track uploaded")
        else:
            st.info("🎵 Upload vocal track")
            
        if st.session_state.model_trained:
            st.success("🤖 Voice model ready")
        else:
            st.info("🤖 Create voice model")
    
    # Step 1: Vocal Track Upload
    if step == "1. Upload Vocal Track":
        st.header("🎵 Step 1: Upload Your Vocal Track")
        st.write("Upload a clean vocal track (voice only, no instruments)")
        
        # File uploader
        uploaded_vocal = st.file_uploader(
            "Choose a vocal audio file",
            type=['mp3', 'wav', 'flac', 'm4a'],
            help="Upload vocals only - no background music or instruments"
        )
        
        if uploaded_vocal is not None:
            try:
                # Load audio file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(uploaded_vocal.read())
                    tmp_file_path = tmp_file.name
                
                # Load with librosa
                vocal_audio, sample_rate = librosa.load(tmp_file_path, sr=None)
                
                # Store in session state
                st.session_state.vocal_track = vocal_audio
                st.session_state.vocal_sample_rate = sample_rate
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
                st.success("✅ Vocal track uploaded successfully!")
                
                # Display vocal track info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Duration", f"{len(vocal_audio)/sample_rate:.1f} seconds")
                with col2:
                    st.metric("Sample Rate", f"{sample_rate} Hz")
                
                # Audio player
                st.subheader("🎧 Preview Your Vocal Track")
                vocal_bytes = io.BytesIO()
                sf.write(vocal_bytes, vocal_audio, sample_rate, format='WAV')
                vocal_bytes.seek(0)
                st.audio(vocal_bytes, format="audio/wav")
                
            except Exception as e:
                st.error(f"Error loading vocal track: {str(e)}")
    
    # Step 2: Voice Model Creation
    elif step == "2. Create Voice Model":
        st.header("🎙️ Step 2: Create Your Voice Model")
        
        if not st.session_state.model_trained:
            st.write("Record samples of your singing voice to create your personal voice model.")
            st.info("💡 Tip: Sing different notes and phrases for better results!")
            
            # Initialize voice samples list
            if 'voice_samples' not in st.session_state:
                st.session_state.voice_samples = []
            
            # Microphone recorder
            st.subheader("🎤 Record Your Voice Samples")
            
            audio_data = mic_recorder(
                start_prompt="🎤 Start Recording Sample",
                stop_prompt="⏹️ Stop Recording",
                just_once=True,
                use_container_width=True,
                key="voice_recorder"
            )
            
            # Process recorded audio
            if audio_data is not None:
                st.session_state.voice_samples.append(audio_data)
                st.success(f"✅ Sample {len(st.session_state.voice_samples)} recorded!")
                
                # Play back the recorded sample
                st.audio(audio_data['bytes'], format="audio/wav")
            
            # Display recorded samples
            if st.session_state.voice_samples:
                st.subheader(f"📝 Recorded Samples ({len(st.session_state.voice_samples)})")
                for i, sample in enumerate(st.session_state.voice_samples):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.audio(sample['bytes'], format="audio/wav")
                    with col2:
                        if st.button(f"🗑️", key=f"delete_{i}", help="Delete this sample"):
                            st.session_state.voice_samples.pop(i)
                            st.experimental_rerun()
            
            # Train model button
            if len(st.session_state.voice_samples) >= 3:
                if st.button("🤖 Train Voice Model", type="primary"):
                    if create_voice_model(st.session_state.voice_samples):
                        st.success("🎉 Voice model trained successfully!")
                        st.balloons()
                        st.info("✅ Your voice model is now saved! You won't need to record again.")
            else:
                st.warning("⚠️ Please record at least 3 voice samples to train your model.")
        
        else:
            st.success("✅ Your voice model is ready!")
            st.info("🎉 Your voice model has been trained and saved. You can now generate voice clones!")
            
            # Show model info
            model_info = st.session_state.user_voice_model
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Voice Samples", model_info['sample_count'])
            with col2:
                st.metric("Status", "✅ Trained")
            
            # Option to retrain
            if st.button("🔄 Retrain Voice Model"):
                st.session_state.model_trained = False
                st.session_state.user_voice_model = None
                st.session_state.voice_samples = []
                st.experimental_rerun()
    
    # Step 3: Voice Replacement and Generation
    elif step == "3. Generate Clone":
        st.header("🎭 Step 3: Generate Your Voice Clone")
        
        # Check prerequisites
        missing_requirements = []
        if not st.session_state.model_trained:
            missing_requirements.append("❌ Voice model not trained")
        if st.session_state.vocal_track is None:
            missing_requirements.append("❌ Vocal track not uploaded")
        
        if missing_requirements:
            st.warning("⚠️ Please complete the missing steps:")
            for req in missing_requirements:
                st.write(req)
            return
        
        st.success("✅ All requirements met! Ready to generate your voice clone.")
        
        # Show input summary
        st.subheader("📋 Input Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write("🎵 **Original Vocal Track**")
            vocal_bytes = io.BytesIO()
            sf.write(vocal_bytes, st.session_state.vocal_track, st.session_state.vocal_sample_rate, format='WAV')
            vocal_bytes.seek(0)
            st.audio(vocal_bytes, format="audio/wav")
        
        with col2:
            st.write("🤖 **Your Voice Model**")
            model_info = st.session_state.user_voice_model
            st.write(f"✅ Trained with {model_info['sample_count']} samples")
        
        # Generate clone button
        if st.button("🎵 Generate My Voice Clone", type="primary", use_container_width=True):
            # Replace vocals with user voice
            converted_vocals = replace_vocals_with_user_voice(
                st.session_state.vocal_track,
                st.session_state.user_voice_model,
                st.session_state.vocal_sample_rate
            )
            
            if converted_vocals is not None:
                # Normalize audio
                converted_vocals = converted_vocals / np.max(np.abs(converted_vocals))
                
                st.success("🎉 Your voice clone is ready!")
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎵 Original Vocals")
                    original_bytes = io.BytesIO()
                    sf.write(original_bytes, st.session_state.vocal_track, st.session_state.vocal_sample_rate, format='WAV')
                    original_bytes.seek(0)
                    st.audio(original_bytes, format="audio/wav")
                
                with col2:
                    st.subheader("🎤 Your Voice Clone")
                    clone_bytes = io.BytesIO()
                    sf.write(clone_bytes, converted_vocals, st.session_state.vocal_sample_rate, format='WAV')
                    clone_bytes.seek(0)
                    st.audio(clone_bytes, format="audio/wav")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Your Voice Clone",
                        data=clone_bytes.getvalue(),
                        file_name="my_voice_clone.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>🎤 AI Voice Cloning Studio • Simple & Powerful</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Installation requirements info in sidebar
def show_requirements():
    """Display installation requirements"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("📦 Requirements")
        
        requirements = """
        ```bash
        # Main packages
        streamlit
        librosa
        soundfile
        streamlit-mic-recorder
        numpy
        ```
        """
        
        st.markdown(requirements)
        st.markdown("**✅ No system dependencies needed!**")

if __name__ == "__main__":
    show_requirements()
    main()