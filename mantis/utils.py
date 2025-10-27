import io
import mimetypes
import os
import tempfile
import threading
import time
import logging
from typing import Callable, TypeVar, Any, Dict, Optional
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import google.generativeai as genai
from google.generativeai import protos, types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .models import ProcessingProgress

# Set up logging
logger = logging.getLogger("mantis")

# Progress constants for consistent UX updates
_INITIAL_PROGRESS = 0.0
_DOWNLOAD_PROGRESS_START = 0.05
_DOWNLOAD_PROGRESS_END = 0.25
_VALIDATION_PROGRESS = 0.3
_UPLOAD_PREP_PROGRESS = 0.35
_UPLOAD_PROGRESS_END = 0.6
_FILE_PROCESSING_END = 0.75
_MODEL_INVOKE_PROGRESS = 0.8
_RESPONSE_PROGRESS = 0.9
_COMPLETE_PROGRESS = 1.0

_AUDIO_MIME_OVERRIDES: Dict[str, str] = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
}

_SOUNDFILE_FORMAT_MIMES: Dict[str, str] = {
    "AIFF": "audio/aiff",
    "FLAC": "audio/flac",
    "MP3": "audio/mpeg",
    "MP4": "audio/mp4",
    "OGG": "audio/ogg",
    "WAV": "audio/wav",
}

_DEFAULT_MIME_TYPE = "application/octet-stream"

_uploaded_file_cache: Dict[str, Dict[str, str]] = {}
_uploaded_file_cache_lock = threading.Lock()


class _ProgressFile:
    """Wrap a file object to emit incremental upload progress callbacks."""

    def __init__(self, file_obj: io.BufferedIOBase, chunk_callback: Optional[Callable[[int], None]] = None):
        self._file_obj = file_obj
        self._chunk_callback = chunk_callback

    def read(self, size: int = -1) -> bytes:
        data = self._file_obj.read(size)
        if data and self._chunk_callback:
            self._chunk_callback(len(data))
        return data

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        return self._file_obj.seek(offset, whence)

    def tell(self) -> int:
        return self._file_obj.tell()

    def close(self) -> None:
        self._file_obj.close()

    def __getattr__(self, item: str) -> Any:
        return getattr(self._file_obj, item)


def _detect_mime_type(file_path: str) -> str:
    """Detect the MIME type of the provided audio file."""

    extension = os.path.splitext(file_path)[1].lower()
    if extension in _AUDIO_MIME_OVERRIDES:
        return _AUDIO_MIME_OVERRIDES[extension]

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type

    try:
        import soundfile as sf  # type: ignore

        with sf.SoundFile(file_path) as audio_file:
            format_name = (audio_file.format or "").upper()
        if format_name in _SOUNDFILE_FORMAT_MIMES:
            return _SOUNDFILE_FORMAT_MIMES[format_name]
    except ImportError:
        logger.debug("soundfile library not available for MIME detection; using fallback")
    except Exception as exc:
        logger.debug("Failed to inspect audio with soundfile: %s", exc)

    logger.debug("Falling back to default MIME type for %s", file_path)
    return _DEFAULT_MIME_TYPE


def _get_file_cache_key(file_path: str) -> str:
    stats = os.stat(file_path)
    absolute_path = os.path.abspath(file_path)
    return f"{absolute_path}:{int(stats.st_mtime_ns)}:{stats.st_size}"


def _get_cached_uploaded_file(cache_key: str) -> Optional[types.File]:
    with _uploaded_file_cache_lock:
        cached = _uploaded_file_cache.get(cache_key)

    if not cached:
        return None

    try:
        file = genai.get_file(cached["name"])
    except Exception as exc:  # pragma: no cover - depends on external API availability
        logger.debug("Failed to retrieve cached Gemini file %s: %s", cached.get("name"), exc)
        with _uploaded_file_cache_lock:
            _uploaded_file_cache.pop(cache_key, None)
        return None

    if file.state == protos.File.State.FAILED:
        logger.debug("Cached Gemini file %s is in FAILED state; ignoring cache", file.name)
        with _uploaded_file_cache_lock:
            _uploaded_file_cache.pop(cache_key, None)
        return None

    return file


def _store_uploaded_file(cache_key: str, file: types.File) -> None:
    with _uploaded_file_cache_lock:
        _uploaded_file_cache[cache_key] = {
            "name": file.name,
            "uri": file.uri,
            "mime_type": file.mime_type,
        }


