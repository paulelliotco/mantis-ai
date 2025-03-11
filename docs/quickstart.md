# Quick Start Guide

This guide will help you get up and running with Mantis AI quickly. We'll cover the three core functions—transcribe, summarize, and extract—with practical examples that solve real problems.

## Basic Usage

First, import the Mantis library:

```python
import mantis
```

## Transcribing Audio

Transcription converts audio to text, removing speech artifacts like "um" and "uh" by default.

### Transcribe a Local Audio File

```python
# Transcribe a local audio file
transcript = mantis.transcribe("interview.mp3")
print(transcript)
```

### Transcribe a YouTube Video

```python
# Transcribe a YouTube video
youtube_transcript = mantis.transcribe("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(youtube_transcript)
```

## Generating Summaries

Summarization creates a concise overview of the audio content.

### Summarize a Local Audio File

```python
# Summarize a local audio file
summary = mantis.summarize("lecture.mp3")
print(summary)
```

### Summarize a YouTube Video

```python
# Summarize a YouTube video
youtube_summary = mantis.summarize("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(youtube_summary)
```

## Extracting Information

Extraction allows you to ask specific questions about the audio content.

### Extract Information from a Local Audio File

```python
# Extract key points from a meeting recording
key_points = mantis.extract(
    "meeting.mp3", 
    "What are the main action items and who is responsible for each?"
)
print(key_points)
```

### Extract Information from a YouTube Video

```python
# Extract specific information from a YouTube video
analysis = mantis.extract(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "What are the main themes of this song and how do they relate to popular culture?"
)
print(analysis)
```

## Using the Command Line Interface

Mantis AI also provides a command-line interface for quick tasks.

### Transcribe

```bash
python -m mantis.cli transcribe "interview.mp3"
```

### Summarize

```bash
python -m mantis.cli summarize "lecture.mp3"
```

### Extract

```bash
python -m mantis.cli extract "meeting.mp3" "What are the key decisions made in this meeting?"
```

## Real-World Examples

### Example 1: Processing Meeting Recordings

```python
import mantis
import os

# Process all meeting recordings in a directory
meeting_dir = "meetings/"
for filename in os.listdir(meeting_dir):
    if filename.endswith(".mp3"):
        file_path = os.path.join(meeting_dir, filename)
        
        # Get the meeting date from the filename (assuming format: meeting_YYYY-MM-DD.mp3)
        meeting_date = filename.replace("meeting_", "").replace(".mp3", "")
        
        print(f"Processing meeting from {meeting_date}...")
        
        # Transcribe the meeting
        transcript = mantis.transcribe(file_path)
        
        # Summarize the meeting
        summary = mantis.summarize(file_path)
        
        # Extract action items
        action_items = mantis.extract(file_path, "List all action items mentioned in this meeting")
        
        # Save results
        with open(f"meeting_notes_{meeting_date}.txt", "w") as f:
            f.write(f"# Meeting Notes: {meeting_date}\n\n")
            f.write("## Summary\n\n")
            f.write(summary)
            f.write("\n\n## Action Items\n\n")
            f.write(action_items)
            f.write("\n\n## Full Transcript\n\n")
            f.write(transcript)
        
        print(f"Saved meeting notes to meeting_notes_{meeting_date}.txt")
```

### Example 2: Analyzing Educational Content

```python
import mantis

# Process an educational lecture
lecture_url = "https://www.youtube.com/watch?v=example_lecture"

# Generate a comprehensive study guide
transcript = mantis.transcribe(lecture_url)
summary = mantis.summarize(lecture_url)
key_concepts = mantis.extract(lecture_url, "What are the key concepts explained in this lecture?")
examples = mantis.extract(lecture_url, "List all examples mentioned and explain their significance")
questions = mantis.extract(lecture_url, "Generate 5 quiz questions with answers based on this lecture")

# Create a study guide
study_guide = f"""
# Lecture Study Guide

## Summary
{summary}

## Key Concepts
{key_concepts}

## Examples
{examples}

## Practice Questions
{questions}
"""

print(study_guide)
```

## Next Steps

Now that you're familiar with the basics, check out:

- [Core Concepts](concepts.md) to understand how Mantis works
- [API Reference](api-reference.md) for detailed documentation
- [Use Cases](use-cases/index.md) for more examples 