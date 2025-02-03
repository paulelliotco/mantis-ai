import os
from pydantic import ValidationError
from .models import SummarizeInput, SummarizeOutput
import google.generativeai as genai
from .utils import is_youtube_url, stream_youtube_audio
from typing import Optional

# Configure Gemini AI with your API key from environment variables.
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY'))

def summarize(audio_file: str) -> SummarizeOutput:
    """
    Summarize the content of an audio source using Gemini AI.

    Args:
        audio_file (str): Path to the audio file or YouTube URL to be summarized.

    Returns:
        SummarizeOutput: The summary of the audio source.
    """
    temp_file_path: Optional[str] = None
    try:
        # Validate input using the SummarizeInput model
        input_data = SummarizeInput(audio_file=audio_file)
    except Exception as e:
        raise ValueError(f"Invalid input: {e}") from e

    # Use the utility function to check if the audio_file is a YouTube URL
    if is_youtube_url(input_data.audio_file):
        try:
            # Stream audio from YouTube and get the temporary file path
            temp_file_path = stream_youtube_audio(input_data.audio_file)
            file_to_summarize = temp_file_path
        except Exception as e:
            raise ConnectionError(f"Failed to stream audio from YouTube: {e}") from e
    else:
        file_to_summarize = input_data.audio_file

    try:
        # Upload the audio file to Gemini AI
        uploaded_file = genai.upload_file(file_to_summarize)
    except Exception as upload_error:
        raise ConnectionError(f"Failed to upload audio file: {upload_error}")

    try:
        # Perform summarization using Gemini AI's GenerativeModel
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = "Summarize the following audio."
        response = model.generate_content([prompt, uploaded_file])
        summary = response.text
    except Exception as gen_error:
        raise RuntimeError(f"Summarization failed: {gen_error}")

    try:
        # Validate the output using Pydantic
        output_data = SummarizeOutput(summary=summary)
    except ValidationError as e:
        raise ValueError(f"Invalid summarization output: {e}")

    return output_data