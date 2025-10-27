from typing import Callable, Optional, Union

from .models import ProcessingProgress, SummarizeInput, SummarizeOutput
from .utils import MantisError, process_audio_with_gemini


def summarize(
    audio_file: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash-latest",
    max_length: Optional[int] = None,
    language: str = "English",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
    *,
    stream: bool = False,
    stream_callback: Optional[Callable[[str], None]] = None,
    safety_settings: Optional[Any] = None,
    response_schema: Optional[Any] = None,
    response_mime_type: Optional[str] = None,
) -> Union[str, SummarizeOutput]:
    """
    Summarize an audio source using Gemini AI.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        raw_output: If True, returns the full SummarizeOutput object.
                   If False (default), returns just the summary string.
        model: The Gemini model to use for summarization
        max_length: Optional maximum length for the summary in characters
        language: Language for the summary output (default: English)
        progress_callback: Optional callback function to report progress
        stream: If True, stream partial responses as they arrive
        stream_callback: Optional callable to receive streaming text chunks
        safety_settings: Optional Gemini safety settings configuration
        response_schema: Optional schema definition for JSON-formatted responses
        response_mime_type: Optional MIME type for the structured response (for example, "application/json")
        
    Returns:
        Either a string containing the summary or a SummarizeOutput object
        
    Raises:
        MantisError: If there's an error during summarization
    """
    # Assert input validation
    assert audio_file, "Audio file path or URL cannot be empty"
    assert isinstance(audio_file, str), "Audio file path or URL must be a string"
    assert isinstance(raw_output, bool), "raw_output must be a boolean"
    assert model, "Model name cannot be empty"
    assert isinstance(model, str), "Model name must be a string"
    assert max_length is None or (isinstance(max_length, int) and max_length > 0), "max_length must be a positive integer or None"
    assert language, "Language cannot be empty"
    assert isinstance(language, str), "Language must be a string"
    
    # Use the specific prompt format provided by the user
    prompt = (
        "You are an expert meeting assistant. Listen to the attached audio, generate a concise summary that covers the primary "
        "goals, decisions, action items, and any risks. Focus on factual content. Respond only with the summary text in the "
        f"{language} language."
    )
    
    # Assert prompt is not empty
    assert prompt, "Prompt cannot be empty"
    
    if max_length:
        # Insert the max length requirement before the final instruction
        prompt = (
            prompt
            + f" Limit the summary to {max_length} characters while preserving the most critical information."
        )
    
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: SummarizeInput(audio_file=x, model=model, max_length=max_length),
        create_output=lambda x: SummarizeOutput(
            summary=x,
            word_count=len(x.split()) if x else 0
        ),
        model_prompt=prompt,
        model_name=model,
        progress_callback=progress_callback,
        stream=stream,
        stream_callback=stream_callback,
        safety_settings=safety_settings,
        response_schema=response_schema,
        response_mime_type=response_mime_type,
    )
    
    # Assert result is not None
    assert result is not None, "Summarization result cannot be None"
    
    if raw_output:
        # Assert result is a SummarizeOutput object
        assert hasattr(result, 'summary'), "Raw output must have a summary attribute"
        return result
    else:
        # Return the 'summary' attribute if present; otherwise, return result directly.
        if hasattr(result, 'summary'):
            # Assert summary is not empty
            assert result.summary, "Summary cannot be empty"
            return result.summary
        else:
            # Assert result is a string
            assert isinstance(result, str), "Result must be a string when not returning raw output"
            return result
