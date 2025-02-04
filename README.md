# Mantis: Audio Processing with Large Language Models

Mantis is a Python package that makes it easy to transcribe audio files, generate summaries, and extract information using large language models. Built with Pydantic for robust data validation, it provides a simple and user-friendly API for processing both local audio files and YouTube content.

[![PyPI version](https://badge.fury.io/py/mantisai.svg)](https://badge.fury.io/py/mantisai)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Key Features

- **Audio Transcription:** Convert audio files to text
- **Text Summarization:** Generate concise summaries of your audio content
- **Information Extraction:** Retrieve specific details from audio using custom prompts
- **Structured Data:** Extract information in typed, validated formats using Pydantic models
- **YouTube Support:** Automatically process YouTube URLs
- **Pydantic Validation:** Ensure robust input/output handling

## Installation

Install Mantis with pip:

```bash
pip install mantisai
```

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

### Structured Data Extraction

Extract typed, validated data using Pydantic models:

```python
from pydantic import BaseModel, Field
from typing import List

class MeetingAnalysis(BaseModel):
    title: str = Field(..., description="Title of the meeting")
    attendees: List[str] = Field(..., description="List of meeting participants")
    action_items: List[str] = Field(..., description="Action items discussed")
    key_decisions: List[str] = Field(..., description="Key decisions made")
    duration: float = Field(..., description="Meeting duration in minutes")

# Extract structured data from audio
meeting = mantis.extract_structured("meeting.mp3", MeetingAnalysis)

print(f"Meeting: {meeting.title}")
print(f"Duration: {meeting.duration} minutes")
print("\nAction Items:")
for item in meeting.action_items:
    print(f"- {item}")
```

### YouTube Support

Process YouTube content with the same API:

```python
# Transcribe a YouTube video
transcript = mantis.transcribe("https://www.youtube.com/watch?v=example")

# Extract structured data from YouTube
class VideoAnalysis(BaseModel):
    title: str
    main_points: List[str]
    timestamps: dict[str, float]
    sentiment: str

analysis = mantis.extract_structured(
    "https://youtube.com/watch?v=example",
    VideoAnalysis
)
```

## Usage Notes

- **Unified Interface:** Whether you're passing a `.mp3` file or a YouTube URL, the functions work the same way
- **Custom Prompts:** For extraction, you can provide custom prompts to guide the information retrieval
- **API Key:** Ensure your Gemini AI API key is set in your environment (or in your code)
- **Default Model:** Mantis uses Gemini 1.5 Flash by default

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


