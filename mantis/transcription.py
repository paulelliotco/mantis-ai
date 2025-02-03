import os
from pydantic import ValidationError
from .models import TranscriptionInput, TranscriptionOutput
import google.generativeai as genai
import mantis.utils as utils  # Import the module instead of individual functions
from typing import Optional

# Configure Gemini AI with your API key from environment variables.
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))


def transcribe(audio_file: str) -> TranscriptionOutput:
    """
    Transcribe an audio source using Gemini AI.

    Args:
        audio_file (str): Path to the MP3 file or YouTube URL to be transcribed.

    Returns:
        TranscriptionOutput: The transcription result.
    """
    temp_file_path: Optional[str] = None
    try:
        # Validate input using the TranscriptionInput model
        input_data = TranscriptionInput(audio_file=audio_file)
    except Exception as e:
        raise ValueError(f"Invalid input: {e}") from e

    # Use the utility function to check if the audio_file is a YouTube URL
    if utils.is_youtube_url(input_data.audio_file):
        try:
            # Stream audio from YouTube and get the temporary file path
            temp_file_path = utils.stream_youtube_audio(input_data.audio_file)
            file_to_transcribe = temp_file_path
        except Exception as e:
            raise ConnectionError(f"Failed to stream audio from YouTube: {e}") from e
    else:
        file_to_transcribe = input_data.audio_file

    try:
        # Upload the audio file to Gemini AI
        uploaded_file = genai.upload_file(file_to_transcribe)
    except Exception as upload_error:
        raise ConnectionError(f"Failed to upload file to Gemini AI: {upload_error}")

    try:
        # Perform transcription using Gemini AI's GenerativeModel
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = "Transcribe the following audio."
        response = model.generate_content([prompt, uploaded_file])
        transcription = response.text
    except Exception as gen_error:
        raise RuntimeError(f"Transcription failed: {gen_error}")

    try:
        # Validate output using Pydantic
        output_data = TranscriptionOutput(transcription=transcription)
    except ValidationError as e:
        raise ValueError(f"Invalid transcription output: {e}")

    return output_data
