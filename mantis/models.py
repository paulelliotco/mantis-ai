from typing import Optional, Callable
from pydantic import BaseModel, Field, field_validator

SUPPORTED_AUDIO_FORMATS = (".mp3", ".wav", ".m4a", ".ogg")


class ProcessingProgress(BaseModel):
    stage: str
    progress: float
    message: Optional[str] = None


class ProcessingOptions(BaseModel):
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
    chunk_size: int = Field(default=1024 * 1024, description="Chunk size for processing large files")
    max_retries: int = Field(default=3, description="Maximum number of retries for failed API calls")
    timeout: int = Field(default=300, description="Timeout in seconds")


class TranscriptionInput(BaseModel):
    """
    Model for input data required for transcription.
    """

    audio_file: str = Field(..., description="Path to the audio file or YouTube URL to be transcribed.")

    @field_validator("audio_file")
    @classmethod
    def validate_audio_file(cls, v):
        if not (v.lower().endswith(SUPPORTED_AUDIO_FORMATS) or v.startswith("http")):
            raise ValueError(f"audio_file must be a path to one of {SUPPORTED_AUDIO_FORMATS} file or a YouTube URL.")
        return v


class TranscriptionOutput(BaseModel):
    """
    Model for the output data after transcription.
    """

    transcription: str = Field(..., description="The transcribed text from the audio source.")


class SummarizeInput(BaseModel):
    audio_file: str = Field(..., description="Path to the audio file or YouTube URL to be summarized.")

    @field_validator("audio_file")
    @classmethod
    def validate_audio_file(cls, v):
        if not (v.lower().endswith(SUPPORTED_AUDIO_FORMATS) or v.startswith("http")):
            raise ValueError(f"audio_file must be a path to one of {SUPPORTED_AUDIO_FORMATS} file or a YouTube URL.")
        return v


class SummarizeOutput(BaseModel):
    summary: str = Field(..., description="The summarized text from the audio source.")


class ExtractInput(BaseModel):
    audio_file: str = Field(..., description="Path to the audio file or YouTube URL for extraction.")
    prompt: str = Field(..., description="Custom prompt specifying what information to extract.")

    @field_validator("audio_file")
    @classmethod
    def validate_audio_file(cls, v):
        if not (v.lower().endswith(SUPPORTED_AUDIO_FORMATS) or v.startswith("http")):
            raise ValueError(f"audio_file must be a path to one of {SUPPORTED_AUDIO_FORMATS} file or a YouTube URL.")
        return v

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("prompt cannot be empty.")
        return v


class ExtractOutput(BaseModel):
    extraction: str = Field(..., description="The extracted information from the audio source.")
