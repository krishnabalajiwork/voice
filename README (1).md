# 🎤 AI Singing Voice Cloning Studio

> Transform any song with your AI-cloned singing voice using Streamlit

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Features

✨ **One-Click Song Processing**: Upload any song and automatically separate vocals from instruments  
🎙️ **Personal Voice Cloning**: Record voice samples once, use forever  
🎵 **AI Voice Replacement**: Replace original vocals with your cloned singing voice  
🔄 **Persistent Models**: Your voice model is saved for future use  
🌐 **Web-Based Interface**: Easy-to-use Streamlit interface  
⚡ **Fast Processing**: Optimized for real-time audio processing  

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

```bash
# Download the setup script and run
curl -O https://raw.githubusercontent.com/your-repo/voice-cloning-studio/main/setup.sh
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Setup

```bash
# Clone or download the files
git clone https://github.com/your-repo/voice-cloning-studio.git
cd voice-cloning-studio

# Install system dependencies (Ubuntu/Debian)
sudo apt install ffmpeg libsndfile1

# Create virtual environment
python3 -m venv voice_cloning_env
source voice_cloning_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the application
streamlit run voice-cloning-app.py
```

## 📁 Project Structure

```
voice-cloning-studio/
├── voice-cloning-app.py    # Main Streamlit application
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── setup.sh               # Automated setup script
├── setup-guide.md         # Detailed setup instructions
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

## 🎯 How It Works

### 1. **Song Input & Vocal Separation**
- Upload any audio file (MP3, WAV, FLAC, M4A)
- AI-powered Spleeter separates vocals from instruments
- Preview isolated vocal and instrumental tracks

### 2. **Voice Model Creation (One-Time)**
- Record 3-5 voice samples using your microphone
- AI trains a personalized singing voice model
- Model is automatically saved for future use

### 3. **Voice Cloning & Replacement**
- AI replaces original vocals with your cloned voice
- Maintains original melody, timing, and style
- Download your personalized singing performance

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Web interface and user interaction |
| **Audio Separation** | Spleeter (Deezer) | Vocal/instrumental separation |
| **Audio Processing** | Librosa, SoundFile | Audio analysis and manipulation |
| **Voice Recording** | streamlit-mic-recorder | Browser microphone access |
| **Voice Cloning** | Custom pipeline | Voice model training and inference |
| **Backend** | Python 3.8+ | Core application logic |

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **CPU**: Dual-core 2.0GHz
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Internet**: For initial model downloads

### Recommended Requirements
- **CPU**: Quad-core 3.0GHz+
- **RAM**: 8GB+
- **GPU**: NVIDIA GTX 1060+ (optional, for faster processing)
- **Storage**: 5GB+ free space (SSD preferred)

## 🎮 Usage Guide

### Step 1: Upload Your Song
1. Click "**1. Upload Song**" in the sidebar
2. Upload an audio file (max 100MB, 5 minutes)
3. Click "🎯 **Separate Vocals and Instruments**"
4. Wait for AI processing (1-3 minutes)

### Step 2: Create Voice Model
1. Click "**2. Create Voice Model**" in the sidebar
2. Record 3-5 voice samples (different phrases recommended)
3. Click "🤖 **Train Voice Model**"
4. Model is saved automatically

### Step 3: Generate Clone
1. Click "**3. Generate Clone**" in the sidebar
2. Click "🎵 **Generate My Singing Clone**"
3. Download your AI singing performance

## ⚙️ Configuration

Customize the application behavior by editing `config.py`:

```python
# Audio settings
MAX_FILE_SIZE_MB = 100
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "flac", "m4a"]

# Voice model settings
MIN_VOICE_SAMPLES = 3
RECOMMENDED_VOICE_SAMPLES = 5

# Processing settings
USE_GPU = True
ENABLE_CACHING = True
```

## 🔧 Advanced Features

### GPU Acceleration
Enable GPU processing for 3-5x faster performance:
```bash
# Install CUDA version of TensorFlow
pip install tensorflow-gpu==2.13.0
```

### Professional Voice Models
Integrate advanced models like So-VITS-SVC:
```python
# In config.py
ADVANCED_MODELS = {
    "so_vits_svc": {
        "enabled": True,
        "model_path": "./models/sovits/"
    }
}
```

## 🚀 Deployment Options

### Local Development
```bash
streamlit run voice-cloning-app.py
```

### Docker Deployment
```bash
docker build -t voice-cloning-studio .
docker run -p 8501:8501 voice-cloning-studio
```

### Cloud Deployment
- **Streamlit Cloud**: Connect your GitHub repository
- **Heroku**: Use the provided Procfile
- **AWS/GCP/Azure**: Deploy using container services

## 🔍 Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from https://ffmpeg.org
```

**"Out of memory error"**
- Reduce audio file size or duration
- Close other applications
- Disable GPU acceleration if problematic

**"Microphone not accessible"**
- Ensure HTTPS connection (required for microphone)
- Check browser permissions
- Try Chrome browser (recommended)

### Performance Tips
- Use shorter audio clips for testing
- Enable GPU acceleration if available
- Record voice samples in quiet environment
- Use high-quality input audio (44.1kHz+)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Test your changes thoroughly
4. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black voice-cloning-app.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Deezer](https://github.com/deezer/spleeter)** for the Spleeter audio separation library
- **[Streamlit](https://streamlit.io)** for the amazing web framework
- **[So-VITS-SVC](https://github.com/svc-develop-team/so-vits-svc)** developers for voice cloning research
- Open source audio processing community

## ⚠️ Important Notes

### Legal and Ethical Use
- **Copyright**: Only use songs you own or have permission to modify
- **Privacy**: Voice models are stored locally by default
- **Commercial Use**: Obtain proper licenses for commercial applications
- **Consent**: Only clone voices with explicit permission

### Technical Limitations
- Processing time depends on audio length and system specs
- Voice cloning quality improves with more training samples
- Works best with clear, studio-quality audio
- Current implementation uses simplified voice conversion

## 📞 Support

- **Documentation**: See [setup-guide.md](setup-guide.md) for detailed instructions
- **Issues**: Report bugs via GitHub Issues
- **Community**: Join discussions in GitHub Discussions
- **Updates**: Watch the repository for new releases

## 🔄 Roadmap

### Upcoming Features
- [ ] Advanced voice cloning models (So-VITS-SVC, RVC)
- [ ] Real-time voice conversion
- [ ] Multi-language support
- [ ] Batch processing capabilities
- [ ] Voice style transfer
- [ ] Professional audio effects

### Version History
- **v1.0.0**: Initial release with basic voice cloning
- **v0.9.0**: Beta release with Spleeter integration
- **v0.8.0**: Alpha release with Streamlit interface

---

**Made with ❤️ by the Voice Cloning Community**

*Star ⭐ this repository if you found it helpful!*