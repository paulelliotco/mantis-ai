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

Mantis AI uses Google's Gemini AI models to process audio. The workflow is:

1. The audio file is read into memory
2. A prompt is created based on the task (transcribe, summarize, or extract)
3. The audio and prompt are sent to the Gemini API
4. The model processes the audio and returns a text response

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
result = mantis.transcribe(audio_file, clean_output=True)
```

Under the hood:
1. The audio file is validated
2. A prompt is created asking the model to transcribe the audio
3. If `clean_output` is True, the prompt includes instructions to remove disfluencies
4. The audio is sent to Gemini AI with the prompt
5. The transcription is returned as a string

### Summarize

The `summarize` function generates a concise summary of the audio:

```python
result = mantis.summarize(audio_file, max_length=None, language="English")
```

Under the hood:
1. The audio file is validated
2. A prompt is created asking the model to summarize the audio
3. If `max_length` is specified, the prompt includes a length constraint
4. The `language` parameter specifies the output language
5. The audio is sent to Gemini AI with the prompt
6. The summary is returned as a string

### Extract

The `extract` function retrieves specific information based on a custom prompt:

```python
result = mantis.extract(audio_file, prompt, structured_output=False)
```

Under the hood:
1. The audio file is validated
2. The user's prompt is combined with the audio
3. If `structured_output` is True, the prompt is enhanced and a JSON schema is supplied via Gemini's
   ``response_schema`` parameter
4. The audio is sent to Gemini AI with the prompt and schema
5. The response is validated against the schema and returned as structured data (with graceful fallbacks when parsing fails)

### Domain-specific schemas

Mantis ships with reusable schemas for common tasks such as summarising speakers, generating action items, and providing a
single ``AudioInsightsSchema`` that combines key signals. You can reuse these schemas via the
``mantis.response_schemas.COMMON_RESPONSE_SCHEMAS`` registry or pass your own Pydantic model / JSON schema using the
``response_schema`` parameter on :func:`mantis.extract`. This allows teams to align the structured output with internal data
contracts while still benefiting from prompt engineering in the ``prompt`` argument.

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
- [Advanced Usage](advanced-usage.md) for more complex scenarios and customization 