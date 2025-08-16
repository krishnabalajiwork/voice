# Fixes audio format issues and adds file upload for voice samples

import streamlit as st
import os
import tempfile
import io
import numpy as np
import librosa
import soundfile as sf
from streamlit_mic_recorder import mic_recorder
from scipy import signal
import wave

# Configure the app
st.set_page_config(
    page_title="🎤 AI Voice Cloning Studio",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
def init_session_state():
    if 'vocal_track' not in st.session_state:
        st.session_state.vocal_track = None
    if 'vocal_sample_rate' not in st.session_state:
        st.session_state.vocal_sample_rate = None
    if 'voice_model' not in st.session_state:
        st.session_state.voice_model = None
    if 'voice_samples' not in st.session_state:
        st.session_state.voice_samples = []

# Fixed audio loading function
def load_audio_safely(audio_source, source_type="file"):
    """Safely load audio from different sources"""
    try:
        if source_type == "file":
            # For uploaded files
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_source.read())
                tmp_file_path = tmp_file.name
            
            audio, sr = librosa.load(tmp_file_path, sr=22050)
            os.unlink(tmp_file_path)
            return audio, sr
            
        elif source_type == "bytes":
            # For microphone recorded bytes
            # Save bytes to temporary file first
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_source)
                tmp_file_path = tmp_file.name
            
            audio, sr = librosa.load(tmp_file_path, sr=22050)
            os.unlink(tmp_file_path)
            return audio, sr
            
    except Exception as e:
        st.error(f"Audio loading error: {str(e)}")
        return None, None

# Improved voice analysis with error handling
def analyze_voice_characteristics(voice_samples, sample_sources):
    """Extract voice characteristics with better error handling"""
    characteristics = {
        'pitch_shift': 0,
        'formant_shift': 0, 
        'voice_brightness': 1.0,
        'breathiness': 0.0,
        'vibrato_rate': 0.0
    }
    
    if not voice_samples and not sample_sources:
        return characteristics
    
    all_audio = []
    
    try:
        # Process recorded samples (microphone)
        for sample in voice_samples:
            try:
                audio, sr = load_audio_safely(sample['bytes'], "bytes")
                if audio is not None:
                    all_audio.extend(audio)
            except Exception as e:
                st.warning(f"Skipped one recorded sample due to format issue: {str(e)}")
                continue
        
        # Process uploaded samples (files)
        for uploaded_file in sample_sources:
            try:
                # Reset file pointer
                uploaded_file.seek(0)
                audio, sr = load_audio_safely(uploaded_file, "file")
                if audio is not None:
                    all_audio.extend(audio)
            except Exception as e:
                st.warning(f"Skipped uploaded file {uploaded_file.name}: {str(e)}")
                continue
        
        if len(all_audio) > 1000:
            all_audio = np.array(all_audio)
            
            # Extract pitch (fundamental frequency)
            try:
                pitches, magnitudes = librosa.core.piptrack(y=all_audio, sr=22050, fmin=50, fmax=2000)
                pitch_values = pitches[pitches > 0]
                
                if len(pitch_values) > 0:
                    avg_pitch = np.median(pitch_values)  # Use median for robustness
                    reference_pitch = 220  # A3
                    characteristics['pitch_shift'] = np.log2(avg_pitch / reference_pitch) * 12
                    
                    # Clamp pitch shift to reasonable range
                    characteristics['pitch_shift'] = np.clip(characteristics['pitch_shift'], -12, 12)
            except Exception as e:
                st.warning(f"Pitch analysis failed, using default: {str(e)}")
            
            # Spectral analysis for brightness
            try:
                stft = librosa.stft(all_audio)
                magnitude = np.abs(stft)
                freq_bins = librosa.fft_frequencies(sr=22050, n_fft=2048)
                
                high_freq_energy = np.mean(magnitude[freq_bins > 2000])
                low_freq_energy = np.mean(magnitude[freq_bins < 1000])
                
                if low_freq_energy > 0:
                    brightness = high_freq_energy / low_freq_energy
                    characteristics['voice_brightness'] = np.clip(brightness, 0.5, 3.0)
            except Exception as e:
                st.warning(f"Brightness analysis failed, using default: {str(e)}")
            
            # MFCC for formant approximation
            try:
                mfcc = librosa.feature.mfcc(y=all_audio, sr=22050, n_mfcc=13)
                formant_feature = np.mean(mfcc[1:4])  # Use first few MFCC coefficients
                characteristics['formant_shift'] = np.clip(formant_feature / 20, -0.5, 0.5)
            except Exception as e:
                st.warning(f"Formant analysis failed, using default: {str(e)}")
            
            st.success(f"✅ Voice analyzed: Pitch {characteristics['pitch_shift']:.1f} semitones, Brightness {characteristics['voice_brightness']:.2f}")
            
    except Exception as e:
        st.error(f"Voice analysis error: {str(e)}, using default characteristics")
    
    return characteristics

