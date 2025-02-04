# Advanced Features

Take Mantis to the next level.

## Structured Data Extraction

Extract data in typed, validated formats using Pydantic models:

```python
from pydantic import BaseModel
from typing import List

class Speaker(BaseModel):
    name: str
    speaking_time: float
    main_points: List[str]

# Extract structured data
speakers = mantis.extract_structured("meeting.mp3", Speaker)
for speaker in speakers:
    print(f"{speaker.name}: {len(speaker.main_points)} points")
```

## Async Processing

Process multiple files concurrently:

```python
import asyncio
from mantis.async_api import transcribe_async

async def process_files(files):
    tasks = [transcribe_async(f) for f in files]
    results = await asyncio.gather(*tasks)
    return results

# Use it
files = ["file1.mp3", "file2.mp3", "file3.mp3"]
results = asyncio.run(process_files(files))
```

## Progress Tracking

Monitor long-running operations:

```python
from mantis.models import ProcessingOptions

def progress_callback(progress):
    print(f"Stage: {progress.stage}, Progress: {progress.progress:.2%}")

options = ProcessingOptions(progress_callback=progress_callback)
result = mantis.transcribe("long-audio.mp3", options=options)
```

## Error Handling

Robust error handling for production use:

```python
from mantis.utils import MantisError, APIError

try:
    result = mantis.transcribe("audio.mp3")
except APIError as e:
    print(f"API Error: {e}")
except MantisError as e:
    print(f"Processing Error: {e}")
```

## API Reference

### Core Functions

- `transcribe(audio_file: str, options: Optional[ProcessingOptions] = None) -> TranscriptionOutput`
- `summarize(audio_file: str, options: Optional[ProcessingOptions] = None) -> SummarizeOutput`
- `extract(audio_file: str, prompt: str, options: Optional[ProcessingOptions] = None) -> ExtractOutput`

### Async Functions

- `transcribe_async(audio_file: str) -> TranscriptionOutput`
- `summarize_async(audio_file: str) -> SummarizeOutput`
- `extract_async(audio_file: str, prompt: str) -> ExtractOutput`

## Performance Optimization

### Batch Processing

For processing multiple files efficiently:

```python
from mantis.models import ProcessingOptions

options = ProcessingOptions(
    chunk_size=2048 * 1024,  # Larger chunks for faster processing
    max_retries=5,           # More retries for reliability
    timeout=600              # Longer timeout for large files
)
```

### Caching

Enable caching to avoid reprocessing the same files:

```python
import mantis
from mantis.utils import setup_cache

# Configure caching
setup_cache(cache_dir="./mantis_cache", max_size_mb=1000)

# Subsequent calls with the same file will use cached results
result = mantis.transcribe("repeated_file.mp3")
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, UploadFile
from mantis.async_api import transcribe_async

app = FastAPI()

@app.post("/transcribe/")
async def transcribe_endpoint(file: UploadFile):
    result = await transcribe_async(file.filename)
    return {"transcription": result.transcription}
```

### Celery Integration

```python
from celery import Celery
import mantis

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def transcribe_task(audio_file: str):
    return mantis.transcribe(audio_file).transcription
```

## Troubleshooting Guide

### Common Issues

1. **API Key Issues**
   ```python
   import os
   os.environ["GEMINI_API_KEY"] = "your-api-key"  # Set before importing mantis
   ```

2. **Memory Management**
   ```python
   # For large files, use streaming
   options = ProcessingOptions(chunk_size=1024 * 1024)
   result = mantis.transcribe("large_file.mp3", options=options)
   ```

3. **Network Issues**
   ```python
   # Increase timeout and retries
   options = ProcessingOptions(
       timeout=600,
       max_retries=5
   )
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
mantis.set_debug(True)
```
