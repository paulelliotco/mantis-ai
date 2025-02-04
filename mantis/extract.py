import os
from .models import ExtractInput, ExtractOutput
import google.generativeai as genai
from .utils import process_audio_with_gemini

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def extract(audio_file: str, prompt: str) -> ExtractOutput:
    """Extract information from an audio source using Gemini AI."""
    return process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: ExtractInput(audio_file=x, prompt=prompt),
        create_output=lambda x: ExtractOutput(extraction=x),
        model_prompt=prompt,
    )
