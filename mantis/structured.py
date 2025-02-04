from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import google.generativeai as genai
import os
from .models import ProcessingOptions
import mantis.utils as utils
from typing import Optional

# Configure Gemini AI with your API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

T = TypeVar('T', bound=BaseModel)

def extract_structured(
    audio_file: str,
    model: Type[T],
    description: Optional[str] = None,
    options: Optional[ProcessingOptions] = None
) -> T:
    """
    Extract structured information from audio using a user-defined Pydantic model.

    Args:
        audio_file (str): Path to the audio file or YouTube URL
        model (Type[BaseModel]): A Pydantic model class defining the desired output structure
        description (Optional[str]): Optional description to guide the extraction
        options (Optional[ProcessingOptions]): Processing options for the extraction

    Returns:
        An instance of the provided model populated with extracted data

    Example:
        ```python
        from pydantic import BaseModel
        from typing import List

        class SpeakerInfo(BaseModel):
            name: str
            topics: List[str]
            speaking_time: float

        result = extract_structured(
            "meeting.mp3",
            model=SpeakerInfo,
            description="Extract information about the main speaker"
        )
        ```
    """
    temp_file_path: Optional[str] = None

    # Handle YouTube URLs
    if utils.is_youtube_url(audio_file):
        try:
            temp_file_path = utils.stream_youtube_audio(audio_file)
            file_to_process = temp_file_path
        except Exception as e:
            raise ConnectionError(f"Failed to stream audio from YouTube: {e}") from e
    else:
        file_to_process = audio_file

    try:
        # Upload the audio file to Gemini AI
        uploaded_file = genai.upload_file(file_to_process)

        # Generate a schema description for the LLM
        schema = model.model_json_schema()
        
        # Create the prompt
        prompt = f"""
        Extract information from the audio and provide output exactly matching this JSON schema:
        {schema}

        {f"Additional context: {description}" if description else ""}
        
        Return only valid JSON matching the schema exactly.
        """

        # Perform extraction using Gemini AI
        genai_model = genai.GenerativeModel("gemini-1.5-flash")
        response = genai_model.generate_content([prompt, uploaded_file])
        
        # Parse the response into the model
        try:
            return model.model_validate_json(response.text)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM output into the specified model: {e}")

    except Exception as e:
        raise RuntimeError(f"Extraction failed: {e}")

    finally:
        # Clean up temporary file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)