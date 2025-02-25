from typing import Optional, List, Any, Literal, Union, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator

SUPPORTED_AUDIO_FORMATS = (".mp3", ".wav", ".m4a", ".ogg")


class ProcessingProgress:
    """Model for tracking processing progress."""
    
    def __init__(self, stage: str, progress: float):
        self.stage = stage
        self.progress = progress


class MantisBaseModel(BaseModel):
    """Base model with common configuration for all Mantis models."""
    
    model_config = {
        "extra": "forbid",
        "frozen": True,
    }


class TranscriptionInput(MantisBaseModel):
    """
    Model for input data required for transcription.
    """

    audio_file: str = Field(..., description="Path to the audio file or YouTube URL to be transcribed.")
    model: str = Field("gemini-1.5-flash", description="The Gemini model to use for transcription.")

    @field_validator("audio_file")
    @classmethod
    def validate_audio_file(cls, v: str) -> str:
        if not any(v.endswith(fmt) for fmt in SUPPORTED_AUDIO_FORMATS) and not v.startswith("http"):
            raise ValueError(f"Audio file must end with one of {SUPPORTED_AUDIO_FORMATS} or be a valid URL")
        return v


class TranscriptionOutput(MantisBaseModel):
    """
    Model for the output data after transcription.
    """

    transcription: str = Field(..., description="The transcribed text from the audio source.")
    confidence: Optional[float] = Field(None, description="Confidence score of the transcription if available.")
    duration_seconds: Optional[float] = Field(None, description="Duration of the audio in seconds if available.")


class SummarizeInput(MantisBaseModel):
    audio_file: str = Field(..., description="Path to the audio file or YouTube URL to be summarized.")
    model: str = Field("gemini-1.5-flash", description="The Gemini model to use for summarization.")
    max_length: Optional[int] = Field(None, description="Maximum length of the summary in characters.")

    @field_validator("audio_file")
    @classmethod
    def validate_audio_file(cls, v: str) -> str:
        if not (v.lower().endswith(SUPPORTED_AUDIO_FORMATS) or v.startswith("http")):
            raise ValueError(f"audio_file must be a path to one of {SUPPORTED_AUDIO_FORMATS} file or a YouTube URL.")
        return v


class SummarizeOutput(MantisBaseModel):
    summary: str = Field(..., description="The summarized text from the audio source.")
    word_count: Optional[int] = Field(None, description="Word count of the summary.")


class ExtractInput(MantisBaseModel):
    audio_file: str = Field(..., description="Path to the audio file or YouTube URL for extraction.")
    prompt: str = Field(..., description="Custom prompt specifying what information to extract.")
    model: str = Field("gemini-1.5-flash", description="The Gemini model to use for extraction.")
    structured_output: bool = Field(False, description="Whether to attempt to return structured data.")

    @field_validator("audio_file")
    @classmethod
    def validate_audio_file(cls, v: str) -> str:
        if not (v.lower().endswith(SUPPORTED_AUDIO_FORMATS) or v.startswith("http")):
            raise ValueError(f"audio_file must be a path to one of {SUPPORTED_AUDIO_FORMATS} file or a YouTube URL.")
        return v

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("prompt cannot be empty.")
        return v


class ExtractOutput(MantisBaseModel):
    extraction: str = Field(..., description="The extracted information from the audio source.")
    structured_data: Optional[dict] = Field(None, description="Structured data if available and requested.")
