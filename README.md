# Mantis: Audio Processing with Gemini 1.5

Mantis is a Python package that wraps Google's latest Gemini 1.5 models to make it
simple to transcribe audio files, generate summaries, and extract structured
insights from long-form recordings. Built with Pydantic for robust validation,
Mantis provides a streamlined API that works with both Google AI Studio API keys
and Vertex AI enterprise deployments.

[![PyPI version](https://badge.fury.io/py/mantisai.svg)](https://badge.fury.io/py/mantisai)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> Developed by [Paul Elliot](mailto:paul@paulelliot.co)

## Key Features

- **Latest Gemini Coverage:** Defaults to `gemini-1.5-flash-latest` with easy opt-in
  to `gemini-1.5-pro-latest` for higher quality summaries and extra-long context.
- **Audio Transcription:** Convert local files or YouTube audio into readable text.
- **Response Schemas:** Request structured JSON directly from Gemini for downstream
  automation and analytics.
- **Safety Controls:** Pass Gemini safety settings through every high-level helper
  to align with your content policies.
- **Optional Streaming:** Watch transcripts or summaries stream into the CLI as the
  model responds.
- **Pydantic Validation:** Input/output models guard against malformed requests.
- **Robust Error Handling:** Clear exceptions and retry logic across downloads and
  inference.

## Supported Formats

- `.mp3` - MP3 audio files
- `.wav` - WAV audio files
- `.m4a` - M4A audio files
- `.ogg` - OGG audio files
- `.flac` - FLAC lossless audio files
- `.aac` - AAC audio files
- YouTube URLs

## Installation

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

Mantis now exposes a `configure` helper so you can initialize the new
`google.generativeai` SDK exactly once and share it across the package.

### Google AI Studio (API key)

```python
import mantis

mantis.configure(api_key="YOUR_GEMINI_API_KEY")
```

You can also set the `GEMINI_API_KEY` environment variable. The helper will fall
back to it automatically.

### Vertex AI (service account)

```python
import mantis

mantis.configure(
    vertex_project="my-gcp-project",
    vertex_location="us-central1",
)
```

Make sure your service account credentials are available to the runtime—either by
setting `GOOGLE_APPLICATION_CREDENTIALS` or running on GCP with the appropriate
workload identity.

> If you do not call `mantis.configure(...)`, the package attempts to read the
> same values from environment variables at runtime.

## Quick Start

### Python API

```python
import os
import mantis

mantis.configure(api_key=os.environ["GEMINI_API_KEY"])

# Transcribe a local audio file with streaming output
transcript = mantis.transcribe(
    "path/to/local/audio.mp3",
    clean_output=True,
    stream=True,
    stream_callback=lambda chunk: print(chunk, end=""),
)

print("\nFull transcript:\n", transcript)

# Summarize the same file with the pro model and a JSON schema
summary = mantis.summarize(
    "path/to/local/audio.mp3",
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

# Extract structured insights from a YouTube video
action_items = mantis.extract(
    "https://www.youtube.com/watch?v=example",
    "List decisions and owners",
    structured_output=True,
    safety_settings={"HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE"},
)

print(action_items)
```

### Command Line Interface

Mantis ships with a CLI that mirrors the Python helpers and now supports
streaming plus on-the-fly model selection.

```bash
# Transcribe with streaming output using gemini-1.5-flash-latest
python -m mantis.cli transcribe path/to/audio.mp3 --stream

# Summarize with the pro model
python -m mantis.cli summarize path/to/audio.mp3 --model gemini-1.5-pro-latest

# Extract JSON with a custom MIME type
python -m mantis.cli extract path/to/audio.mp3 "List action items" --response-mime-type application/json
```

## Advanced Usage Highlights

- **Response Schemas:** Pass JSON schema dictionaries plus `response_mime_type`
  to `summarize` or `extract` for machine-readable output.
- **Safety Settings:** Supply Gemini safety configuration dictionaries to any
  helper via the `safety_settings` parameter.
- **Streaming:** Toggle the `stream` flag and provide a `stream_callback` to react
  to incremental updates in real time (available in the Python API and CLI).

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

mantis.enable_verbose_logging()
# or
mantis.enable_debug_logging()
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

### Gemini Quotas and Rate Limits

Google enforces request-per-minute and tokens-per-day quotas. If you see errors
like `429 RESOURCE_EXHAUSTED`, reduce concurrency, retry with exponential
backoff, or request higher quota in the Google Cloud console.

### Long Audio Processing

`gemini-1.5-flash-latest` currently supports uploads up to 1 hour (approx. 500 MB).
Split longer recordings before calling Mantis or upgrade to the pro model for a
larger context window.

### Regional Availability

Vertex AI routes requests through the region provided during configuration. Ensure
that the model is available in your chosen region (for example, `us-central1` or
`europe-west4`). Mismatched regions return `NOT_FOUND` errors.

### YouTube Download Issues

You may occasionally encounter HTTP 403 errors when downloading YouTube audio:

```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

Retry the request, add exponential backoff, or switch to a different video. For
production workloads consider the official YouTube Data API.

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

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Mantis is released under the Apache 2.0 License. See the [LICENSE](LICENSE)
file for more information.
