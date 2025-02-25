import os
from typing import Union, Optional, Callable
import google.generativeai as genai
from .models import TranscriptionInput, TranscriptionOutput, ProcessingProgress
from .utils import process_audio_with_gemini, MantisError

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

def transcribe(
    audio_file: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, TranscriptionOutput]:
    """
    Transcribe an audio source using Gemini AI.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        raw_output: If True, returns the full TranscriptionOutput object. 
                   If False (default), returns just the transcription string.
        model: The Gemini model to use for transcription
        progress_callback: Optional callback function to report progress
        
    Returns:
        Either a string containing the transcription or a TranscriptionOutput object
        
    Raises:
        MantisError: If there's an error during transcription
    """
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: TranscriptionInput(audio_file=x, model=model),
        create_output=lambda x: TranscriptionOutput(transcription=x),
        model_prompt="Transcribe the following audio.",
        model_name=model,
        progress_callback=progress_callback
    )
    
    if raw_output:
        return result
    else:
        # If result has a 'transcription' attribute, return it; otherwise, assume result is already a string.
        if hasattr(result, 'transcription'):
            return result.transcription
        else:
            return result
