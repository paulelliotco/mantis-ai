import os
from .models import ExtractInput, ExtractOutput
import google.generativeai as genai
from .utils import process_audio_with_gemini

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def extract(audio_file: str, prompt: str, raw_output: bool = False) -> str | ExtractOutput:
    """Extract information from an audio source using Gemini AI."""
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: ExtractInput(audio_file=x, prompt=prompt),
        create_output=lambda x: ExtractOutput(extraction=x),
        model_prompt=prompt,
    )
    
    if raw_output:
        return result
    else:
        # Return the 'extraction' attribute if present; otherwise, return result directly.
        if hasattr(result, 'extraction'):
            return result.extraction
        else:
            return result
