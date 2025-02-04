# 5-Minute Quickstart

Let's process your first audio file with Mantis.

## 1. Installation

```bash
pip install mantisai
```

## 2. Set Up Your API Key

```python
import os
os.environ["GEMINI_API_KEY"] = "your-api-key"
```

## 3. Process Your First Audio File

```python
import mantis

# Transcribe an audio file
transcript = mantis.transcribe("path/to/audio.mp3")
print(transcript)

# Or use a YouTube URL
transcript = mantis.transcribe("https://youtube.com/watch?v=example")
print(transcript)
```

That's it! You're ready to process audio with AI.

## What's Next?

- [Common Use Cases](./guide/use-cases.md) - See how others are using Mantis
- [Advanced Features](./guide/advanced-features.md) - Learn about async processing, batch operations, and more
- [API Reference](./api/core.md) - Explore the full API