def _wait_for_file_processing(
    file: types.File,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
    poll_interval: float = 1.0,
    timeout: float = 300.0,
) -> types.File:
    start_time = time.time()

    while file.state == protos.File.State.PROCESSING:
        if progress_callback:
            elapsed_ratio = min((time.time() - start_time) / max(timeout, poll_interval), 1.0)
            progress_value = _UPLOAD_PROGRESS_END + elapsed_ratio * (_FILE_PROCESSING_END - _UPLOAD_PROGRESS_END)
            progress_callback(
                ProcessingProgress(
                    stage="Processing uploaded audio on Gemini",
                    progress=progress_value,
                    phase="processing",
                    detail=f"File {file.display_name or file.name} is processing",
                )
            )

        time.sleep(poll_interval)

        try:
            file = genai.get_file(file.name)
        except Exception as exc:  # pragma: no cover - depends on external API availability
            logger.error("Failed to poll uploaded file status: %s", exc)
            raise AudioProcessingError(f"Failed to poll uploaded file status: {exc}") from exc

        if time.time() - start_time > timeout:
            raise AudioProcessingError("Timed out waiting for Gemini to process the uploaded file")

    if file.state == protos.File.State.FAILED:
        error_message = getattr(file.error, "message", "Unknown error") if file.error else "Unknown error"
        raise AudioProcessingError(f"Gemini failed to process the uploaded file: {error_message}")

    if progress_callback:
        progress_callback(
            ProcessingProgress(
                stage="Gemini finished preparing the upload",
                progress=_FILE_PROCESSING_END,
                phase="processing",
                detail=f"File ready: {file.display_name or file.name}",
            )
        )

    return file


def _upload_file_with_progress(
    file_path: str,
    mime_type: str,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
) -> types.File:
    file_size = os.path.getsize(file_path)
    uploaded_bytes = 0

    def on_chunk(chunk_size: int) -> None:
        nonlocal uploaded_bytes
        uploaded_bytes += chunk_size
        if progress_callback and file_size > 0:
            fraction = min(uploaded_bytes / file_size, 1.0)
            progress_value = _UPLOAD_PREP_PROGRESS + fraction * (_UPLOAD_PROGRESS_END - _UPLOAD_PREP_PROGRESS)
            detail = f"Uploaded {uploaded_bytes:,} of {file_size:,} bytes"
            progress_callback(
                ProcessingProgress(
                    stage="Uploading audio to Gemini",
                    progress=progress_value,
                    phase="upload",
                    detail=detail,
                )
            )

    if progress_callback:
        progress_callback(
            ProcessingProgress(
                stage="Preparing audio upload",
                progress=_UPLOAD_PREP_PROGRESS,
                phase="upload",
                detail=os.path.basename(file_path),
            )
        )

    if progress_callback and file_size > 0:
        with open(file_path, "rb") as raw_file:
            progress_file = _ProgressFile(raw_file, on_chunk)
            uploaded = genai.upload_file(
                path=progress_file,
                mime_type=mime_type,
                display_name=os.path.basename(file_path),
                resumable=True,
            )
    else:
        uploaded = genai.upload_file(
            path=file_path,
            mime_type=mime_type,
            display_name=os.path.basename(file_path),
            resumable=True,
        )

    if progress_callback:
        progress_callback(
            ProcessingProgress(
                stage="Upload complete",
                progress=_UPLOAD_PROGRESS_END,
                phase="upload",
                detail=os.path.basename(file_path),
            )
        )

    return _wait_for_file_processing(uploaded, progress_callback)


