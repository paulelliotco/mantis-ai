import os
from .models import TranscriptionInput, TranscriptionOutput
import google.generativeai as genai
from .utils import process_audio_with_gemini


# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def transcribe(audio_file: str) -> TranscriptionOutput:
    """Transcribe an audio source using Gemini AI."""
    return process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: TranscriptionInput(audio_file=x),
        create_output=lambda x: TranscriptionOutput(transcription=x),
        model_prompt="Transcribe the following audio.",
    )
