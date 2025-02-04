from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import google.generativeai as genai
import os
from .models import ProcessingOptions
from . import utils

T = TypeVar("T", bound=BaseModel)


def extract_structured(
    audio_file: str, model: Type[T], description: Optional[str] = None, options: Optional[ProcessingOptions] = None
) -> T:
    """Extract structured information from audio using a user-defined Pydantic model."""
    temp_file_path: Optional[str] = None
    # Handle YouTube URLs
    if utils.is_youtube_url(audio_file):
        try:
            temp_file_path = utils.stream_youtube_audio(audio_file)
            file_to_process = temp_file_path
        except Exception as error:
            raise ConnectionError(f"Failed to stream audio from YouTube: {error}") from error
    else:
        file_to_process = audio_file

    try:
        # Upload the audio file to Gemini AI
        uploaded_file = genai.upload_file(file_to_process)

        # Generate a schema description for the LLM
        schema = model.model_json_schema()

        # Create the prompt using a concatenated string for clarity
        prompt = (
            f"Extract information from the audio and provide output exactly matching this JSON schema:\n"
            f"{schema}\n\n"
            f"{f'Additional context: {description}' if description else ''}\n\n"
            "Return only valid JSON matching the schema exactly."
        )

        # Perform extraction using Gemini AI
        genai_model = genai.GenerativeModel("gemini-1.5-flash")
        response = genai_model.generate_content([prompt, uploaded_file])

        # Parse the response into the model
        try:
            return model.model_validate_json(response.text)
        except Exception as error:
            raise ValueError(f"Failed to parse LLM output into the specified model: {error}")

    except Exception as error:
        raise RuntimeError(f"Extraction failed: {error}")

    finally:
        # Clean up temporary file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
