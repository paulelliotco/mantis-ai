import os
import mimetypes
import tempfile
import logging
from typing import Callable, TypeVar, Any, Dict, Optional, Union, List
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .models import ProcessingProgress

# Set up logging
logger = logging.getLogger("mantis")

DEFAULT_SAFETY_SETTINGS: List[Dict[str, Any]] = [
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_NONE"},
]

DEFAULT_STRING_RESPONSE_SCHEMA: Dict[str, Any] = {"type": "STRING"}

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


def _normalize_model_name(model_name: str) -> str:
    name = model_name.strip()
    if name.startswith("models/") or name.startswith("tunedModels/"):
        return name
    return f"models/{name}"


def create_genai_client() -> genai.Client:
    """Create a configured Google GenAI client following documented precedence."""
    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GENAI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )
    api_endpoint = (
        os.getenv("GOOGLE_API_ENDPOINT")
        or os.getenv("GOOGLE_GENAI_API_ENDPOINT")
        or os.getenv("GOOGLE_VERTEX_AI_ENDPOINT")
    )

    client_kwargs: Dict[str, Any] = {}
    if api_endpoint:
        client_kwargs["api_endpoint"] = api_endpoint
        logger.debug("Configuring Google GenAI client with custom API endpoint: %s", api_endpoint)

    if api_key:
        client_kwargs["api_key"] = api_key
        logger.debug("Using Google AI Studio API key for GenAI client authentication")
        return genai.Client(**client_kwargs)

    project = (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GOOGLE_GENAI_PROJECT")
        or os.getenv("GOOGLE_VERTEX_PROJECT")
    )
    location = (
        os.getenv("GOOGLE_CLOUD_LOCATION")
        or os.getenv("GOOGLE_CLOUD_REGION")
        or os.getenv("GOOGLE_VERTEX_LOCATION")
        or "us-central1"
    )

    if project:
        client_kwargs["vertexai"] = {"project": project, "location": location}
        logger.debug(
            "Using Vertex AI configuration for GenAI client authentication (project=%s, location=%s)",
            project,
            location,
        )
        return genai.Client(**client_kwargs)

    raise MantisError(
        "Unable to configure Google GenAI client. Set GOOGLE_API_KEY (AI Studio) or GOOGLE_CLOUD_PROJECT"
        " and GOOGLE_CLOUD_LOCATION (Vertex AI)."
    )

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
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
    safety_settings: Optional[List[Dict[str, Any]]] = None,
    response_schema: Optional[Dict[str, Any]] = None,
    generation_config: Optional[Dict[str, Any]] = None,
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
        safety_settings: Optional list of safety settings to apply to the request
        response_schema: Optional response schema (JSON schema dict) for structured outputs
        generation_config: Optional generation configuration parameters
        
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
    assert safety_settings is None or isinstance(safety_settings, list), "safety_settings must be a list or None"
    assert response_schema is None or isinstance(response_schema, dict), "response_schema must be a dict or None"
    assert generation_config is None or isinstance(generation_config, dict), "generation_config must be a dict or None"
    
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
        
        # Process with Gemini using the modern client API
        try:
            client = create_genai_client()

            mime_type, _ = mimetypes.guess_type(file_to_process)
            if not mime_type:
                mime_type = "application/octet-stream"

            with open(file_to_process, "rb") as file_handle:
                uploaded_file = client.files.upload(
                    file=file_handle,
                    display_name=os.path.basename(file_to_process),
                    mime_type=mime_type,
                )

            file_uri = getattr(uploaded_file, "name", None) or getattr(uploaded_file, "uri", None)
            if not file_uri:
                raise ModelInferenceError("Uploaded file response did not provide a file identifier")

            contents = [
                {
                    "role": "user",
                    "parts": [
                        {
                            "file_data": {
                                "file_uri": file_uri,
                                "mime_type": getattr(uploaded_file, "mime_type", mime_type),
                            }
                        },
                        {"text": model_prompt},
                    ],
                }
            ]

            request_payload: Dict[str, Any] = {
                "model": _normalize_model_name(model_name),
                "contents": contents,
            }

            if safety_settings:
                request_payload["safety_settings"] = safety_settings

            if response_schema:
                request_payload["response_schema"] = response_schema

            if generation_config:
                request_payload["generation_config"] = generation_config

            response = client.responses.generate(**request_payload)

            response_text = getattr(response, "output_text", None)
            if not response_text and hasattr(response, "text"):
                response_text = getattr(response, "text")

            if not response_text and hasattr(response, "candidates"):
                candidate_texts: List[str] = []
                for candidate in getattr(response, "candidates", []):
                    candidate_content = getattr(candidate, "content", None)
                    if candidate_content is not None and hasattr(candidate_content, "parts"):
                        for part in getattr(candidate_content, "parts", []):
                            part_text = getattr(part, "text", None)
                            if part_text:
                                candidate_texts.append(part_text)
                            elif isinstance(part, dict) and part.get("text"):
                                candidate_texts.append(part["text"])
                    elif hasattr(candidate, "text") and getattr(candidate, "text"):
                        candidate_texts.append(getattr(candidate, "text"))
                if candidate_texts:
                    response_text = "\n".join(candidate_texts)

            if not response_text:
                raise ModelInferenceError("Model response did not include any text output")

            if progress_callback:
                progress_callback(ProcessingProgress("Processing complete", 1.0))

            output = create_output(response_text)

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