def _prepare_uploaded_file(
    file_path: str,
    mime_type: str,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
) -> types.File:
    cache_key = _get_file_cache_key(file_path)
    cached = _get_cached_uploaded_file(cache_key)

    if cached is not None:
        logger.debug("Reusing cached Gemini file for %s", file_path)
        if progress_callback:
            progress_callback(
                ProcessingProgress(
                    stage="Reusing cached Gemini upload",
                    progress=_UPLOAD_PROGRESS_END,
                    phase="upload",
                    detail=cached.display_name or cached.name,
                )
            )
        return _wait_for_file_processing(cached, progress_callback)

    logger.debug("Uploading new audio file to Gemini: %s", file_path)
    uploaded = _upload_file_with_progress(file_path, mime_type, progress_callback)
    _store_uploaded_file(cache_key, uploaded)
    return uploaded


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
    
    if progress_callback:
        progress_callback(
            ProcessingProgress(
                stage="Preparing YouTube download",
                progress=_DOWNLOAD_PROGRESS_START,
                phase="download",
                detail=url,
            )
        )

    def progress_hook(d: Dict[str, Any]) -> None:
        if not progress_callback:
            return

        status = d.get('status')
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes') or 0

        fraction = 0.0
        if total_bytes:
            fraction = min(downloaded_bytes / total_bytes, 1.0)
        elif downloaded_bytes:
            fraction = 0.0 if status != 'finished' else 1.0

        if status == 'finished':
            fraction = 1.0
            if total_bytes == 0:
                total_bytes = downloaded_bytes

        progress_value = _DOWNLOAD_PROGRESS_START + fraction * (_DOWNLOAD_PROGRESS_END - _DOWNLOAD_PROGRESS_START)

        if total_bytes:
            detail = f"{downloaded_bytes:,}/{total_bytes:,} bytes"
        else:
            detail = f"{downloaded_bytes:,} bytes"

        stage = "Downloading YouTube audio" if status != 'finished' else "Finished downloading YouTube audio"

        progress_callback(
            ProcessingProgress(
                stage=stage,
                progress=min(progress_value, _DOWNLOAD_PROGRESS_END),
                phase="download",
                detail=detail,
            )
        )

    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio/best',
        'outtmpl': temp_file,
        'noplaylist': True,
        'quiet': True,  # Suppress most output
        'no_warnings': True,  # Suppress warnings
        'progress_hooks': [progress_hook] if progress_callback else [],
        'logger': None,  # Disable logger output
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
    
    temp_file_path: Optional[str] = None
    output: Optional[T] = None

    try:
        if progress_callback:
            progress_callback(
                ProcessingProgress(
                    stage="Starting processing",
                    progress=_INITIAL_PROGRESS,
                    phase="initializing",
                    detail=audio_file,
                )
            )

        # Handle YouTube URLs
        if is_youtube_url(audio_file):
            logger.info(f"Processing YouTube URL: {audio_file}")
            temp_file_path = stream_youtube_audio(audio_file, progress_callback)
            file_to_process = temp_file_path

            # Assert the downloaded file exists
            assert os.path.exists(file_to_process), f"Downloaded YouTube audio file does not exist: {file_to_process}"
        else:
            logger.info(f"Processing local audio file: {audio_file}")
            file_to_process = audio_file

            # Assert the local file exists
            assert os.path.exists(file_to_process), f"Local audio file does not exist: {file_to_process}"

            if progress_callback:
                progress_callback(
                    ProcessingProgress(
                        stage="Loaded local audio file",
                        progress=_DOWNLOAD_PROGRESS_END,
                        phase="initializing",
                        detail=file_to_process,
                    )
                )

        # Validate input
        try:
            validated_input = validate_input(file_to_process)
            assert validated_input is not None, "Validated input cannot be None"
            if progress_callback:
                progress_callback(
                    ProcessingProgress(
                        stage="Validated audio input",
                        progress=_VALIDATION_PROGRESS,
                        phase="initializing",
                        detail=os.path.basename(file_to_process),
                    )
                )
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise ValidationError(f"Input validation failed: {str(e)}")

        mime_type = _detect_mime_type(file_to_process)
        logger.debug("Detected MIME type %s for %s", mime_type, file_to_process)

        uploaded_file = _prepare_uploaded_file(file_to_process, mime_type, progress_callback)

        try:
            model = genai.GenerativeModel(model_name)
            assert model is not None, "Failed to create Gemini model"

            if progress_callback:
                progress_callback(
                    ProcessingProgress(
                        stage="Submitting audio to Gemini model",
                        progress=_MODEL_INVOKE_PROGRESS,
                        phase="processing",
                        detail=model_name,
                    )
                )

            response = model.generate_content(
                [
                    {"text": model_prompt},
                    {
                        "file_data": {
                            "file_uri": uploaded_file.uri,
                            "mime_type": uploaded_file.mime_type or mime_type,
                        }
                    },
                ]
            )

            assert response is not None, "Model response cannot be None"
            assert hasattr(response, "text"), "Model response must have a text attribute"
            assert response.text, "Model response text cannot be empty"

            if progress_callback:
                progress_callback(
                    ProcessingProgress(
                        stage="Received response from Gemini",
                        progress=_RESPONSE_PROGRESS,
                        phase="response",
                        detail=model_name,
                    )
                )

            output = create_output(response.text)
            assert output is not None, "Created output cannot be None"

            if progress_callback:
                progress_callback(
                    ProcessingProgress(
                        stage="Processing complete",
                        progress=_COMPLETE_PROGRESS,
                        phase="complete",
                    )
                )

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
