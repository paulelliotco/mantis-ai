# Installation Guide

Getting started with Mantis AI is straightforward. This guide covers installing
the package, configuring the refreshed Gemini SDK, and troubleshooting common
issues.

> Developed by [Paul Elliot](mailto:paul@paulelliot.co)

## Prerequisites

- Python 3.9 or higher
- `pip`
- Either:
  - A Gemini API key generated in [Google AI Studio](https://ai.google.dev/)
  - **or** a Google Cloud project with Vertex AI enabled and a service account
    that has permission to call the Gemini API

## Step 1: Install the Package

```bash
pip install mantisai
```

## Step 2: Configure Credentials

Mantis now exposes a `configure` helper that wraps the latest
`google.generativeai` client. Call it once during application startup.

### Option A – Google AI Studio (API key)

```python
import mantis

mantis.configure(api_key="YOUR_GEMINI_API_KEY")
```

You can store the key securely using environment variables:

```bash
export GEMINI_API_KEY="your-api-key"
```

### Option B – Vertex AI (service account)

```python
import mantis

mantis.configure(
    vertex_project="my-gcp-project",
    vertex_location="us-central1",
)
```

Vertex requires Google Cloud authentication. Set the `GOOGLE_APPLICATION_CREDENTIALS`
variable to point at a service account JSON key or run inside a workload that has
sufficient permissions.

If you skip `mantis.configure(...)`, the library attempts to read the same values
from `GEMINI_API_KEY`, `VERTEX_PROJECT`, and `VERTEX_LOCATION` when you make your
first request.

## Step 3: Verify Installation

```python
import mantis

mantis.configure(api_key="YOUR_GEMINI_API_KEY")

print(mantis.__version__)
```

## Optional Dependencies

For YouTube processing, Mantis uses `yt-dlp`, which is installed automatically. If
you run into issues, reinstall it manually:

```bash
pip install yt-dlp
```

## Troubleshooting

### API Key or Credential Errors

Ensure that `mantis.configure` receives the correct values. For Vertex AI, double
check `VERTEX_PROJECT`, `VERTEX_LOCATION`, and your service account permissions.

### Quota or Rate Limit Errors

Google applies per-minute and per-day quota on Gemini. `RESOURCE_EXHAUSTED` and
`429` responses indicate that you should slow down, add exponential backoff, or
request higher limits in the Google Cloud console.

### Long Audio Limits

`gemini-1.5-flash-latest` supports roughly one hour of audio (about 500 MB).
Split longer recordings or switch to `gemini-1.5-pro-latest` for the expanded
context window.

### Regional Constraints

When using Vertex AI, requests must target a region that offers the selected
model. Configure matching values for both `vertex_location` and the model you
intend to call. A mismatch results in `NOT_FOUND` or `PERMISSION_DENIED` errors.

### YouTube Download Issues

`yt_dlp` may occasionally receive HTTP 403 responses. Retry with exponential
backoff, try a different video, or consider the official YouTube Data API for
production workloads.

### Getting Help

- Review the [Migration Guide](migration-guide.md) if you are upgrading from the
  legacy `google-generativeai` flow.
- Check [GitHub Issues](https://github.com/paulelliotco/mantis-ai/issues) for
  similar reports or open a new one.

## Next Steps

Continue with the [Quick Start Guide](quickstart.md) to explore streaming,
response schemas, and safety settings in practice.
