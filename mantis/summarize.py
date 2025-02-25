import os
from typing import Union, Optional, Callable
import google.generativeai as genai
from .models import SummarizeInput, SummarizeOutput, ProcessingProgress
from .utils import process_audio_with_gemini, MantisError

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def summarize(
    audio_file: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    max_length: Optional[int] = None,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, SummarizeOutput]:
    """
    Summarize an audio source using Gemini AI.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        raw_output: If True, returns the full SummarizeOutput object.
                   If False (default), returns just the summary string.
        model: The Gemini model to use for summarization
        max_length: Optional maximum length for the summary in characters
        progress_callback: Optional callback function to report progress
        
    Returns:
        Either a string containing the summary or a SummarizeOutput object
        
    Raises:
        MantisError: If there's an error during summarization
    """
    prompt = "Summarize the following audio."
    if max_length:
        prompt += f" Keep the summary under {max_length} characters."
    
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: SummarizeInput(audio_file=x, model=model, max_length=max_length),
        create_output=lambda x: SummarizeOutput(
            summary=x,
            word_count=len(x.split()) if x else 0
        ),
        model_prompt=prompt,
        model_name=model,
        progress_callback=progress_callback
    )
    
    if raw_output:
        return result
    else:
        # Return the 'summary' attribute if present; otherwise, return result directly.
        if hasattr(result, 'summary'):
            return result.summary
        else:
            return result
