# 🎤 AI Singing Voice Cloning Studio - Setup Guide

## Overview
This application creates a complete singing voice cloning system that:
1. **Accepts any song** from the user
2. **Separates vocals and instruments** using AI-powered source separation
3. **Creates a personalized voice model** from user recordings (one-time setup)
4. **Replaces original vocals** with the user's cloned singing voice
5. **Stores the voice model** for future use (no re-recording needed)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git (for cloning repositories)
- FFmpeg (for audio processing)
- At least 4GB RAM (recommended 8GB+)
- GPU (optional but recommended for faster processing)

### Step 1: System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg libsndfile1 python3-pip
```

#### On macOS:
```bash
brew install ffmpeg libsndfile
```

#### On Windows:
1. Download and install FFmpeg from https://ffmpeg.org/download.html
2. Add FFmpeg to your system PATH
3. Install Python from https://python.org

### Step 2: Python Environment Setup
```bash
# Create virtual environment
python -m venv voice_cloning_env

# Activate environment
# On Linux/macOS:
source voice_cloning_env/bin/activate
# On Windows:
voice_cloning_env\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Install Spleeter separately (sometimes needs special handling)
pip install spleeter==2.3.2

# Verify installation
python -c "import spleeter; print('Spleeter installed successfully')"
```

### Step 4: Run the Application
```bash
streamlit run voice-cloning-app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 How to Use the Application

### Step 1: Upload Your Song
1. Click "1. Upload Song" in the sidebar
2. Upload any audio file (MP3, WAV, FLAC, M4A)
3. Click "🎯 Separate Vocals and Instruments"
4. Wait for AI to separate the tracks (this may take 1-3 minutes)

### Step 2: Create Your Voice Model (One-Time Setup)
1. Click "2. Create Voice Model" in the sidebar
2. Record at least 3 voice samples using the microphone recorder
3. Sing different phrases, notes, and styles for better results
4. Click "🤖 Train Voice Model"
5. Your model will be saved for future use

### Step 3: Generate Your Singing Clone
1. Click "3. Generate Clone" in the sidebar
2. Click "🎵 Generate My Singing Clone"
3. Download your AI-generated singing performance

## 🛠️ Advanced Setup (Optional)

### For Production Voice Cloning Models

If you want to use advanced models like So-VITS-SVC:

```bash
# Install PyTorch (adjust for your CUDA version)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Clone So-VITS-SVC repository
git clone https://github.com/svc-develop-team/so-vits-svc.git
cd so-vits-svc
pip install -r requirements.txt

# Download pre-trained models
# Follow So-VITS-SVC documentation for model setup
```

### GPU Setup (Recommended)
- **NVIDIA GPU**: Install CUDA 11.8 and cuDNN
- **AMD GPU**: Install ROCm (Linux only)
- **Apple Silicon**: Use MPS backend (automatically detected)

## 🌐 Deployment Options

### 1. Local Development
```bash
streamlit run voice-cloning-app.py
```

### 2. Streamlit Cloud
1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Deploy (note: may have resource limitations)

### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "voice-cloning-app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t voice-cloning-app .
docker run -p 8501:8501 voice-cloning-app
```

### 4. Cloud Platforms

#### Heroku
```bash
# Add to Procfile
web: streamlit run voice-cloning-app.py --server.port=$PORT --server.address=0.0.0.0

# Add apt-buildpack for FFmpeg
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add heroku/python
```

#### AWS/Google Cloud/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Ensure adequate memory and storage
- Consider using GPU instances for better performance

## ⚙️ Configuration Options

### Environment Variables
Create a `.env` file:
```env
# Model settings
MAX_AUDIO_LENGTH=300  # seconds
SAMPLE_RATE=22050
VOCAL_SEPARATION_MODEL=spleeter:2stems

# Streamlit settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Customization
Modify these variables in `voice-cloning-app.py`:
- `MAX_FILE_SIZE`: Maximum upload file size
- `SUPPORTED_FORMATS`: Supported audio formats
- `MODEL_SAVE_PATH`: Where to save voice models

## 🐛 Troubleshooting

### Common Issues

#### "FFmpeg not found"
```bash
# On Ubuntu/Debian
sudo apt install ffmpeg

# On macOS
brew install ffmpeg

# On Windows
# Download from https://ffmpeg.org and add to PATH
```

#### "Spleeter model download failed"
```bash
# Manual model download
python -c "import spleeter; from spleeter.separator import Separator; Separator('spleeter:2stems')"
```

#### "Out of memory error"
- Reduce audio file size or length
- Close other applications
- Use smaller batch sizes
- Consider using GPU acceleration

#### "Microphone not working"
- Ensure HTTPS connection (required for microphone access)
- Check browser permissions
- Try different browsers (Chrome recommended)

### Performance Optimization

#### For Faster Processing:
1. **Use GPU acceleration** (if available)
2. **Reduce audio quality** for testing
3. **Use shorter audio clips** during development
4. **Enable audio caching** in the app

#### For Better Quality:
1. **Use high-quality input audio** (44.1kHz, 16-bit minimum)
2. **Record voice samples** in quiet environment
3. **Use diverse training samples** (different pitches, styles)
4. **Train with more voice samples** (5-10 recommended)

## 📊 System Requirements

### Minimum Requirements
- **CPU**: Dual-core 2.0GHz
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Internet**: Broadband (for model downloads)

### Recommended Requirements
- **CPU**: Quad-core 3.0GHz or better
- **RAM**: 8GB or more
- **GPU**: NVIDIA GTX 1060 or better
- **Storage**: 5GB free space (SSD preferred)

## 🔐 Security Considerations

### Data Privacy
- Audio files are processed locally by default
- Voice models are stored in session state (not persistent)
- No data is sent to external servers (except Streamlit Cloud deployment)

### Production Deployment
- Use HTTPS for microphone access
- Implement user authentication
- Set up proper backup systems
- Monitor resource usage

## 🆕 Upgrading and Updates

### Update Dependencies
```bash
pip install --upgrade streamlit spleeter librosa
```

### Update Application
```bash
git pull origin main  # if using version control
# Or download latest version manually
```

## 📞 Support and Contributing

### Getting Help
1. Check troubleshooting section above
2. Review GitHub issues in component repositories
3. Join Streamlit community forums
4. Check Spleeter documentation

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License and Credits

This application uses:
- **Streamlit**: Apache 2.0 License
- **Spleeter**: MIT License (Deezer)
- **Librosa**: ISC License
- **streamlit-mic-recorder**: MIT License

### Acknowledgments
- Deezer team for Spleeter
- Streamlit team for the framework
- So-VITS-SVC developers for voice cloning research
- Open source audio processing community

---

**⚠️ Important Note**: This application is for educational and personal use. Ensure you have proper rights to any audio content you process. Respect copyright laws and obtain necessary permissions for commercial use.