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
    # Assert input validation
    assert audio_file, "Audio file path or URL cannot be empty"
    assert isinstance(audio_file, str), "Audio file path or URL must be a string"
    assert prompt, "Prompt cannot be empty"
    assert isinstance(prompt, str), "Prompt must be a string"
    assert isinstance(raw_output, bool), "raw_output must be a boolean"
    assert model, "Model name cannot be empty"
    assert isinstance(model, str), "Model name must be a string"
    assert isinstance(structured_output, bool), "structured_output must be a boolean"
    
    # Enhance prompt for structured output if requested
    enhanced_prompt = prompt
    if structured_output:
        enhanced_prompt = f"{prompt} Please format your response as structured data that can be parsed as JSON."
    
    # Assert enhanced prompt is not empty
    assert enhanced_prompt, "Enhanced prompt cannot be empty"
    
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
    
    # Assert result is not None
    assert result is not None, "Extraction result cannot be None"
    
    if raw_output:
        # Assert result is an ExtractOutput object
        assert hasattr(result, 'extraction'), "Raw output must have an extraction attribute"
        return result
    else:
        # Return the 'extraction' attribute if present; otherwise, return result directly.
        if hasattr(result, 'extraction'):
            # Assert extraction is not empty
            assert result.extraction, "Extraction cannot be empty"
            return result.extraction
        else:
            # Assert result is a string
            assert isinstance(result, str), "Result must be a string when not returning raw output"
            return result
