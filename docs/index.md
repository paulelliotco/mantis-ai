# Mantis AI Documentation

**Transform audio into actionable insights with just a few lines of code.**

Mantis AI is a Python library that makes it easy to transcribe audio, generate summaries, and extract specific information using large language models. Whether you're working with local audio files or YouTube content, Mantis provides a simple, consistent API to unlock the value in your audio data.

> Developed by [Paul Elliot](mailto:paul@paulelliot.co)

## Why Mantis?

- **Solve Real Problems**: Process hours of audio content in minutes
- **Simple API**: Just 3 core functions to learn
- **Flexible Input**: Works with local audio files and YouTube URLs
- **Clean Results**: Get polished transcriptions without speech artifacts
- **Custom Extraction**: Ask specific questions about your audio content

## Quick Example

```python
import mantis

# Transcribe an audio file
transcript = mantis.transcribe("interview.mp3")
print(transcript)

# Generate a concise summary
summary = mantis.summarize("interview.mp3")
print(summary)

# Extract specific information
key_points = mantis.extract("interview.mp3", "What are the main arguments presented?")
print(key_points)
```

## Getting Started

- [Installation](installation.md): Get up and running in under 2 minutes
- [Quick Start Guide](quickstart.md): Learn the basics with practical examples
- [Core Concepts](concepts.md): Understand how Mantis works
- [API Reference](api-reference.md): Detailed documentation of all functions and parameters

## Common Use Cases

- [Meeting Transcription](use-cases/meetings.md): Capture and summarize team discussions
- [Content Creation](use-cases/content.md): Generate transcripts and summaries for videos
- [Research](use-cases/research.md): Extract insights from interviews and focus groups
- [Education](use-cases/education.md): Process lecture recordings and educational content 