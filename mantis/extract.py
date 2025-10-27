import json
import logging
from typing import Callable, Optional, Union

from google.genai import types

from .models import ExtractInput, ExtractOutput, ExtractionResult, ProcessingProgress
from .utils import MantisError, process_audio_with_gemini


logger = logging.getLogger("mantis.extract")


DEFAULT_EXTRACTION_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "summary": types.Schema(type=types.Type.STRING, description="Concise description of the audio"),
        "key_points": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
            description="Major takeaways or bullet points",
        ),
        "entities": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
            description="Important people, organizations, or places mentioned",
        ),
        "action_items": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
            description="Follow-up tasks derived from the conversation",
        ),
        "raw_text": types.Schema(type=types.Type.STRING, description="Verbatim excerpt or supporting text"),
    },
)



def extract(
    audio_file: str,
    prompt: str,
    raw_output: bool = False,
    model: str = "gemini-1.5-pro-latest",
    structured_output: bool = False,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
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
        enhanced_prompt = (
            f"{prompt} Return your answer using the provided schema, focusing on factual data. "
            "If a field is not applicable, omit it."
        )
    
    # Assert enhanced prompt is not empty
    assert enhanced_prompt, "Enhanced prompt cannot be empty"
    
    def _create_plain_output(text: str) -> ExtractOutput:
        return ExtractOutput(extraction=text, structured_data=None)

    def _create_structured_output(text: str) -> ExtractOutput:
        try:
            data = json.loads(text) if text else {}
            validated = ExtractionResult.model_validate(data)
            payload = validated.model_dump(exclude_none=True)
            extraction_text = payload.get("summary") or payload.get("raw_text") or prompt
            return ExtractOutput(extraction=extraction_text, structured_data=payload)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to parse structured extraction output: %s", exc)
            return ExtractOutput(extraction=text, structured_data=None)

    result = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: ExtractInput(
            audio_file=x,
            prompt=prompt,
            model=model,
            structured_output=structured_output,
        ),
        create_output=_create_structured_output if structured_output else _create_plain_output,
        model_prompt=enhanced_prompt,
        model_name=model,
        progress_callback=progress_callback,
        response_schema=DEFAULT_EXTRACTION_SCHEMA if structured_output else None,
        output_mime_type="application/json" if structured_output else None,
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
