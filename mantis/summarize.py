from typing import Union, Optional, Callable
from .models import SummarizeInput, SummarizeOutput, ProcessingProgress
from .utils import (
    process_audio_with_gemini,
    MantisError,
    DEFAULT_SAFETY_SETTINGS,
    DEFAULT_STRING_RESPONSE_SCHEMA,
)


def summarize(
    audio_file: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    max_length: Optional[int] = None,
    language: str = "English",
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
        language: Language for the summary output (default: English)
        progress_callback: Optional callback function to report progress
        
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
        f"You are a highly skilled AI trained in language comprehension and summarization. "
        f"I would like you to read the text delimited by triple quotes and summarize it into a concise abstract paragraph. "
        f"Aim to retain the most important points, providing a coherent and readable summary that could help a person understand "
        f"the main points of the discussion without needing to read the entire text. "
        f"Please avoid unnecessary details or tangential points. Only give me the output and nothing else. "
        f"Do not wrap responses in quotes. Respond in the {language} language. "
        f"\"\"\" {{transcription}} \"\"\""
    )
    
    # Assert prompt is not empty
    assert prompt, "Prompt cannot be empty"
    
    if max_length:
        # Insert the max length requirement before the final instruction
        prompt = prompt.replace(
            "Only give me the output and nothing else.",
            f"Keep the summary under {max_length} characters. Only give me the output and nothing else."
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
        safety_settings=DEFAULT_SAFETY_SETTINGS,
        response_schema=DEFAULT_STRING_RESPONSE_SCHEMA,
        generation_config={"response_mime_type": "text/plain"},
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
