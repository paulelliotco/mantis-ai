import re
import os
from tempfile import NamedTemporaryFile
from typing import Optional

import yt_dlp
import requests
import subprocess

YOUTUBE_URL_REGEX = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
)

def is_youtube_url(url: str) -> bool:
    """
    Determines if the provided URL is a YouTube URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a YouTube URL, False otherwise.
    """
    youtube_patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?youtu\.be/[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)

def stream_youtube_audio(url: str, output_format: str = "mp3") -> str:
    """
    Streams audio from a YouTube URL and saves it as a temporary file.

    Args:
        url (str): The YouTube URL.
        output_format (str, optional): The format to save the audio. Defaults to "mp3".

    Returns:
        str: The path to the temporary audio file.

    Raises:
        RuntimeError: If the audio streaming or conversion fails.
    """
    try:
        temp_audio_file = "temp_audio." + output_format
        # Use yt-dlp to extract audio
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", output_format,
            "-o", temp_audio_file,
            url
        ], check=True)
        return temp_audio_file
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to stream audio from YouTube: {e}") from e

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
    # Configure yt_dlp to get the direct best audio URL without downloading.
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        audio_url = info_dict.get('url')
        if not audio_url:
            raise ValueError("Failed to obtain audio URL from YouTube info.")

    # Download the audio directly using requests
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()

    # Save the streamed audio to a temporary file
    temp_audio = NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(temp_audio.name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return temp_audio.name 