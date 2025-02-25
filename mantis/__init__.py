__version__ = "0.1.8"

# Add logging configuration at the top
import os
import logging
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
logging.getLogger('absl').setLevel(logging.ERROR)  # Suppress absl logging
warnings.filterwarnings('ignore', category=UserWarning)  # Suppress warnings

# Configure package logger
logger = logging.getLogger("mantis")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

from .transcription import transcribe
from .summarize import summarize
from .extract import extract
from .utils import MantisError, AudioProcessingError, YouTubeDownloadError, ModelInferenceError, ValidationError
from .models import ProcessingProgress

# Core functionality
__all__ = [
    'transcribe', 
    'summarize', 
    'extract', 
    'MantisError', 
    'AudioProcessingError', 
    'YouTubeDownloadError', 
    'ModelInferenceError', 
    'ValidationError',
    'ProcessingProgress'
]
