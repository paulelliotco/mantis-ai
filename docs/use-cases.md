# Common Use Cases

Real-world problems Mantis solves.

## Content Creation

### Transcribing Podcasts
```python
import mantis

# Get a clean transcript of your podcast
transcript = mantis.transcribe("podcast-episode.mp3")

# Generate a summary for show notes
summary = mantis.summarize("podcast-episode.mp3")
```

### YouTube Video Analysis
```python
# Extract key points from a video
points = mantis.extract(
    "https://youtube.com/watch?v=example",
    "List the main arguments and supporting evidence"
)
```

## Business Applications

### Meeting Summaries
```python
# Get actionable items from meetings
action_items = mantis.extract(
    "meeting-recording.mp3",
    "Extract all action items, assignees, and deadlines"
)
```

### Interview Analysis
```python
# Extract candidate information
candidate_info = mantis.extract(
    "interview.mp3",
    "Extract: technical skills, years of experience, and key achievements"
)
```

## Research & Analysis

### Academic Lectures
```python
# Get detailed notes from lectures
lecture_notes = mantis.summarize("lecture.mp3")
```

### Market Research
```python
# Extract competitive intelligence
market_info = mantis.extract(
    "earnings-call.mp3",
    "Extract: revenue figures, growth metrics, and future projections"
)
```