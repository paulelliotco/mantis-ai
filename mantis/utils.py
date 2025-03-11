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
    # Assert input validation
    assert url, "YouTube URL cannot be empty"
    assert isinstance(url, str), "YouTube URL must be a string"
    assert is_youtube_url(url), f"Invalid YouTube URL: {url}"
    assert progress_callback is None or callable(progress_callback), "progress_callback must be None or a callable function"
    
    temp_dir = tempfile.gettempdir()
    
    # Create a unique filename based on the URL to prevent caching issues
    import hashlib
    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    temp_file = os.path.join(temp_dir, f'mantis_yt_{url_hash}.mp3')
    
    # Clean up any existing files with the same name
    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
            logger.debug(f"Removed existing temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"Failed to remove existing temporary file {temp_file}: {e}")
    
    def progress_hook(d: Dict[str, Any]) -> None:
        if progress_callback and 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] > 0:
            progress = d['downloaded_bytes'] / d['total_bytes']
            progress_callback(ProcessingProgress("Downloading YouTube audio", progress))
    
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio/best',
        'outtmpl': temp_file,
        'noplaylist': True,
        'quiet': True,  # Suppress most output
        'no_warnings': True,  # Suppress warnings
        'progress_hooks': [progress_hook] if progress_callback else [],
        'logger': None,  # Disable logger output
        'progress_callback': progress_callback,  # Pass the progress callback directly
        # Additional options to bypass YouTube's anti-bot measures
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'geo_bypass': True,
        'extractor_args': {'youtube': {'nocheckcertificate': True, 'skip_download': False}},
        # Use a random User-Agent to avoid being blocked
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            logger.debug(f"Attempting to download audio from YouTube URL: {url}")
            ydl.download([url])
        
        # Assert the file was downloaded successfully
        assert os.path.exists(temp_file), f"Failed to download audio from {url}"
        assert os.path.getsize(temp_file) > 0, f"Downloaded file is empty: {temp_file}"
            
        logger.debug(f"Successfully downloaded audio from YouTube URL: {url} to {temp_file}")
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
    # Assert input validation
    assert audio_file, "Audio file path or URL cannot be empty"
    assert isinstance(audio_file, str), "Audio file path or URL must be a string"
    assert callable(validate_input), "validate_input must be a callable function"
    assert callable(create_output), "create_output must be a callable function"
    assert model_prompt, "Model prompt cannot be empty"
    assert isinstance(model_prompt, str), "Model prompt must be a string"
    assert model_name, "Model name cannot be empty"
    assert isinstance(model_name, str), "Model name must be a string"
    assert progress_callback is None or callable(progress_callback), "progress_callback must be None or a callable function"
    
    temp_file_path = None
    output = None
    
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
            
            # Assert the downloaded file exists
            assert os.path.exists(file_to_process), f"Downloaded YouTube audio file does not exist: {file_to_process}"
        else:
            logger.info(f"Processing local audio file: {audio_file}")
            file_to_process = audio_file
            
            # Assert the local file exists
            assert os.path.exists(file_to_process), f"Local audio file does not exist: {file_to_process}"
            
        # Validate input
        try:
            validated_input = validate_input(file_to_process)
            # Assert validated input is not None
            assert validated_input is not None, "Validated input cannot be None"
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise ValidationError(f"Input validation failed: {str(e)}")
        
        # Report progress before model processing
        if progress_callback:
            progress_callback(ProcessingProgress("Processing with AI model", 0.5))
        
        # Process with Gemini using the newer API
        try:
            model = genai.GenerativeModel(model_name)
            
            # Assert model is not None
            assert model is not None, "Failed to create Gemini model"
            
            # Open the file in binary mode
            with open(file_to_process, "rb") as f:
                file_content = f.read()
            
            # Assert file content is not empty
            assert file_content, "Audio file content cannot be empty"
            
            # Create a file part for the model
            file_part = {"mime_type": "audio/mpeg", "data": file_content}
            
            # Generate content with the file and prompt
            response = model.generate_content([model_prompt, file_part])
            
            # Assert response is not None
            assert response is not None, "Model response cannot be None"
            assert hasattr(response, 'text'), "Model response must have a text attribute"
            assert response.text, "Model response text cannot be empty"
            
            # Report completion
            if progress_callback:
                progress_callback(ProcessingProgress("Processing complete", 1.0))
            
            # Create and return output
            output = create_output(response.text)
            
            # Assert output is not None
            assert output is not None, "Created output cannot be None"
            
            return output
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
        # Ensure temporary files are cleaned up
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                # Make sure the file is not in use
                import time
                for attempt in range(3):
                    try:
                        os.remove(temp_file_path)
                        logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                        break
                    except PermissionError:
                        # File might still be in use, wait a bit and retry
                        time.sleep(0.5)
                    except Exception as e:
                        logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
                        break
                else:
                    logger.warning(f"Could not clean up temporary file after multiple attempts: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
        
        # Return the output if we have it, otherwise re-raise the exception
        if output is not None:
            return output

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
