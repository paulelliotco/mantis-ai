from pydantic import BaseModel, FilePath, Field, validator
from typing import Optional
import re
import os

class TranscriptionInput(BaseModel):
    """
    Model for input data required for transcription.
    """
    audio_file: str = Field(..., description="Path to the MP3 file or YouTube URL to be transcribed.")

    @validator('audio_file')
    def validate_audio_file(cls, v):
        if not (v.endswith('.mp3') or v.startswith('http')):
            raise ValueError('audio_file must be a path to an MP3 file or a YouTube URL.')
        return v

class TranscriptionOutput(BaseModel):
    """
    Model for the output data after transcription.
    """
    transcription: str = Field(..., description="The transcribed text from the audio source.")

class SummarizeInput(BaseModel):
    audio_file: str = Field(..., description="Path to the audio file or YouTube URL to be summarized.")

    @validator('audio_file')
    def validate_audio_file(cls, v):
        if not (v.endswith('.mp3') or v.startswith('http')):
            raise ValueError('audio_file must be a path to an MP3 file or a YouTube URL.')
        return v

class SummarizeOutput(BaseModel):
    summary: str = Field(..., description="The summarized text from the audio source.")

class ExtractInput(BaseModel):
    audio_file: str = Field(..., description="Path to the audio file or YouTube URL for extraction.")
    prompt: str = Field(..., description="Custom prompt specifying what information to extract.")

    @validator('audio_file')
    def validate_audio_file(cls, v):
        if not (v.endswith('.mp3') or v.startswith('http')):
            raise ValueError('audio_file must be a path to an MP3 file or a YouTube URL.')
        return v

    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('prompt cannot be empty.')
        return v

class ExtractOutput(BaseModel):
    extraction: str = Field(..., description="The extracted information from the audio source.")
