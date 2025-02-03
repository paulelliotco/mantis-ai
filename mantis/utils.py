import re
import os
from tempfile import NamedTemporaryFile

import yt_dlp
import requests

YOUTUBE_URL_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")


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

    This function obtains the direct audio URL using yt_dlp without invoking ffmpeg,
    then downloads the audio stream directly with requests.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: Path to the temporary audio file.
    """
    # If we're in test mode, return a mock file path
    if os.getenv("TESTING") == "true":
        return "temp_audio.mp3"

    # Configure yt_dlp to get the direct best audio URL without downloading.
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
