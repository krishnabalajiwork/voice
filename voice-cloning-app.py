# Enhanced Voice Cloning App with Real Voice Transformation
# Actual voice characteristic changes, not just audio effects

import streamlit as st
import os
import tempfile
import io
import numpy as np
import librosa
import soundfile as sf
from streamlit_mic_recorder import mic_recorder
from scipy import signal
import scipy.fft

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

# Analyze voice characteristics from samples
def analyze_voice_characteristics(voice_samples):
    """Extract actual voice characteristics from recorded samples"""
    characteristics = {
        'pitch_shift': 0,
        'formant_shift': 0, 
        'voice_brightness': 1.0,
        'breathiness': 0.0,
        'vibrato_rate': 0.0
    }
    
    if not voice_samples:
        return characteristics
    
    try:
        # Analyze the recorded voice samples
        all_audio = []
        
        for sample in voice_samples:
            # Convert bytes to audio
            audio_bytes = io.BytesIO(sample['bytes'])
            audio, sr = librosa.load(audio_bytes, sr=22050)
            all_audio.extend(audio)
        
        if len(all_audio) > 1000:
            all_audio = np.array(all_audio)
            
            # Extract fundamental frequency (pitch)
            pitches, magnitudes = librosa.core.piptrack(y=all_audio, sr=22050)
            avg_pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 220
            
            # Calculate pitch shift needed (relative to average voice)
            reference_pitch = 220  # Reference A3
            characteristics['pitch_shift'] = np.log2(avg_pitch / reference_pitch) * 12  # In semitones
            
            # Analyze spectral characteristics
            stft = librosa.stft(all_audio)
            magnitude = np.abs(stft)
            
            # Voice brightness (high frequency content)
            freq_bins = librosa.fft_frequencies(sr=22050, n_fft=2048)
            high_freq_energy = np.mean(magnitude[freq_bins > 2000])
            low_freq_energy = np.mean(magnitude[freq_bins < 1000])
            characteristics['voice_brightness'] = high_freq_energy / (low_freq_energy + 1e-10)
            
            # Formant estimation (simplified)
            mfcc = librosa.feature.mfcc(y=all_audio, sr=22050, n_mfcc=13)
            characteristics['formant_shift'] = np.mean(mfcc[1:3]) / 10  # Simplified formant representation
            
            st.success(f"✅ Voice analyzed: Pitch shift: {characteristics['pitch_shift']:.1f} semitones")
            
    except Exception as e:
        st.warning(f"Voice analysis error: {str(e)}, using default characteristics")
    
    return characteristics

# Create voice model with real characteristics
def create_voice_model(samples, method="recorded"):
    """Create voice model with analyzed characteristics"""
    try:
        if method == "sample":
            # Sample model with predefined characteristics
            model_data = {
                'type': 'sample_model',
                'characteristics': {
                    'pitch_shift': 3.0,  # +3 semitones higher
                    'formant_shift': 0.15,
                    'voice_brightness': 1.3,
                    'breathiness': 0.1,
                    'vibrato_rate': 0.05
                },
                'trained': True
            }
        else:
            # Analyze personal voice samples
            characteristics = analyze_voice_characteristics(samples)
            model_data = {
                'type': 'personal_model', 
                'samples': samples,
                'sample_count': len(samples),
                'characteristics': characteristics,
                'trained': True
            }
        
        st.session_state.voice_model = model_data
        return True
    except Exception as e:
        st.error(f"Error creating voice model: {str(e)}")
        return False

# Advanced voice transformation
def clone_voice(original_vocals, voice_model, sample_rate):
    """Apply real voice transformation based on analyzed characteristics"""
    try:
        characteristics = voice_model['characteristics']
        cloned_vocals = original_vocals.copy()
        
        # 1. PITCH SHIFTING (most important for voice change)
        pitch_shift_semitones = characteristics['pitch_shift']
        if abs(pitch_shift_semitones) > 0.1:
            cloned_vocals = librosa.effects.pitch_shift(
                cloned_vocals, sr=sample_rate, n_steps=pitch_shift_semitones
            )
        
        # 2. FORMANT SHIFTING (changes voice character)
        if abs(characteristics['formant_shift']) > 0.05:
            # Apply formant shifting through spectral manipulation
            stft = librosa.stft(cloned_vocals)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Shift formants by modifying spectral envelope
            formant_factor = 1 + characteristics['formant_shift']
            freq_bins = len(magnitude)
            new_magnitude = np.zeros_like(magnitude)
            
            for i in range(magnitude.shape[1]):
                # Interpolate magnitude spectrum with formant shift
                shifted_freqs = np.arange(freq_bins) * formant_factor
                shifted_freqs = np.clip(shifted_freqs, 0, freq_bins-1)
                new_magnitude[:, i] = np.interp(range(freq_bins), shifted_freqs, magnitude[:, i])
            
            # Reconstruct audio
            new_stft = new_magnitude * np.exp(1j * phase)
            cloned_vocals = librosa.istft(new_stft)
        
        # 3. VOICE BRIGHTNESS ADJUSTMENT
        brightness = characteristics['voice_brightness']
        if abs(brightness - 1.0) > 0.1:
            # Apply EQ-like filtering
            if brightness > 1.0:
                # Boost high frequencies
                b, a = signal.butter(2, 3000/(sample_rate/2), btype='high')
                high_freq = signal.filtfilt(b, a, cloned_vocals)
                cloned_vocals = cloned_vocals + high_freq * (brightness - 1.0) * 0.3
            else:
                # Reduce high frequencies  
                b, a = signal.butter(2, 3000/(sample_rate/2), btype='low')
                cloned_vocals = signal.filtfilt(b, a, cloned_vocals)
        
        # 4. ADD BREATHINESS (if specified)
        breathiness = characteristics.get('breathiness', 0)
        if breathiness > 0:
            # Add subtle noise to simulate breathiness
            breath_noise = np.random.normal(0, breathiness * 0.05, len(cloned_vocals))
            cloned_vocals = cloned_vocals + breath_noise
        
        # 5. VIBRATO EFFECT (if specified)
        vibrato_rate = characteristics.get('vibrato_rate', 0)
        if vibrato_rate > 0:
            # Add vibrato (pitch modulation)
            vibrato = np.sin(2 * np.pi * vibrato_rate * np.arange(len(cloned_vocals)) / sample_rate)
            pitch_mod = vibrato * 0.5  # Small pitch modulation
            cloned_vocals = cloned_vocals * (1 + pitch_mod * 0.02)
        
        # 6. NORMALIZE AND CLEAN UP
        cloned_vocals = np.nan_to_num(cloned_vocals)  # Remove NaN values
        if np.max(np.abs(cloned_vocals)) > 0:
            cloned_vocals = cloned_vocals / np.max(np.abs(cloned_vocals)) * 0.95
        
        return cloned_vocals
        
    except Exception as e:
        st.error(f"Voice cloning error: {str(e)}")
        # Fallback: return original with simple pitch shift
        try:
            return librosa.effects.pitch_shift(original_vocals, sr=sample_rate, n_steps=2.0)
        except:
            return original_vocals

