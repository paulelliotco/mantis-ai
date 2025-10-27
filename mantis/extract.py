import json
import logging
import os
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from pydantic import BaseModel as PydanticBaseModel, ValidationError
import google.generativeai as genai
from .models import ExtractInput, ExtractOutput, ProcessingProgress
from .utils import process_audio_with_gemini, MantisError
from .response_schemas import COMMON_RESPONSE_SCHEMAS, AudioInsightsSchema

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


logger = logging.getLogger("mantis")


def _resolve_response_schema(
    structured_output: bool,
    schema: Optional[Union[str, Dict[str, Any], Type[PydanticBaseModel]]]
) -> Tuple[Optional[Dict[str, Any]], Optional[Callable[[str], Dict[str, Any]]]]:
    """Resolve a schema specification into a JSON schema and parser."""

    if not structured_output:
        return None, None

    resolved_model: Optional[Type[PydanticBaseModel]] = None

    if schema is None:
        resolved_model = AudioInsightsSchema
    elif isinstance(schema, str):
        if schema not in COMMON_RESPONSE_SCHEMAS:
            raise ValueError(
                f"Unknown response schema '{schema}'. Available schemas: {', '.join(COMMON_RESPONSE_SCHEMAS)}"
            )
        resolved_model = COMMON_RESPONSE_SCHEMAS[schema]
    elif isinstance(schema, dict):
        def parser(response_text: str) -> Dict[str, Any]:
            data = json.loads(response_text)
            if not isinstance(data, dict):
                raise TypeError("Structured response must decode to a JSON object.")
            return data

        return schema, parser
    elif isinstance(schema, type) and issubclass(schema, PydanticBaseModel):
        resolved_model = schema
    else:
        raise TypeError("response_schema must be None, a schema key, dict, or Pydantic model class.")

    assert resolved_model is not None, "Resolved Pydantic model cannot be None when structured output is requested."

    def parser(response_text: str) -> Dict[str, Any]:
        model = resolved_model.model_validate_json(response_text)
        return model.model_dump()

    return resolved_model.model_json_schema(), parser


def _parse_structured_response(
    response_text: str,
    parser: Optional[Callable[[str], Dict[str, Any]]]
) -> Optional[Dict[str, Any]]:
    """Attempt to parse structured data from the model response."""

    if not parser:
        return None

    try:
        return parser(response_text)
    except (ValidationError, json.JSONDecodeError, TypeError) as exc:
        logger.warning(
            "Failed to validate structured response against schema: %s. Falling back to raw text.",
            exc,
        )

        # Google guidance recommends falling back to text when the response cannot be parsed.
        # Attempt one more permissive parse by trimming leading/trailing content before giving up.
        try:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            trimmed = response_text[start:end]
            return parser(trimmed)
        except Exception:
            return None


def extract(
    audio_file: str,
    prompt: str,
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    structured_output: bool = False,
    response_schema: Optional[Union[str, Dict[str, Any], Type[PydanticBaseModel]]] = None,
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
        response_schema: Optional schema identifier, JSON schema dictionary, or Pydantic model
            describing the structured response shape when ``structured_output`` is True. If not
            provided, the default ``AudioInsightsSchema`` is used.
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
    
    json_schema, schema_parser = _resolve_response_schema(structured_output, response_schema)

    response_text = process_audio_with_gemini(
        audio_file=audio_file,
        validate_input=lambda x: ExtractInput(
            audio_file=x,
            prompt=prompt,
            model=model,
            structured_output=structured_output
        ),
        create_output=lambda x: x,
        model_prompt=enhanced_prompt,
        model_name=model,
        progress_callback=progress_callback,
        response_schema=json_schema,
    )

    # Assert result is not None
    assert response_text is not None, "Extraction result cannot be None"
    assert isinstance(response_text, str), "Model response must be text"

    structured_data = _parse_structured_response(response_text, schema_parser)

    result = ExtractOutput(
        extraction=response_text,
        structured_data=structured_data,
    )
    
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
