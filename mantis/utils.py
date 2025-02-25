import os
import tempfile
import logging
from typing import Callable, TypeVar, Any, Dict, Optional, Union, Generic, cast
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .models import ProcessingProgress

# Set up logging
logger = logging.getLogger("mantis")

T = TypeVar('T')
InputValidator = Callable[[str], Any]
OutputCreator = Callable[[str], T]

class MantisError(Exception):
    """Base exception class for Mantis errors."""
    pass

class AudioProcessingError(MantisError):
    """Exception raised when there's an error processing audio."""
    pass

class YouTubeDownloadError(MantisError):
    """Exception raised when there's an error downloading from YouTube."""
    pass

class ModelInferenceError(MantisError):
    """Exception raised when there's an error with the AI model inference."""
    pass

class ValidationError(MantisError):
    """Exception raised when there's a validation error."""
    pass

def is_youtube_url(url: str) -> bool:
    """
    Check if the given URL is a YouTube URL.
    
    Args:
        url: The URL to check
        
    Returns:
        bool: True if the URL is a YouTube URL, False otherwise
    """
    try:
        parsed = urlparse(url)
        return any(
            domain in parsed.netloc
            for domain in ['youtube.com', 'youtu.be', 'www.youtube.com']
        )
    except Exception as e:
        logger.warning(f"Error parsing URL {url}: {e}")
        return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(YouTubeDownloadError),
    reraise=True
)
def stream_youtube_audio(url: str, progress_callback: Optional[Callable[[ProcessingProgress], None]] = None) -> str:
    """
    Download audio from a YouTube URL to a temporary file.
    
    Args:
        url: The YouTube URL to download from
        progress_callback: Optional callback function to report progress
        
    Returns:
        str: Path to the downloaded temporary file
        
    Raises:
        YouTubeDownloadError: If there's an error downloading from YouTube
    """
    temp_dir = tempfile.gettempdir()
    # The output file is designated as an mp3 file.
    temp_file = os.path.join(temp_dir, 'temp_audio.mp3')
    
    def progress_hook(d: Dict[str, Any]) -> None:
        if progress_callback and 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
            progress = d['downloaded_bytes'] / d['total_bytes']
            progress_callback(ProcessingProgress("Downloading audio", progress))
    
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio',
        'outtmpl': temp_file,
        'noplaylist': True,
        'quiet': True,  # Suppress most output
        'no_warnings': True,  # Suppress warnings
        'progress_hooks': [progress_hook] if progress_callback else [],
        'logger': None  # Disable logger output
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not os.path.exists(temp_file):
            raise YouTubeDownloadError(f"Failed to download audio from {url}")
            
        return temp_file
    except Exception as e:
        logger.error(f"Error downloading YouTube audio from {url}: {e}")
        raise YouTubeDownloadError(f"Failed to download audio from YouTube: {str(e)}")

def process_audio_with_gemini(
    audio_file: str,
    validate_input: InputValidator,
    create_output: OutputCreator[T],
    model_prompt: str,
    model_name: str = "gemini-1.5-flash",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> T:
    """
    Process audio with Gemini AI using the provided input/output handlers.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        validate_input: Function to validate the input
        create_output: Function to create the output from the model response
        model_prompt: Prompt to send to the model
        model_name: Name of the Gemini model to use
        progress_callback: Optional callback function to report progress
        
    Returns:
        T: The processed output
        
    Raises:
        AudioProcessingError: If there's an error processing the audio
        ModelInferenceError: If there's an error with the model inference
        ValidationError: If there's a validation error
    """
    temp_file_path = None
    
    try:
        # Report initial progress
        if progress_callback:
            progress_callback(ProcessingProgress("Starting processing", 0.0))
        
        # Handle YouTube URLs
        if is_youtube_url(audio_file):
            logger.info(f"Processing YouTube URL: {audio_file}")
            if progress_callback:
                progress_callback(ProcessingProgress("Downloading YouTube audio", 0.0))
            
            temp_file_path = stream_youtube_audio(audio_file, progress_callback)
            file_to_process = temp_file_path
        else:
            logger.info(f"Processing local audio file: {audio_file}")
            file_to_process = audio_file
            
        # Validate input
        try:
            validate_input(file_to_process)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise ValidationError(f"Input validation failed: {str(e)}")
        
        # Report progress before model processing
        if progress_callback:
            progress_callback(ProcessingProgress("Processing with AI model", 0.5))
        
        # Upload and process with Gemini
        try:
            uploaded_file = genai.upload_file(file_to_process)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([model_prompt, uploaded_file])
            
            # Report completion
            if progress_callback:
                progress_callback(ProcessingProgress("Processing complete", 1.0))
            
            # Create and return output
            return create_output(response.text)
        except Exception as e:
            logger.error(f"Model inference error: {e}")
            raise ModelInferenceError(f"Error processing with Gemini AI: {str(e)}")
        
    except MantisError:
        # Re-raise MantisError subclasses without wrapping
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing audio: {e}")
        raise AudioProcessingError(f"Unexpected error processing audio: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        file_path: Path to the temporary file to clean up
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {e}")
