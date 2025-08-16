# Uses WORLD vocoder and mel-cepstral analysis for real voice transformation

import streamlit as st
import numpy as np
import librosa
import soundfile as sf
import io
import pyworld as pw
import pysptk
from streamlit_mic_recorder import mic_recorder

# Configure the app
st.set_page_config(
    page_title="🎤 Advanced Voice Morphing Studio",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
def init_session_state():
    if 'vocal_track' not in st.session_state:
        st.session_state.vocal_track = None
    if 'voice_samples' not in st.session_state:
        st.session_state.voice_samples = []
    if 'uploaded_samples' not in st.session_state:
        st.session_state.uploaded_samples = []
    if 'timbre_template' not in st.session_state:
        st.session_state.timbre_template = None

@st.cache_resource
def create_timbre_template(voice_samples, uploaded_samples):
    """Create timbre template from voice samples using mel-cepstral analysis"""
    try:
        all_mceps = []
        
        # Process recorded samples
        for sample in voice_samples:
            try:
                # Convert bytes to audio
                audio_bytes = io.BytesIO(sample['bytes'])
                wav, sr = librosa.load(audio_bytes, sr=16000, mono=True)
                
                if len(wav) > 1600:  # At least 0.1 seconds
                    # Extract spectral features using WORLD vocoder
                    f0, t = pw.harvest(wav.astype(np.float64), sr, frame_period=5.0)
                    sp = pw.cheaptrick(wav.astype(np.float64), f0, t, sr)
                    
                    # Convert to mel-cepstral coefficients
                    mcep = pysptk.sptk.mcep(np.log(sp + 1e-8), 24, 0.55)
                    all_mceps.append(mcep.mean(axis=0))
                    
            except Exception as e:
                st.warning(f"Skipped one recorded sample: {str(e)}")
                continue
        
        # Process uploaded samples
        for uploaded_file in uploaded_samples:
            try:
                uploaded_file.seek(0)
                wav, sr = librosa.load(uploaded_file, sr=16000, mono=True)
                
                if len(wav) > 1600:
                    f0, t = pw.harvest(wav.astype(np.float64), sr, frame_period=5.0)
                    sp = pw.cheaptrick(wav.astype(np.float64), f0, t, sr)
                    mcep = pysptk.sptk.mcep(np.log(sp + 1e-8), 24, 0.55)
                    all_mceps.append(mcep.mean(axis=0))
                    
            except Exception as e:
                st.warning(f"Skipped uploaded file: {str(e)}")
                continue
        
        if len(all_mceps) > 0:
            # Average all mel-cepstral coefficients to create timbre template
            template = np.mean(all_mceps, axis=0)
            st.success(f"✅ Timbre template created from {len(all_mceps)} voice samples")
            return template
        else:
            st.error("Could not process any voice samples")
            return None
            
    except Exception as e:
        st.error(f"Error creating timbre template: {str(e)}")
        return None

def morph_vocal_track(vocal_audio, timbre_template, sample_rate, alpha=0.4):
    """Apply voice morphing using WORLD vocoder and spectral envelope modification"""
    try:
        # Resample to 16kHz for WORLD vocoder
        if sample_rate != 16000:
            vocal_audio = librosa.resample(vocal_audio, orig_sr=sample_rate, target_sr=16000)
            sample_rate = 16000
        
        # Ensure audio is in correct format for WORLD
        wav = vocal_audio.astype(np.float64)
        
        # WORLD vocoder analysis
        f0, t = pw.harvest(wav, sample_rate, frame_period=5.0)
        sp = pw.cheaptrick(wav, f0, t, sample_rate)
        ap = pw.d4c(wav, f0, t, sample_rate)
        
        # Convert spectral envelope to mel-cepstral coefficients
        mcep = pysptk.sptk.mcep(np.log(sp + 1e-8), 24, 0.55)
        
        # Morph spectral envelope toward user's timbre
        for i in range(len(mcep)):
            mcep[i] = alpha * mcep[i] + (1 - alpha) * timbre_template
        
        # Convert back to spectral envelope
        sp_morphed = np.exp(pysptk.sptk.mc2sp(mcep, 0.55, sample_rate // 2))
        
        # Synthesize morphed audio
        morphed_audio = pw.synthesize(f0, sp_morphed, ap, sample_rate, frame_period=5.0)
        
        # Normalize
        if np.max(np.abs(morphed_audio)) > 0:
            morphed_audio = morphed_audio / np.max(np.abs(morphed_audio)) * 0.9
        
        return morphed_audio.astype(np.float32), sample_rate
        
    except Exception as e:
        st.error(f"Voice morphing error: {str(e)}")
        return None, None

def main():
    init_session_state()
    
    st.title("🎤 Advanced Voice Morphing Studio")
    st.markdown("**Real voice transformation using WORLD vocoder and mel-cepstral analysis**")
    st.info("💡 This uses advanced signal processing to morph the vocal timbre toward your voice characteristics")
    
    # =================== STEP 1: UPLOAD VOCAL TRACK ===================
    st.header("🎵 Step 1: Upload Your Vocal Track")
    
    uploaded_vocal = st.file_uploader(
        "Choose vocal audio file (clean vocals only, no instruments)",
        type=['mp3', 'wav', 'flac', 'm4a', 'ogg'],
        help="Upload a clean vocal track for best results"
    )
    
    if uploaded_vocal is not None:
        try:
            # Load vocal track
            vocal_audio, sample_rate = librosa.load(uploaded_vocal, sr=None)
            st.session_state.vocal_track = (vocal_audio, sample_rate)
            
            st.success("✅ Vocal track uploaded successfully!")
            
            # Show audio info
            duration = len(vocal_audio) / sample_rate
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{duration:.1f} seconds")
            with col2:
                st.metric("Sample Rate", f"{sample_rate} Hz")
            with col3:
                st.metric("Channels", "Mono")
            
            # Audio preview
            st.subheader("🎧 Preview Original Vocal")
            vocal_bytes = io.BytesIO()
            sf.write(vocal_bytes, vocal_audio, sample_rate, format='WAV')
            vocal_bytes.seek(0)
            st.audio(vocal_bytes, format="audio/wav")
            
        except Exception as e:
            st.error(f"Error loading vocal track: {str(e)}")
    
    # =================== STEP 2: VOICE SAMPLES ===================
    if st.session_state.vocal_track is not None:
        st.markdown("---")
        st.header("🎙️ Step 2: Provide Your Voice Samples")
        st.info("📝 Record or upload 3-5 clear samples of YOUR voice (singing or speaking)")
        
        # Create tabs for recording vs uploading
        tab1, tab2 = st.tabs(["🎤 Record Voice", "📁 Upload Audio Files"])
        
        with tab1:
            st.subheader("Record Your Voice")
            st.write("Record short samples (3-10 seconds each) of your voice:")
            
            # Microphone recorder
            audio_data = mic_recorder(
                start_prompt="🎤 Start Recording Your Voice",
                stop_prompt="⏹️ Stop Recording",
                just_once=True,
                use_container_width=True,
                key=f"voice_recorder_{len(st.session_state.voice_samples)}"
            )
            
            if audio_data is not None:
                st.session_state.voice_samples.append(audio_data)
                st.success(f"✅ Voice sample {len(st.session_state.voice_samples)} recorded!")
            
            # Show recorded samples
            if st.session_state.voice_samples:
                st.write(f"**Recorded Samples: {len(st.session_state.voice_samples)}**")
                for i, sample in enumerate(st.session_state.voice_samples):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.audio(sample['bytes'], format="audio/wav")
                    with col2:
                        if st.button("🗑️", key=f"delete_rec_{i}", help="Delete sample"):
                            st.session_state.voice_samples.pop(i)
                            st.rerun()
        
        with tab2:
            st.subheader("Upload Voice Files")
            st.write("Upload audio files of your voice (any format, 3-30 seconds each):")
            
            uploaded_voice_files = st.file_uploader(
                "Select your voice audio files",
                type=['mp3', 'wav', 'flac', 'm4a', 'ogg'],
                accept_multiple_files=True,
                key="voice_files"
            )
            
            if uploaded_voice_files:
                st.session_state.uploaded_samples = uploaded_voice_files
                st.success(f"✅ {len(uploaded_voice_files)} voice files uploaded!")
                
                # Preview uploaded files
                for i, file in enumerate(uploaded_voice_files):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{file.name}** ({file.size/1024:.1f} KB)")
                        try:
                            file.seek(0)
                            st.audio(file, format="audio/wav")
                        except:
                            st.write("(Preview not available)")
                    with col2:
                        st.write(" ")  # Spacing
        
        # Calculate total samples
        total_samples = len(st.session_state.voice_samples) + len(st.session_state.uploaded_samples)
        
        # Create timbre template
        if total_samples >= 3:
            if st.button("🔬 Analyze My Voice Characteristics", type="primary", use_container_width=True):
                with st.spinner("Analyzing your voice timbre using mel-cepstral analysis..."):
                    template = create_timbre_template(
                        st.session_state.voice_samples,
                        st.session_state.uploaded_samples
                    )
                    
                    if template is not None:
                        st.session_state.timbre_template = template
                        st.success("🎉 Voice analysis complete! Your timbre template is ready.")
        else:
            st.warning(f"⚠️ Please provide at least 3 voice samples (currently: {total_samples})")
    
    # =================== STEP 3: VOICE MORPHING ===================
    if (st.session_state.vocal_track is not None and 
        st.session_state.timbre_template is not None):
        
        st.markdown("---")
        st.header("🎭 Step 3: Generate Voice-Morphed Audio")
        
        # Morphing strength slider
        alpha = st.slider(
            "Morphing Strength",
            min_value=0.1,
            max_value=0.8,
            value=0.4,
            step=0.1,
            help="Higher values = more of your voice characteristics"
        )
        
        strength_labels = {
            0.1: "Very Subtle",
            0.2: "Subtle", 
            0.3: "Moderate",
            0.4: "Strong",
            0.5: "Very Strong",
            0.6: "Intense",
            0.7: "Maximum",
            0.8: "Extreme"
        }
        
        st.write(f"**Morphing Level: {strength_labels.get(alpha, 'Custom')}**")
        
        # Generate morphed voice
        if st.button("🎵 Morph Voice Now!", type="primary", use_container_width=True):
            vocal_audio, sample_rate = st.session_state.vocal_track
            
            with st.spinner("🔧 Applying WORLD vocoder analysis..."):
                morphed_audio, morphed_sr = morph_vocal_track(
                    vocal_audio, 
                    st.session_state.timbre_template, 
                    sample_rate, 
                    alpha=alpha
                )
            
            if morphed_audio is not None:
                st.success("🎉 Voice morphing complete!")
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎵 Original Vocal")
                    original_bytes = io.BytesIO()
                    sf.write(original_bytes, vocal_audio, sample_rate, format='WAV')
                    original_bytes.seek(0)
                    st.audio(original_bytes, format="audio/wav")
                
                with col2:
                    st.subheader("🎤 Your Morphed Voice")
                    morphed_bytes = io.BytesIO()
                    sf.write(morphed_bytes, morphed_audio, morphed_sr, format='WAV')
                    morphed_bytes.seek(0)
                    st.audio(morphed_bytes, format="audio/wav")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Morphed Voice",
                        data=morphed_bytes.getvalue(),
                        file_name=f"morphed_voice_strength_{alpha}.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                
                # Analysis info
                st.info(f"🔬 Applied {alpha*100:.0f}% of your voice characteristics using advanced spectral morphing")
                
                # Reset option
                if st.button("🔄 Start Over", use_container_width=True):
                    for key in ['vocal_track', 'voice_samples', 'uploaded_samples', 'timbre_template']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>🎤 Advanced Voice Morphing Studio • Powered by WORLD Vocoder & Mel-Cepstral Analysis</p>
            <p><small>Free-tier compatible • No GPU required • Real voice transformation</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
