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
- **API Key:** Ensure your Gemini AI API key is set in your environment (or in your code)
- **Default Model:** Mantis uses Gemini 1.5 Flash by default
- **Silent Operation:** Logging is disabled by default for clean output. Enable it only when needed for debugging.

```python
# By default, logging is disabled for clean output

# Enable informational logging when needed
import mantis
mantis.enable_verbose_logging()

# Enable detailed debug logging for troubleshooting
mantis.enable_debug_logging()

# Enable only warnings and errors
mantis.enable_warning_logging()
```

## Recent Improvements (v0.1.17)

- **Enhanced YouTube Processing:** Fixed caching issues with YouTube downloads
- **Improved Robustness:** Added comprehensive assertions throughout the codebase
- **Better Error Handling:** More reliable cleanup of temporary files
- **Simplified Interface:** Streamlined CLI with focus on core functionalities
- **Silent Operation:** Disabled all logging by default for clean, results-only output

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

