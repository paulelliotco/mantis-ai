import os
from typing import Union, Optional, Callable
import google.generativeai as genai
from .models import ExtractInput, ExtractOutput, ProcessingProgress
from .utils import process_audio_with_gemini, MantisError

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def extract(
    audio_file: str, 
    prompt: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    structured_output: bool = False,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, ExtractOutput]:
    """
    Extract information from an audio source using Gemini AI.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        prompt: Custom prompt specifying what information to extract
        raw_output: If True, returns the full ExtractOutput object.
                   If False (default), returns just the extraction string.
        model: The Gemini model to use for extraction
        structured_output: Whether to attempt to return structured data
        progress_callback: Optional callback function to report progress
        
    Returns:
        Either a string containing the extracted information or an ExtractOutput object
        
    Raises:
        MantisError: If there's an error during extraction
    """
    # Enhance prompt for structured output if requested
    enhanced_prompt = prompt
    if structured_output:
        enhanced_prompt = f"{prompt} Please format your response as structured data that can be parsed as JSON."
    
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: ExtractInput(
            audio_file=x, 
            prompt=prompt, 
            model=model,
            structured_output=structured_output
        ),
        create_output=lambda x: ExtractOutput(
            extraction=x,
            structured_data=None  # In a real implementation, we would attempt to parse JSON here
        ),
        model_prompt=enhanced_prompt,
        model_name=model,
        progress_callback=progress_callback
    )
    
    if raw_output:
        return result
    else:
        # Return the 'extraction' attribute if present; otherwise, return result directly.
        if hasattr(result, 'extraction'):
            return result.extraction
        else:
            return result
