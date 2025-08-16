#!/bin/bash

# AI Singing Voice Cloning Studio - Quick Setup Script
# Run this script to automatically set up the entire application

echo "🎤 AI Singing Voice Cloning Studio - Quick Setup"
echo "================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Install system dependencies based on OS
echo "🔧 Installing system dependencies..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "📦 Installing dependencies for Linux..."
    sudo apt update
    sudo apt install -y ffmpeg libsndfile1 python3-venv python3-pip
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📦 Installing dependencies for macOS..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg libsndfile
    else
        echo "⚠️  Homebrew not found. Please install FFmpeg and libsndfile manually."
        echo "   Visit: https://ffmpeg.org and https://github.com/libsndfile/libsndfile"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "⚠️  Windows detected. Please manually install:"
    echo "   - FFmpeg: https://ffmpeg.org/download.html"
    echo "   - Add FFmpeg to your system PATH"
    read -p "Press Enter after installing FFmpeg..."
else
    echo "⚠️  Unknown OS. Please manually install FFmpeg and libsndfile."
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv voice_cloning_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source voice_cloning_env/Scripts/activate
else
    source voice_cloning_env/bin/activate
fi

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install streamlit==1.28.0
pip install numpy==1.24.3
pip install scipy==1.11.2
pip install librosa==0.10.1
pip install soundfile==0.12.1
pip install streamlit-mic-recorder==0.0.5
pip install pandas==2.0.3

# Install Spleeter separately (sometimes needs special handling)
echo "🎵 Installing Spleeter for vocal separation..."
pip install tensorflow==2.13.0
pip install spleeter==2.3.2

# Verify Spleeter installation
echo "✅ Verifying Spleeter installation..."
python -c "import spleeter; print('Spleeter installed successfully!')" || {
    echo "❌ Spleeter installation failed. Trying alternative method..."
    pip install --no-cache-dir spleeter==2.3.2
}

# Download Spleeter models (this might take a while)
echo "📥 Downloading AI models (this may take a few minutes)..."
python -c "
import spleeter
from spleeter.separator import Separator
print('Downloading 2-stem separation model...')
separator = Separator('spleeter:2stems')
print('Models downloaded successfully!')
" || echo "⚠️  Model download failed. Models will be downloaded on first use."

# Create launcher script
echo "🚀 Creating launcher script..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows batch file
    cat > launch_app.bat << 'EOF'
@echo off
echo Starting AI Singing Voice Cloning Studio...
call voice_cloning_env\Scripts\activate
streamlit run voice-cloning-app.py
pause
EOF
    chmod +x launch_app.bat
    echo "✅ Created launch_app.bat"
else
    # Unix shell script
    cat > launch_app.sh << 'EOF'
#!/bin/bash
echo "🎤 Starting AI Singing Voice Cloning Studio..."
source voice_cloning_env/bin/activate
streamlit run voice-cloning-app.py
EOF
    chmod +x launch_app.sh
    echo "✅ Created launch_app.sh"
fi

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
voice_cloning_env/
.env

# Audio files
*.wav
*.mp3
*.flac
*.m4a

# Models and data
models/
data/
temp/
*.pkl
*.pth

# Streamlit
.streamlit/

# OS
.DS_Store
Thumbs.db
EOF

# Final setup verification
echo "🔍 Verifying installation..."
python -c "
try:
    import streamlit
    import librosa
    import soundfile
    import numpy
    import spleeter
    print('✅ All core packages imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo "================================================="
echo ""
echo "📋 Next steps:"
echo "1. Ensure you have the following files in this directory:"
echo "   - voice-cloning-app.py (main application)"
echo "   - requirements.txt (Python dependencies)"
echo "   - setup-guide.md (detailed documentation)"
echo ""
echo "2. Start the application:"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "   Double-click: launch_app.bat"
    echo "   Or run: voice_cloning_env\\Scripts\\activate && streamlit run voice-cloning-app.py"
else
    echo "   Run: ./launch_app.sh"
    echo "   Or run: source voice_cloning_env/bin/activate && streamlit run voice-cloning-app.py"
fi
echo ""
echo "3. Open your browser and go to: http://localhost:8501"
echo ""
echo "📖 For detailed usage instructions, see setup-guide.md"
echo ""
echo "🎤 Enjoy creating your AI singing clones!"

# Check if launch should happen automatically
read -p "🚀 Would you like to launch the app now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎤 Launching AI Singing Voice Cloning Studio..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        cmd //c launch_app.bat
    else
        ./launch_app.sh
    fi
fi