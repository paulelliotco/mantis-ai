# Mantis: Audio Processing with Large Language Models

Mantis is a Python package that makes it easy to transcribe audio files, generate summaries, and extract information using large language models. Built with Pydantic for robust data validation, it provides a simple and user-friendly API for processing both local audio files and YouTube content.

[![PyPI version](https://badge.fury.io/py/mantisai.svg)](https://badge.fury.io/py/mantisai)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Key Features

- **Audio Transcription:** Convert audio files to text
- **Text Summarization:** Generate concise summaries of your audio content
- **Information Extraction:** Retrieve specific details from audio using custom prompts
- **YouTube Support:** Automatically process YouTube URLs
- **Pydantic Validation:** Ensure robust input/output handling

## Supported Formats

- `.mp3` - MP3 audio files
- `.wav` - WAV audio files
- `.m4a` - M4A audio files
- `.ogg` - OGG audio files
- YouTube URLs

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

### YouTube Support

Process YouTube content with the same API:

```python
# Transcribe a YouTube video
transcript = mantis.transcribe("https://www.youtube.com/watch?v=example")
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

