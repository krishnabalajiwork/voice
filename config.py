# Configuration file for AI Singing Voice Cloning Studio

# Application Settings
APP_TITLE = "AI Singing Voice Cloning Studio"
APP_ICON = "🎤"
VERSION = "1.0.0"

# Audio Processing Settings
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "flac", "m4a", "ogg"]
MAX_FILE_SIZE_MB = 100
DEFAULT_SAMPLE_RATE = 22050
MAX_AUDIO_LENGTH_SECONDS = 300

# Voice Model Settings
MIN_VOICE_SAMPLES = 3
RECOMMENDED_VOICE_SAMPLES = 5
MAX_VOICE_SAMPLES = 10
VOICE_SAMPLE_MIN_DURATION = 3  # seconds
VOICE_SAMPLE_MAX_DURATION = 30  # seconds

# Spleeter Settings
SPLEETER_MODEL = "spleeter:2stems"  # Options: "2stems", "4stems", "5stems"
AUDIO_ADAPTER = "tensorflow"
SAMPLE_RATE = 44100
AUDIO_BITRATE = "128k"

# Session State Keys
SESSION_KEYS = {
    "user_voice_model": "user_voice_model",
    "model_trained": "model_trained", 
    "separated_vocals": "separated_vocals",
    "separated_accompaniment": "separated_accompaniment",
    "original_song": "original_song",
    "voice_samples": "voice_samples",
    "processing_status": "processing_status"
}

# UI Settings
SIDEBAR_WIDTH = 300
MAIN_CONTENT_WIDTH = 800
SHOW_PROGRESS_BARS = True
ENABLE_AUDIO_PREVIEW = True
SHOW_AUDIO_WAVEFORMS = False  # Requires additional dependencies

# Advanced Model Settings (for future So-VITS-SVC integration)
ADVANCED_MODELS = {
    "so_vits_svc": {
        "enabled": False,
        "model_path": "./models/sovits/",
        "config_path": "./models/sovits/config.json"
    },
    "rvc": {
        "enabled": False,
        "model_path": "./models/rvc/"
    }
}

# Performance Settings
USE_GPU = True  # Set to False to force CPU usage
MAX_WORKERS = 4
ENABLE_CACHING = True
CACHE_TTL = 3600  # Cache time-to-live in seconds

# Debug Settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
SAVE_INTERMEDIATE_FILES = False  # Keep temporary files for debugging

# Security Settings
ENABLE_FILE_VALIDATION = True
MAX_CONCURRENT_USERS = 10
RATE_LIMIT_REQUESTS_PER_MINUTE = 30

# Deployment Settings
STREAMLIT_CONFIG = {
    "server.port": 8501,
    "server.address": "0.0.0.0",
    "server.maxUploadSize": 200,  # MB
    "browser.gatherUsageStats": False,
    "theme.primaryColor": "#FF6B6B",
    "theme.backgroundColor": "#FFFFFF",
    "theme.secondaryBackgroundColor": "#F0F2F6",
    "theme.textColor": "#262730"
}

# Model Training Settings (for advanced users)
TRAINING_CONFIG = {
    "batch_size": 16,
    "learning_rate": 0.0001,
    "epochs": 100,
    "validation_split": 0.2,
    "early_stopping_patience": 10
}

# Error Messages
ERROR_MESSAGES = {
    "file_too_large": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit",
    "unsupported_format": f"Supported formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}",
    "audio_too_long": f"Audio length exceeds {MAX_AUDIO_LENGTH_SECONDS} seconds",
    "insufficient_samples": f"Please record at least {MIN_VOICE_SAMPLES} voice samples",
    "model_not_trained": "Voice model not found. Please train your voice model first",
    "separation_failed": "Vocal separation failed. Please try a different audio file",
    "gpu_not_available": "GPU not available, falling back to CPU processing"
}

# Success Messages  
SUCCESS_MESSAGES = {
    "file_uploaded": "✅ Audio file uploaded successfully",
    "separation_complete": "🎵 Vocal separation completed successfully",
    "model_trained": "🤖 Voice model trained successfully",
    "clone_generated": "🎉 Singing clone generated successfully",
    "download_ready": "📥 Your singing clone is ready for download"
}

# Help Text
HELP_TEXT = {
    "upload_song": "Upload any song you want to sing. Supported formats: MP3, WAV, FLAC, M4A",
    "record_samples": "Record 3-5 voice samples singing different phrases for best results",
    "voice_model": "Your voice model will be saved for future use - no need to re-record",
    "generate_clone": "Replace the original vocals with your AI-cloned singing voice"
}