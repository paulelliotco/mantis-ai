from typing import Callable, Optional, Union

from .models import ProcessingProgress, TranscriptionInput, TranscriptionOutput
from .utils import MantisError, process_audio_with_gemini

def transcribe(
    audio_file: str, 
    raw_output: bool = False,
    clean_output: bool = False,
    model: str = "gemini-1.5-flash-latest",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, TranscriptionOutput]:
    """
    Transcribe an audio source using Gemini AI.
    
    Args:
        audio_file: Path to the audio file or YouTube URL
        raw_output: If True, returns the full TranscriptionOutput object. 
                   If False (default), returns just the transcription string.
        clean_output: If True, removes disfluencies, repetitions, and other speech artifacts.
                     If False (default), provides the verbatim transcription.
        model: The Gemini model to use for transcription
        progress_callback: Optional callback function to report progress
        
    Returns:
        Either a string containing the transcription or a TranscriptionOutput object
        
    Raises:
        MantisError: If there's an error during transcription
    """
    # Assert input validation
    assert audio_file, "Audio file path or URL cannot be empty"
    assert isinstance(audio_file, str), "Audio file path or URL must be a string"
    assert isinstance(raw_output, bool), "raw_output must be a boolean"
    assert isinstance(clean_output, bool), "clean_output must be a boolean"
    assert model, "Model name cannot be empty"
    assert isinstance(model, str), "Model name must be a string"
    
    # Create the appropriate prompt based on clean_output setting
    if clean_output:
        model_prompt = (
            "You are a world-class transcription engine. Listen to the audio and return a polished transcript "
            "without disfluencies (um, uh, etc.), filler words, or repeated fragments. Preserve speaker meaning and "
            "punctuation where possible."
        )
    else:
        model_prompt = (
            "You are a meticulous transcription engine. Listen to the audio and provide a verbatim transcript with "
            "accurate punctuation and speaker cues when available."
        )
    
    # Assert prompt is not empty
    assert model_prompt, "Model prompt cannot be empty"
    
    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: TranscriptionInput(audio_file=x, model=model),
        create_output=lambda x: TranscriptionOutput(transcription=x),
        model_prompt=model_prompt,
        model_name=model,
        progress_callback=progress_callback
    )
    
    # Assert result is not None
    assert result is not None, "Transcription result cannot be None"
    
    if raw_output:
        # Assert result is a TranscriptionOutput object
        assert hasattr(result, 'transcription'), "Raw output must have a transcription attribute"
        return result
    else:
        # If result has a 'transcription' attribute, return it; otherwise, assume result is already a string.
        if hasattr(result, 'transcription'):
            # Assert transcription is not empty
            assert result.transcription, "Transcription cannot be empty"
            return result.transcription
        else:
            # Assert result is a string
            assert isinstance(result, str), "Result must be a string when not returning raw output"
            return result
