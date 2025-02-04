import asyncio
from typing import Optional
import google.generativeai as genai
from .models import TranscriptionOutput, SummarizeOutput, ExtractOutput

async def transcribe_async(audio_file: str) -> TranscriptionOutput:
    """Async version of transcribe function"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, transcribe, audio_file)

async def summarize_async(audio_file: str) -> SummarizeOutput:
    """Async version of summarize function"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, summarize, audio_file)

async def extract_async(audio_file: str, prompt: str) -> ExtractOutput:
    """Async version of extract function"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, extract, audio_file, prompt)
