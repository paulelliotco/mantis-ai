import logging

# Configure logging but set to ERROR level by default to effectively disable most logging
logging.basicConfig(
    level=logging.ERROR,  # Set to ERROR level to disable most logging by default
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Package metadata
__version__ = "0.2.0"  # Responses API refresh
__author__ = "Paul Elliot"
__email__ = "paul@paulelliot.co"
__description__ = "Audio processing with large language models"

# Add logging configuration at the top
import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging completely
logging.getLogger('absl').setLevel(logging.ERROR)  # Suppress absl logging
warnings.filterwarnings('ignore', category=UserWarning)  # Suppress warnings

# Configure package logger - disabled by default
logger = logging.getLogger("mantis")
logger.setLevel(logging.ERROR)  # Set to ERROR level to disable most logging
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def enable_verbose_logging():
    """
    Enable verbose logging for the Mantis package.
    This is useful for debugging or understanding the processing flow.
    """
    logger.setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Verbose logging enabled for Mantis")

def enable_debug_logging():
    """
    Enable debug-level logging for the Mantis package.
    This provides the most detailed logging for troubleshooting issues.
    """
    logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled for Mantis")

def enable_warning_logging():
    """
    Enable warning-level logging for the Mantis package.
    This provides only warning and error messages.
    """
    logger.setLevel(logging.WARNING)
    logging.getLogger().setLevel(logging.WARNING)

# Import public API
from .transcription import transcribe
from .summarize import summarize
from .extract import extract
from .models import (
    TranscriptionInput, TranscriptionOutput,
    SummarizeInput, SummarizeOutput,
    ExtractInput, ExtractOutput,
    ExtractionResult, ProcessingProgress
)
from .utils import (
    MantisError, AudioProcessingError, 
    YouTubeDownloadError, ModelInferenceError,
    ValidationError
)

# Define public API
__all__ = [
    "transcribe",
    "summarize",
    "extract",
    "TranscriptionInput",
    "TranscriptionOutput",
    "SummarizeInput",
    "SummarizeOutput",
    "ExtractInput",
    "ExtractOutput",
    "ExtractionResult",
    "ProcessingProgress",
    "MantisError",
    "AudioProcessingError",
    "YouTubeDownloadError",
    "ModelInferenceError",
    "ValidationError",
    "enable_verbose_logging",
    "enable_debug_logging",
    "enable_warning_logging"
]