# Create voice model
def create_voice_model(voice_samples, uploaded_samples, method="recorded"):
    """Create voice model from samples or use default"""
    try:
        if method == "sample":
            model_data = {
                'type': 'sample_model',
                'characteristics': {
                    'pitch_shift': 3.0,
                    'formant_shift': 0.15,
                    'voice_brightness': 1.4,
                    'breathiness': 0.1,
                    'vibrato_rate': 0.05
                },
                'trained': True
            }
        else:
            # Analyze voice samples
            characteristics = analyze_voice_characteristics(voice_samples, uploaded_samples)
            total_samples = len(voice_samples) + len(uploaded_samples)
            
            model_data = {
                'type': 'personal_model', 
                'samples': voice_samples,
                'uploaded_samples': uploaded_samples,
                'sample_count': total_samples,
                'characteristics': characteristics,
                'trained': True
            }
        
        st.session_state.voice_model = model_data
        return True
    except Exception as e:
        st.error(f"Error creating voice model: {str(e)}")
        return False

# Enhanced voice transformation
def clone_voice(original_vocals, voice_model, sample_rate):
    """Apply voice transformation with fallback options"""
    try:
        characteristics = voice_model['characteristics']
        cloned_vocals = original_vocals.copy()
        
        # 1. Pitch shifting (most important)
        pitch_shift = characteristics['pitch_shift']
        if abs(pitch_shift) > 0.1:
            try:
                cloned_vocals = librosa.effects.pitch_shift(
                    cloned_vocals, sr=sample_rate, n_steps=pitch_shift
                )
            except Exception as e:
                st.warning(f"Pitch shift failed: {str(e)}, trying alternative method")
                # Fallback: simple speed change
                if pitch_shift > 0:
                    # Higher pitch - speed up slightly
                    speed_factor = 1 + (pitch_shift * 0.02)
                    indices = np.arange(0, len(cloned_vocals), speed_factor)
                    cloned_vocals = np.interp(range(len(cloned_vocals)), indices, cloned_vocals)
        
        # 2. Formant shifting through spectral manipulation
        formant_shift = characteristics['formant_shift']
        if abs(formant_shift) > 0.02:
            try:
                stft = librosa.stft(cloned_vocals)
                magnitude = np.abs(stft)
                phase = np.angle(stft)
                
                # Shift formants
                formant_factor = 1 + formant_shift
                freq_bins, time_frames = magnitude.shape
                new_magnitude = np.zeros_like(magnitude)
                
                for i in range(time_frames):
                    shifted_freqs = np.arange(freq_bins) * formant_factor
                    shifted_freqs = np.clip(shifted_freqs, 0, freq_bins-1)
                    new_magnitude[:, i] = np.interp(range(freq_bins), shifted_freqs, magnitude[:, i])
                
                new_stft = new_magnitude * np.exp(1j * phase)
                cloned_vocals = librosa.istft(new_stft, length=len(original_vocals))
                
            except Exception as e:
                st.warning(f"Formant shifting failed: {str(e)}")
        
        # 3. Brightness adjustment
        brightness = characteristics['voice_brightness']
        if abs(brightness - 1.0) > 0.1:
            try:
                if brightness > 1.2:
                    # Boost high frequencies
                    b, a = signal.butter(2, 3000/(sample_rate/2), btype='high')
                    high_freq = signal.filtfilt(b, a, cloned_vocals)
                    cloned_vocals = cloned_vocals + high_freq * (brightness - 1.0) * 0.2
                elif brightness < 0.8:
                    # Reduce high frequencies
                    b, a = signal.butter(2, 4000/(sample_rate/2), btype='low')
                    cloned_vocals = signal.filtfilt(b, a, cloned_vocals)
            except Exception as e:
                st.warning(f"Brightness adjustment failed: {str(e)}")
        
        # 4. Normalize and clean
        cloned_vocals = np.nan_to_num(cloned_vocals)
        if np.max(np.abs(cloned_vocals)) > 0:
            cloned_vocals = cloned_vocals / np.max(np.abs(cloned_vocals)) * 0.9
        
        return cloned_vocals
        
    except Exception as e:
        st.error(f"Voice cloning error: {str(e)}")
        # Ultimate fallback: simple pitch shift
        try:
            return librosa.effects.pitch_shift(original_vocals, sr=sample_rate, n_steps=2.0)
        except:
            st.error("All transformation methods failed, returning original audio")
            return original_vocals

