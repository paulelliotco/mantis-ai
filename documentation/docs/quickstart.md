# Quick Start Guide

This guide gets you up and running with the refreshed Mantis workflow powered by
Google's Gemini 1.5 models. You'll learn how to configure credentials, call the
Python helpers with streaming, and make the most of the CLI.

## Before You Begin

1. Install the package: `pip install mantisai`
2. Obtain either a Gemini API key (Google AI Studio) or set up a Vertex AI
   project with service account credentials.
3. Configure the SDK once at application start:

```python
import mantis

# Option 1: Google AI Studio
mantis.configure(api_key="YOUR_GEMINI_API_KEY")

# Option 2: Vertex AI
mantis.configure(vertex_project="my-gcp-project", vertex_location="us-central1")
```

If you prefer environment variables, set `GEMINI_API_KEY`, `VERTEX_PROJECT`, and
`VERTEX_LOCATION`. The helper will read them automatically.

## Transcribing Audio with Streaming Output

```python
import mantis

mantis.configure(api_key="YOUR_GEMINI_API_KEY")

stream_buffer = []

def on_chunk(text: str) -> None:
    stream_buffer.append(text)
    print(text, end="")

transcript = mantis.transcribe(
    "interview.mp3",
    clean_output=True,
    stream=True,
    stream_callback=on_chunk,
)

print("\nFull transcript:\n", transcript)
```

The `stream` flag triggers Gemini's streaming mode while the callback echoes
chunks as they arrive. Mantis still returns the full transcript when the call
completes.

## Generating Structured Summaries

```python
summary = mantis.summarize(
    "interview.mp3",
    model="gemini-1.5-pro-latest",
    response_schema={
        "type": "object",
        "properties": {
            "overview": {"type": "string"},
            "action_items": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["overview"],
    },
    response_mime_type="application/json",
)

print(summary)
```

Passing a JSON schema plus `response_mime_type` instructs Gemini to emit valid
machine-readable responses. This is ideal for downstream automation and storage.

## Extracting Insights with Safety Settings

```python
decisions = mantis.extract(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "List the major decisions and who owns them",
    structured_output=True,
    safety_settings={
        "HATE": "BLOCK_MEDIUM_AND_ABOVE",
        "HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
    },
)

print(decisions)
```

Safety settings mirror the latest Gemini safety specification, letting you align
responses with organisational policy.

## Command Line Interface

```bash
# Stream a transcript in real time
python -m mantis.cli transcribe interview.mp3 --stream

# Upgrade to gemini-1.5-pro-latest for richer summaries
python -m mantis.cli summarize interview.mp3 --model gemini-1.5-pro-latest

# Request JSON from the extractor
python -m mantis.cli extract interview.mp3 "List action items" --response-mime-type application/json
```

The CLI shares the same streaming implementation and accepts the latest model
identifiers (`gemini-1.5-flash-latest`, `gemini-1.5-pro-latest`).

## Upload Patterns and Large Files

Mantis handles file uploads for you—local paths are read directly and streamed to
Gemini, while YouTube URLs are downloaded to a temporary location. For very large
recordings, consider chunking audio and calling `mantis.transcribe` sequentially
or switching to the pro model, which unlocks longer context windows.

## What Next?

- [Installation](installation.md) – Review environment setup in detail.
- [Core Concepts](concepts.md) – Explore how Mantis orchestrates downloads,
  validation, and Gemini requests.
- [Migration Guide](migration-guide.md) – Move from the legacy `google-generativeai`
  flows to the new SDK usage.
