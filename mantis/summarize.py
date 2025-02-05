import os
from .models import SummarizeInput, SummarizeOutput
import google.generativeai as genai
from .utils import process_audio_with_gemini

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def summarize(audio_file: str, raw_output: bool = False) -> str | SummarizeOutput:
    """Summarize an audio source using Gemini AI."""
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: SummarizeInput(audio_file=x),
        create_output=lambda x: SummarizeOutput(summary=x),
        model_prompt="Summarize the following audio.",
    )
    
    if raw_output:
        return result
    else:
        # Return the 'summary' attribute if present; otherwise, return result directly.
        if hasattr(result, 'summary'):
            return result.summary
        else:
            return result