# Main app
def main():
    init_session_state()
    
    st.title("🎤 Enhanced AI Voice Cloning Studio")
    st.markdown("**Real voice transformation with upload & recording options!**")
    
    # =================== STEP 1: UPLOAD VOCAL TRACK ===================
    st.header("🎵 Step 1: Upload Your Vocal Track")
    
    uploaded_file = st.file_uploader(
        "Choose your vocal audio file (vocals only, no instruments)",
        type=['mp3', 'wav', 'flac', 'm4a'],
        help="Upload a clean vocal track without background music"
    )
    
    if uploaded_file is not None:
        try:
            vocal_audio, sample_rate = load_audio_safely(uploaded_file, "file")
            
            if vocal_audio is not None:
                st.session_state.vocal_track = vocal_audio
                st.session_state.vocal_sample_rate = sample_rate
                
                st.success("✅ Vocal track uploaded successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Duration", f"{len(vocal_audio)/sample_rate:.1f} seconds")
                with col2:
                    st.metric("Sample Rate", f"{sample_rate} Hz")
                
                # Audio preview
                st.subheader("🎧 Preview Your Vocal Track")
                vocal_bytes = io.BytesIO()
                sf.write(vocal_bytes, vocal_audio, sample_rate, format='WAV')
                vocal_bytes.seek(0)
                st.audio(vocal_bytes, format="audio/wav")
            
        except Exception as e:
            st.error(f"Error loading vocal track: {str(e)}")
    
    # =================== STEP 2: VOICE MODEL ===================
    if st.session_state.vocal_track is not None:
        st.markdown("---")
        st.header("🤖 Step 2: Choose Your Voice Model")
        
        model_option = st.radio(
            "Select voice model type:",
            ["🎤 Record/Upload My Voice (Personalized Analysis)", "🎭 Use Sample Voice (+3 semitones higher)"],
            help="Analyze your voice or use a sample model"
        )
        
        if model_option == "🎤 Record/Upload My Voice (Personalized Analysis)":
            st.subheader("Provide Your Voice Samples")
            
            # Tab for recording vs uploading
            tab1, tab2 = st.tabs(["🎤 Record Voice", "📁 Upload Audio Files"])
            
            with tab1:
                st.info("💡 Record 2-3 voice samples singing or speaking clearly")
                
                # Voice recorder
                audio_data = mic_recorder(
                    start_prompt="🎤 Start Recording Your Voice",
                    stop_prompt="⏹️ Stop Recording", 
                    just_once=True,
                    use_container_width=True,
                    key=f"recorder_{len(st.session_state.voice_samples)}"
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
                            if st.button("🗑️", key=f"delete_rec_{i}"):
                                st.session_state.voice_samples.pop(i)
                                st.rerun()
            
            with tab2:
                st.info("💡 Upload 2-3 audio files of your voice (any format)")
                
                # Initialize uploaded samples list
                if 'uploaded_voice_samples' not in st.session_state:
                    st.session_state.uploaded_voice_samples = []
                
                # File uploader for voice samples
                uploaded_voice_files = st.file_uploader(
                    "Upload your voice audio files",
                    type=['mp3', 'wav', 'flac', 'm4a', 'ogg'],
                    accept_multiple_files=True,
                    key="voice_files_uploader"
                )
                
                if uploaded_voice_files:
                    # Update session state with new uploads
                    st.session_state.uploaded_voice_samples = uploaded_voice_files
                    st.success(f"✅ {len(uploaded_voice_files)} voice files uploaded!")
                    
                    # Preview uploaded files
                    for i, file in enumerate(uploaded_voice_files):
                        st.write(f"**{file.name}** ({file.size/1024:.1f} KB)")
                        
                        # Try to preview the audio
                        try:
                            file.seek(0)
                            st.audio(file, format="audio/wav")
                        except Exception as e:
                            st.warning(f"Cannot preview {file.name}: {str(e)}")
            
            # Calculate total samples
            total_samples = len(st.session_state.voice_samples) + len(st.session_state.get('uploaded_voice_samples', []))
            
            if total_samples >= 2:
                if st.button("🔬 Analyze My Voice Characteristics", type="primary", use_container_width=True):
                    with st.spinner("Analyzing your voice characteristics (pitch, formants, brightness)..."):
                        uploaded_samples = st.session_state.get('uploaded_voice_samples', [])
                        if create_voice_model(st.session_state.voice_samples, uploaded_samples, "recorded"):
                            st.success("🎉 Your voice has been analyzed and model created!")
            else:
                st.warning(f"⚠️ Provide at least 2 voice samples (currently: {total_samples})")
        
        else:  # Use Sample Voice
            st.subheader("Use Sample Voice Model")
            st.info("📝 Sample model: +3 semitones higher pitch, brighter tone, enhanced formants")
            
            if st.button("🎭 Use Sample Voice Model", type="primary", use_container_width=True):
                with st.spinner("Loading sample voice model..."):
                    if create_voice_model([], [], "sample"):
                        st.success("🎉 Sample voice model loaded!")
    
    # =================== STEP 3: GENERATE CLONE ===================
    if st.session_state.vocal_track is not None and st.session_state.voice_model is not None:
        st.markdown("---")
        st.header("🎭 Step 3: Generate Your Voice Clone")
        
        # Show model info
        model_info = st.session_state.voice_model
        characteristics = model_info['characteristics']
        
        if model_info['type'] == 'personal_model':
            st.success(f"✅ Personal voice model ready ({model_info['sample_count']} samples)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pitch Shift", f"{characteristics['pitch_shift']:.1f} semitones")
            with col2:
                st.metric("Voice Brightness", f"{characteristics['voice_brightness']:.2f}")
            with col3:
                st.metric("Formant Shift", f"{characteristics['formant_shift']:.2f}")
        else:
            st.success("✅ Sample voice model ready (+3 semitones, enhanced)")
        
        # Generate clone button
        if st.button("🎵 Transform Voice Now!", type="primary", use_container_width=True):
            with st.spinner("🎭 Applying voice transformation..."):
                cloned_audio = clone_voice(
                    st.session_state.vocal_track,
                    st.session_state.voice_model, 
                    st.session_state.vocal_sample_rate
                )
                
                if cloned_audio is not None:
                    st.success("🎉 Voice transformation complete!")
                    
                    # Show results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🎵 Original Voice")
                        original_bytes = io.BytesIO()
                        sf.write(original_bytes, st.session_state.vocal_track, st.session_state.vocal_sample_rate, format='WAV')
                        original_bytes.seek(0)
                        st.audio(original_bytes, format="audio/wav")
                    
                    with col2:
                        st.subheader("🎤 Transformed Voice")
                        cloned_bytes = io.BytesIO()
                        sf.write(cloned_bytes, cloned_audio, st.session_state.vocal_sample_rate, format='WAV')
                        cloned_bytes.seek(0)
                        st.audio(cloned_bytes, format="audio/wav")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Transformed Voice",
                            data=cloned_bytes.getvalue(),
                            file_name="transformed_voice.wav",
                            mime="audio/wav",
                            use_container_width=True
                        )
                        
                        # Reset button
                        if st.button("🔄 Start Over", use_container_width=True):
                            for key in ['vocal_track', 'vocal_sample_rate', 'voice_model', 'voice_samples', 'uploaded_voice_samples']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()

if __name__ == "__main__":
    main()
