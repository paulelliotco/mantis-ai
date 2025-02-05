import os
import tempfile
from typing import Callable, TypeVar, Any
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import google.generativeai as genai

T = TypeVar('T')

class MantisError(Exception):
    """Base exception class for Mantis errors."""
    pass

def is_youtube_url(url: str) -> bool:
    """Check if the given URL is a YouTube URL."""
    parsed = urlparse(url)
    return any(
        domain in parsed.netloc
        for domain in ['youtube.com', 'youtu.be', 'www.youtube.com']
    )

def stream_youtube_audio(url: str) -> str:
    """Download audio from a YouTube URL to a temporary file without using ffmpeg.
    
    This function uses yt_dlp's ability to select the best audio stream with an mp3 extension
    if available. If an mp3 stream is not available, it falls back to the best available audio stream.
    Note: In the fallback case, the file extension will still be '.mp3' even if the content is not mp3.
    """
    temp_dir = tempfile.gettempdir()
    # The output file is designated as an mp3 file.
    temp_file = os.path.join(temp_dir, 'temp_audio.mp3')
    
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio',
        'outtmpl': temp_file,
        'noplaylist': True,
        'quiet': True,  # Suppress most output
        'no_warnings': True,  # Suppress warnings
        'progress_hooks': [],  # Disable progress output
        'logger': None  # Disable logger output
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return temp_file

def process_audio_with_gemini(
    audio_file: str,
    validate_input: Callable[[str], Any],
    create_output: Callable[[str], T],
    model_prompt: str
) -> T:
    """Process audio with Gemini AI using the provided input/output handlers."""
    temp_file_path = None
    
    try:
        # Handle YouTube URLs
        if is_youtube_url(audio_file):
            temp_file_path = stream_youtube_audio(audio_file)
            file_to_process = temp_file_path
        else:
            file_to_process = audio_file
            
        # Validate input
        validate_input(file_to_process)
        
        # Upload and process with Gemini
        uploaded_file = genai.upload_file(file_to_process)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([model_prompt, uploaded_file])
        
        # Create and return output
        return create_output(response.text)
        
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def cleanup_temp_file(file_path: str) -> None:
    """Clean up temporary files."""
    if os.path.exists(file_path):
        os.remove(file_path)
