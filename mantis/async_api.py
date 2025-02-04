from typing import Optional
import asyncio
from . import transcribe, summarize, extract


async def transcribe_async(audio_file: str) -> Optional[str]:
    """Asynchronously transcribe audio file."""
    return await asyncio.to_thread(transcribe, audio_file)


async def summarize_async(audio_file: str) -> Optional[str]:
    """Asynchronously summarize audio file."""
    return await asyncio.to_thread(summarize, audio_file)


async def extract_async(audio_file: str, prompt: str) -> Optional[str]:
    """Asynchronously extract information from audio file."""
    return await asyncio.to_thread(extract, audio_file, prompt)
