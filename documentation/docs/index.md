# Mantis AI Documentation

**Transform audio into actionable insights with the latest Gemini 1.5 models.**

Mantis AI is a Python library that wraps Google's refreshed Gemini SDK, giving you
an end-to-end pipeline for transcription, summarisation, and structured
information extraction. The package now exposes explicit configuration hooks for
Google AI Studio (API keys) and Vertex AI projects, plus streaming, response
schema, and safety-setting controls that keep pace with Google's platform.

> Developed by [Paul Elliot](mailto:paul@paulelliot.co)

## Why Mantis?

- **Latest Models**: Defaults to `gemini-1.5-flash-latest` with a single flag to
  switch to `gemini-1.5-pro-latest`.
- **Simple API**: Three top-level functions with optional streaming callbacks.
- **Flexible Input**: Process local audio or YouTube URLs transparently.
- **Structured Output**: Response schemas turn Gemini replies into actionable JSON.
- **Policy-Aware**: Pass through Gemini safety settings without leaving Python.

## Quick Example

```python
import os
import mantis

mantis.configure(api_key=os.environ["GEMINI_API_KEY"])

transcript = mantis.transcribe(
    "interview.mp3",
    clean_output=True,
    stream=True,
    stream_callback=lambda chunk: print(chunk, end=""),
)

summary = mantis.summarize(
    "interview.mp3",
    model="gemini-1.5-pro-latest",
    response_schema={
        "type": "object",
        "properties": {
            "overview": {"type": "string"},
            "next_steps": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["overview"],
    },
    response_mime_type="application/json",
)

actions = mantis.extract(
    "interview.mp3",
    "List the main decisions and owners",
    structured_output=True,
    safety_settings={"HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE"},
)
```

## Getting Started

- [Installation](installation.md): Get up and running in under 2 minutes
- [Quick Start Guide](quickstart.md): Learn the basics with practical examples
- [Core Concepts](concepts.md): Understand how Mantis works
- [API Reference](api-reference.md): Detailed documentation of all functions and parameters
- [Migration Guide](migration-guide.md): Move from legacy Google Generative AI flows to the latest SDK

## Common Use Cases

- [Meeting Transcription](use-cases/meetings.md): Capture and summarize team discussions
- [Content Creation](use-cases/content.md): Generate transcripts and summaries for videos
- [Research](use-cases/research.md): Extract insights from interviews and focus groups
- [Education](use-cases/education.md): Process lecture recordings and educational content 