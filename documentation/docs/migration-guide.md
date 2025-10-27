# Migration Guide

This guide helps teams upgrade from the legacy `google-generativeai` workflow to
the refreshed Mantis release that targets Google's new Gemini SDK. Follow the
checklist below to update your configuration, code, and operational runbooks.

## 1. Configure the SDK Once

**Before:** Each module called `genai.configure(api_key="...")` directly, which
made switching credentials or Vertex projects cumbersome.

**After:** Initialise the client once at start-up:

```python
import mantis

mantis.configure(api_key="YOUR_GEMINI_API_KEY")
# or
mantis.configure(vertex_project="my-gcp-project", vertex_location="us-central1")
```

The helper reads environment variables (`GEMINI_API_KEY`, `VERTEX_PROJECT`,
`VERTEX_LOCATION`) when explicit values are not provided.

## 2. Adopt the New Model Identifiers

Gemini now exposes versioned aliases with a `-latest` suffix.

| Task | Old Identifier | New Identifier |
|------|----------------|----------------|
| Default processing | `gemini-1.5-flash` | `gemini-1.5-flash-latest` |
| Premium/long context | `gemini-1.5-pro` | `gemini-1.5-pro-latest` |

Update any hard-coded model names in your code or environment files.

## 3. Use Streaming Where Helpful

Set `stream=True` and provide a callback to surface partial responses.

```python
mantis.transcribe(
    "interview.mp3",
    stream=True,
    stream_callback=lambda chunk: print(chunk, end=""),
)
```

The CLI gains a matching `--stream` flag for quick experiments.

## 4. Leverage Response Schemas and Safety Settings

Structured outputs and granular content policies are now first-class citizens.

```python
summary = mantis.summarize(
    "interview.mp3",
    response_schema={
        "type": "object",
        "properties": {"overview": {"type": "string"}},
        "required": ["overview"],
    },
    response_mime_type="application/json",
    safety_settings={"HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE"},
)
```

These parameters map directly to the latest Gemini features and are supported in
both the Python API and CLI (via `--response-mime-type` for extraction).

## 5. Refresh Operational Playbooks

- **Quota monitoring:** Gemini surfaces `RESOURCE_EXHAUSTED` and `429` errors.
  Add retries with exponential backoff and track usage in Google Cloud.
- **Regional constraints:** Ensure Vertex requests are routed to regions that
  host the desired model (for example, `us-central1` for Flash or Pro).
- **Long audio limits:** Flash handles ~1 hour of audio; use the Pro model or
  chunk long sessions when needed.

## 6. Validate CLI Scripts

Update automation that wraps `python -m mantis.cli` to include the new options:

```bash
python -m mantis.cli transcribe meeting.wav --stream
python -m mantis.cli summarize meeting.wav --model gemini-1.5-pro-latest
```

## 7. Clean Up Deprecated Code Paths

- Remove inline `genai.configure` calls scattered across modules.
- Delete custom streaming wrappers—the built-in callback handles them now.
- Consolidate model constants to use the new `-latest` aliases.

With these steps complete, your project will be aligned with the current Gemini
platform and ready to take advantage of future updates.
