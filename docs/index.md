# Mantis: Audio Processing with Large Language Models

**Get actionable insights from audio in minutes.**

```python
import mantis

# Get a quick summary of a podcast episode
summary = mantis.summarize("https://example.com/podcast.mp3")
print(summary)

# Extract structured data
from pydantic import BaseModel
class PodcastInfo(BaseModel):
    title: str
    topics: List[str]
    guests: List[str]

info = mantis.extract_structured("podcast.mp3", PodcastInfo)
print(f"Guests: {', '.join(info.guests)}")
```

## Why Mantis?

- **🎯 Immediate Results** - Process audio files or YouTube URLs with just one line of code
- **🔍 Structured Output** - Get clean, validated results using Pydantic models
- **🚀 Production Ready** - Built-in retry logic, error handling, and async support
- **💪 Flexible** - Works with local files and YouTube URLs seamlessly

## Quick Installation

```bash
pip install mantisai
```

## Solve Real Problems

1. **Need to transcribe hours of audio?**
   ```python
   transcript = mantis.transcribe("meeting-recording.mp3")
   ```

2. **Want key points from a YouTube video?**
   ```python
   summary = mantis.summarize("https://youtube.com/watch?v=example")
   ```

3. **Extract specific information?**
   ```python
   info = mantis.extract("interview.mp3", "List all mentioned company names")
   ```

## Next Steps

- [5-Minute Quickstart](./quickstart.md) - Get up and running in minutes
- [Common Use Cases](./guide/use-cases.md) - Real-world examples and solutions
- [API Reference](./api/core.md) - Detailed API documentation
