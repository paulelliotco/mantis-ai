# Mantis: Audio Processing with Large Language Models

Mantis is a Python package that makes it easy to transcribe audio files, generate summaries, and extract information using Large Language Models. Built with Pydantic for robust data validation, it provides a simple and user-friendly API for processing both local audio files and YouTube content.

[![PyPI version](https://badge.fury.io/py/mantisai.svg)](https://badge.fury.io/py/mantisai)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Key Features

* **Audio Transcription**: Convert audio files to text
* **Text Summarization**: Generate concise summaries of transcribed content
* **Information Extraction**: Extract specific information from audio content
* **YouTube Support**: Process audio directly from YouTube URLs
* **Pydantic Validation**: Ensure robust data handling with Pydantic models
* **Easy Integration**: Simple API that works with both local files and YouTube URLs

## Installation

Install Mantis with pip:

```bash
pip install mantisai
```

## Quick Start

Here's a simple example of how to use Mantis:

```python
import mantis
import os

# Configure your API key
os.environ["GEMINI_API_KEY"] = "your-api-key"

# Transcribe an audio file
transcription = mantis.transcribe("sample.mp3")
print(transcription.transcription)

# Generate a summary
summary = mantis.summarize("sample.mp3")
print(summary.summary)

# Extract specific information
extraction = mantis.extract("sample.mp3", "Extract key points about technology mentioned")
print(extraction.extraction)
```

## Working with YouTube

Mantis can also process YouTube videos directly:

```python
# Transcribe from YouTube URL
transcription = mantis.transcribe("https://www.youtube.com/watch?v=example")
print(transcription.transcription)

# Summarize YouTube content
summary = mantis.summarize("https://www.youtube.com/watch?v=example")
print(summary.summary)
```

## Features in Detail

### Transcription

```python
import mantis

# Transcribe local file
result = mantis.transcribe("local_audio.mp3")
print(result.transcription)

# Transcribe YouTube video
result = mantis.transcribe("https://www.youtube.com/watch?v=example")
print(result.transcription)
```

### Summarization

```python
import mantis

# Summarize local file
result = mantis.summarize("local_audio.mp3")
print(result.summary)

# Summarize YouTube video
result = mantis.summarize("https://www.youtube.com/watch?v=example")
print(result.summary)
```

### Information Extraction

```python
import mantis

# Extract information with a custom prompt
result = mantis.extract("local_audio.mp3", "List all mentioned dates and events")
print(result.extraction)
```

## Configuration

Set your Gemini AI API key in your environment:

```bash
export GEMINI_API_KEY="your-api-key"
```

Or in your Python code:

```python
import os
os.environ["GEMINI_API_KEY"] = "your-api-key"
```

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests: `python -m unittest discover tests`
5. Submit a pull request

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.