# Main app
def main():
    init_session_state()
    
    st.title("🎤 Enhanced AI Voice Cloning Studio")
    st.markdown("**Real voice transformation with pitch shifting, formant analysis, and voice characteristics!**")
    
    # =================== STEP 1: UPLOAD VOCAL TRACK ===================
    st.header("🎵 Step 1: Upload Your Vocal Track")
    
    uploaded_file = st.file_uploader(
        "Choose your vocal audio file (vocals only, no instruments)",
        type=['mp3', 'wav', 'flac', 'm4a'],
        help="Upload a clean vocal track without background music"
    )
    
    if uploaded_file is not None:
        # Process uploaded file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            # Load audio
            vocal_audio, sample_rate = librosa.load(tmp_file_path, sr=22050)
            st.session_state.vocal_track = vocal_audio
            st.session_state.vocal_sample_rate = sample_rate
            
            # Clean up
            os.unlink(tmp_file_path)
            
            # Show upload success and preview
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
            st.error(f"Error loading audio: {str(e)}")
            return
    
    # =================== STEP 2: VOICE MODEL ===================
    if st.session_state.vocal_track is not None:
        st.markdown("---")
        st.header("🤖 Step 2: Choose Your Voice Model")
        
        # Voice model options
        model_option = st.radio(
            "Select voice model type:",
            ["🎤 Record My Voice (Personalized Analysis)", "🎭 Use Sample Voice (+3 semitones higher)"],
            help="Record your voice for personalized pitch/formant analysis, or use a sample model"
        )
        
        if model_option == "🎤 Record My Voice (Personalized Analysis)":
            st.subheader("Record Your Voice Samples for Analysis")
            st.info("💡 Sing or speak clearly - we'll analyze your pitch, formants, and voice characteristics")
            
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
                
                for i, sample in enumerate(st.session_state.voice_samples[-3:]):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.audio(sample['bytes'], format="audio/wav")
                    with col2:
                        if st.button("🗑️", key=f"delete_{i}"):
                            st.session_state.voice_samples.pop(i)
                            st.rerun()
                
                # Train model button
                if len(st.session_state.voice_samples) >= 2:
                    if st.button("🔬 Analyze My Voice Characteristics", type="primary", use_container_width=True):
                        with st.spinner("Analyzing your voice characteristics (pitch, formants, brightness)..."):
                            if create_voice_model(st.session_state.voice_samples, "recorded"):
                                st.success("🎉 Your voice has been analyzed and model created!")
                else:
                    st.warning(f"⚠️ Record at least 2 samples (currently: {len(st.session_state.voice_samples)})")
        
        else:  # Use Sample Voice
            st.subheader("Use Sample Voice Model")
            st.info("📝 Sample model: +3 semitones higher pitch, brighter tone, enhanced formants")
            
            if st.button("🎭 Use Sample Voice Model", type="primary", use_container_width=True):
                with st.spinner("Loading sample voice model..."):
                    if create_voice_model([], "sample"):
                        st.success("🎉 Sample voice model loaded!")
    
    # =================== STEP 3: GENERATE CLONE ===================
    if st.session_state.vocal_track is not None and st.session_state.voice_model is not None:
        st.markdown("---")
        st.header("🎭 Step 3: Generate Your Voice Clone")
        
        # Show model info with characteristics
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
            with st.spinner("🎭 Applying voice transformation (pitch, formants, characteristics)..."):
                cloned_audio = clone_voice(
                    st.session_state.vocal_track,
                    st.session_state.voice_model, 
                    st.session_state.vocal_sample_rate
                )
                
                if cloned_audio is not None:
                    st.success("🎉 Voice transformation complete!")
                    
                    # Show results side by side
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
                            for key in ['vocal_track', 'vocal_sample_rate', 'voice_model', 'voice_samples']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()

if __name__ == "__main__":
    main()
