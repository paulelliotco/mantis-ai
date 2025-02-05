__version__ = "0.1.1"

# Add logging configuration at the top
import os
import logging
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
logging.getLogger('absl').setLevel(logging.ERROR)  # Suppress absl logging
warnings.filterwarnings('ignore', category=UserWarning)  # Suppress warnings

from .transcription import transcribe
from .summarize import summarize
from .extract import extract

# Core functionality only
__all__ = ['transcribe', 'summarize', 'extract']
