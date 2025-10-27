# Mantis: Audio Processing with Large Language Models

Mantis is a Python package that makes it easy to transcribe audio files, generate summaries, and extract information using large language models. Built with Pydantic for robust data validation, it provides a simple and user-friendly API for processing both local audio files and YouTube content.

[![PyPI version](https://badge.fury.io/py/mantisai.svg)](https://badge.fury.io/py/mantisai)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> Developed by [Paul Elliot](mailto:paul@paulelliot.co)

## Key Features

- **Audio Transcription:** Convert audio files to text with clean output
- **Text Summarization:** Generate concise summaries of your audio content
- **Information Extraction:** Retrieve specific details from audio using custom prompts
- **YouTube Support:** Automatically process YouTube URLs with reliable caching
- **Pydantic Validation:** Ensure robust input/output handling
- **Robust Error Handling:** Comprehensive assertions and error checks throughout the codebase

## Supported Formats

- `.mp3` - MP3 audio files
- `.wav` - WAV audio files
- `.m4a` - M4A audio files
- `.ogg` - OGG audio files
- `.flac` - FLAC lossless audio files
- `.aac` - AAC audio files
- YouTube URLs

## Installation

Install Mantis with pip:

```bash
pip install mantisai
```

### Configure Google AI access

The refreshed SDK relies on the [google-genai](https://pypi.org/project/google-genai/) client and the new Responses API. Provide
credentials via environment variables before running any code:

```bash
export GOOGLE_API_KEY="your-google-ai-studio-or-vertex-api-key"
# Optional: pin a region or endpoint if you are using Vertex AI
export GOOGLE_API_REGION="us-central1"
# or export GOOGLE_API_ENDPOINT="https://your-custom-endpoint"
```

`GOOGLE_API_KEY` is preferred, but `GEMINI_API_KEY` and `GENAI_API_KEY` remain supported for backwards compatibility.

## Quick Start

### Basic Usage

```python
import mantis

# Transcribe a local audio file
print(mantis.transcribe("path/to/local/audio.mp3"))

# Summarize a local audio file
print(mantis.summarize("path/to/local/audio.mp3"))

# Extract information using a custom prompt
print(mantis.extract("path/to/local/audio.mp3", "Extract key details"))
```

### YouTube Support

Process YouTube content with the same API:

```python
# Transcribe a YouTube video
transcript = mantis.transcribe("https://www.youtube.com/watch?v=example")

# Summarize a YouTube video
summary = mantis.summarize("https://www.youtube.com/watch?v=example")

# Extract information from a YouTube video
info = mantis.extract("https://www.youtube.com/watch?v=example", "Identify the key themes")
```

### Command Line Interface

Mantis also provides a convenient CLI:

```bash
# Transcribe an audio file
python -m mantis.cli transcribe "path/to/audio.mp3"

# Summarize a YouTube video
python -m mantis.cli summarize "https://www.youtube.com/watch?v=example"

# Extract information with a custom prompt
python -m mantis.cli extract "path/to/audio.mp3" "Identify the key themes"
```

## Usage Notes

- **Unified Interface:** Whether you're passing a `.mp3` file or a YouTube URL, the functions work the same way
- **Clean Transcriptions:** By default, transcriptions remove disfluencies and speech artifacts
- **Custom Prompts:** For extraction, you can provide custom prompts to guide the information retrieval
- **API Key:** Set `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) in your environment before running the SDK
- **Default Models:** Transcription and summarization use `gemini-1.5-flash-latest`; extraction defaults to `gemini-1.5-pro-latest`
- **Silent Operation:** Logging is disabled by default for clean output. Enable it only when needed for debugging.

```python
import mantis

# Enable informational logging when needed
mantis.enable_verbose_logging()

# Enable detailed debug logging for troubleshooting
mantis.enable_debug_logging()

# Enable only warnings and errors
mantis.enable_warning_logging()
```

### Structured extraction and response schemas

When you call `mantis.extract(..., structured_output=True)` the SDK now instructs Gemini to follow a structured JSON schema and
validates the response before returning it to you. This yields reliable summaries, key points, entities, and action items that
can be consumed programmatically. If the model ever produces malformed JSON, Mantis gracefully falls back to the raw text so
your application keeps running.

### File uploads and caching

The new pipeline mirrors Google's recommendations by uploading audio via `client.files.upload`, detecting MIME types
automatically, and caching uploads for repeated prompts. Progress callbacks now include distinct stages for YouTube downloads,
file uploads, and model execution to keep end users informed.

## YouTube Download Issues

When working with YouTube URLs, you may occasionally encounter HTTP 403 Forbidden errors:

```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

This happens because YouTube implements anti-scraping measures that can temporarily block automated downloads. If you encounter these errors:

1. **Retry the request** - YouTube's restrictions are often temporary and may succeed on subsequent attempts
2. **Add delay between attempts** - Implement your own retry logic with increasing delays
3. **Try different videos** - Some videos may have stricter access controls than others
4. **Consider YouTube API** - For production applications, consider using YouTube's official API

Mantis uses the `yt_dlp` library which implements various workarounds, but YouTube's protective measures are constantly evolving. For critical applications, implement additional error handling around YouTube downloads.

```python
import mantis
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Example of custom retry logic for YouTube downloads
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
def transcribe_with_retry(url):
    return mantis.transcribe(url)

# Use the retry wrapper
try:
    transcript = transcribe_with_retry("https://www.youtube.com/watch?v=example")
    print(transcript)
except Exception as e:
    print(f"Failed after multiple attempts: {e}")
```

## Recent Improvements (v0.2.0)

- **Responses API upgrade:** Migrated from the deprecated `google-generativeai` SDK to the latest `google-genai` client and
  `client.responses.generate` workflow.
- **Modern audio ingestion:** Follow Google's upload guidance with MIME-type detection, resumable uploads, and caching for
  repeat requests.
- **Reliable structured extraction:** Response schemas and JSON validation power predictable audio intelligence outputs.
- **Expanded format support:** Added FLAC and AAC detection alongside improved YouTube progress reporting.

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests: `python -m unittest discover tests`
5. Submit a pull request

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

