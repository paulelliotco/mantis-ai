import os
from pydantic import ValidationError
from .models import ExtractInput, ExtractOutput
import google.generativeai as genai
from .utils import is_youtube_url, stream_youtube_audio
from typing import Optional

# Configure Gemini AI with your API key from environment variables.
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def extract(audio_file: str, prompt: str) -> ExtractOutput:
    """
    Extract key information from an audio source using Gemini AI, with a custom prompt.

    Args:
        audio_file (str): Path to the audio file or YouTube URL.
        prompt (str): Custom prompt specifying what information to extract.

    Returns:
        ExtractOutput: The extraction result containing the extracted information.
    """
    temp_file_path: Optional[str] = None
    try:
        # Validate input using the ExtractInput model
        input_data = ExtractInput(audio_file=audio_file, prompt=prompt)
    except Exception as e:
        raise ValueError(f"Invalid input: {e}") from e

    # Use the utility function to determine if the audio_file is a YouTube URL
    if is_youtube_url(input_data.audio_file):
        try:
            # Stream audio from YouTube and get the temporary file path
            temp_file_path = stream_youtube_audio(input_data.audio_file)
            file_to_extract = temp_file_path
        except Exception as e:
            raise ConnectionError(f"Failed to stream audio from YouTube: {e}") from e
    else:
        file_to_extract = input_data.audio_file

    try:
        # Upload the audio file to Gemini AI
        uploaded_file = genai.upload_file(file_to_extract)
    except Exception as upload_error:
        raise ConnectionError(f"Failed to upload audio file: {upload_error}")

    try:
        # Perform extraction using Gemini AI's GenerativeModel and the custom prompt
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_data.prompt, uploaded_file])
        extraction = response.text
    except Exception as gen_error:
        raise RuntimeError(f"Extraction failed: {gen_error}")

    try:
        # Validate the output using Pydantic
        output_data = ExtractOutput(extraction=extraction)
    except ValidationError as e:
        raise ValueError(f"Invalid extraction output: {e}")

    return output_data
