import os
from .models import TranscriptionInput, TranscriptionOutput
import google.generativeai as genai
from .utils import process_audio_with_gemini

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

def transcribe(audio_file: str, raw_output: bool = False) -> str | TranscriptionOutput:
    """Transcribe an audio source using Gemini AI.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        raw_output: If True, returns the full TranscriptionOutput object. 
                   If False (default), returns just the transcription string.
    """
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: TranscriptionInput(audio_file=x),
        create_output=lambda x: TranscriptionOutput(transcription=x),
        model_prompt="Transcribe the following audio.",
    )
    
    if raw_output:
        return result
    else:
        # If result has a 'transcription' attribute, return it; otherwise, assume result is already a string.
        if hasattr(result, 'transcription'):
            return result.transcription
        else:
            return result
