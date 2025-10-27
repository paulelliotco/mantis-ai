# Core Concepts

This document explains the key concepts behind Mantis AI and how it works under the hood. Understanding these concepts will help you get the most out of the library.

## Architecture Overview

Mantis AI is built around a simple, consistent workflow:

1. **Input Processing**: Audio files or YouTube URLs are validated and prepared
2. **Audio Processing**: Audio is sent to Google's Gemini AI model
3. **Result Formatting**: The model's response is processed and returned in a clean format

![Mantis Architecture](images/architecture.png)

## Key Components

### Audio Source Handling

Mantis AI supports two types of audio sources:

- **Local Audio Files**: Direct processing of MP3, WAV, M4A, and OGG files
- **YouTube URLs**: Automatic downloading and processing of YouTube audio

When you provide a YouTube URL, Mantis:
1. Validates the URL format
2. Downloads the audio using yt-dlp
3. Saves it to a temporary file
4. Processes it like a local audio file
5. Cleans up the temporary file when done

### Gemini AI Integration

Mantis AI configures the refreshed Gemini SDK once via `mantis.configure(...)`
and reuses it for every request. The workflow now includes:

1. Selecting a model (`gemini-1.5-flash-latest` by default, with easy opt-in to
   `gemini-1.5-pro-latest`).
2. Reading the audio input (local path or downloaded YouTube file) and streaming
   it directly to Gemini.
3. Attaching optional response schemas, safety settings, and streaming
   callbacks.
4. Receiving either a streaming iterator or a full response payload, which is
   then converted into Pydantic models or plain text.

### Clean Output Processing

By default, transcription removes disfluencies and speech artifacts:

- Filler words ("um", "uh", "like")
- False starts and repetitions
- Other speech artifacts

This results in clean, readable text that preserves the original meaning.

## Core Functions

### Transcribe

The `transcribe` function converts audio to text:

```python
result = mantis.transcribe(
    audio_file,
    clean_output=True,
    stream=True,
    stream_callback=lambda chunk: print(chunk, end=""),
)
```

Under the hood:
1. The audio file is validated.
2. Gemini is configured if it has not been initialised yet.
3. A transcription prompt is assembled (optionally removing disfluencies).
4. The audio stream and prompt are sent to Gemini with streaming enabled.
5. The helper aggregates partial responses, returning a clean string or
   `TranscriptionOutput` model.

### Summarize

The `summarize` function generates a concise summary of the audio:

```python
result = mantis.summarize(
    audio_file,
    model="gemini-1.5-pro-latest",
    response_schema={
        "type": "object",
        "properties": {"overview": {"type": "string"}},
        "required": ["overview"],
    },
    response_mime_type="application/json",
)
```

Under the hood:
1. Input validation occurs as before.
2. Response schemas and MIME types are attached to the Gemini request if
   provided.
3. The pro model is selected for higher-quality summarisation.
4. Gemini returns JSON that is parsed into the `SummarizeOutput` model.

### Extract

The `extract` function retrieves specific information based on a custom prompt:

```python
result = mantis.extract(
    audio_file,
    prompt,
    structured_output=True,
    safety_settings={"HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE"},
    stream=True,
)
```

Under the hood:
1. Audio and prompts are validated and prepared.
2. Optional structured-output hints and safety settings are passed through.
3. Streaming mode can surface incremental reasoning traces, while the helper
   still returns aggregated results at completion.

## Error Handling

Mantis AI includes comprehensive error handling:

- **Input Validation**: Ensures audio files and parameters are valid
- **Network Errors**: Handles API connection issues
- **Processing Errors**: Manages issues during audio processing
- **Cleanup**: Ensures temporary files are removed even if errors occur

All errors are wrapped in specific exception types that inherit from `MantisError`, making it easy to catch and handle different error scenarios.

## Logging

Mantis AI uses a silent-by-default approach to logging:

- By default, logging is disabled for clean output
- `enable_verbose_logging()`: Enables informational logging
- `enable_debug_logging()`: Enables detailed debug logging
- `enable_warning_logging()`: Enables only warnings and errors

This allows you to control the verbosity of the library based on your needs.

## Next Steps

Now that you understand how Mantis AI works, check out:

- [API Reference](api-reference.md) for detailed documentation of all functions and parameters
- [Migration Guide](migration-guide.md) to update existing projects to the latest SDK