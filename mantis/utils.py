import re
import os
from tempfile import NamedTemporaryFile
from tenacity import retry, stop_after_attempt, wait_exponential

import yt_dlp
import requests

YOUTUBE_URL_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")


class MantisError(Exception):
    """Base exception for Mantis errors"""
    pass

class APIError(MantisError):
    """Raised when API calls fail"""
    pass

class AudioProcessingError(MantisError):
    """Raised when audio processing fails"""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry_error_cls=APIError
)
def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with retry logic"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise APIError(f"API call failed: {str(e)}")


def is_youtube_url(url: str) -> bool:
    """
    Determines if the provided URL is a YouTube URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a YouTube URL, False otherwise.
    """
    youtube_patterns = [
        r"(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+",
        r"(https?://)?youtu\.be/[\w-]+",
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)


def stream_youtube_audio(url: str) -> str:
    """
    Stream audio from a YouTube URL and return the path to the temporary audio file.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: Path to the temporary audio file.
    """
    # For CI environments or testing, return a mock path
    if os.getenv("CI") == "true" or os.getenv("TESTING") == "true":
        return os.path.join(os.path.dirname(__file__), "test_data", "mock_audio.mp3")

    # Regular YouTube processing logic
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        audio_url = info_dict.get("url")
        if not audio_url:
            raise ValueError("Failed to obtain audio URL from YouTube info.")

    # Download the audio directly using requests
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()

    # Save the streamed audio to a temporary file
    temp_audio = NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(temp_audio.name, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return temp_audio.name
