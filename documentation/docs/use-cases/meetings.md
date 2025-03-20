# Meeting Transcription and Analysis

One of the most common applications for Mantis AI is processing meeting recordings. This use case demonstrates how to automatically transcribe meetings, generate summaries, and extract action items, decisions, and other key information.

## The Problem

Meetings are essential for collaboration, but they often result in:

- Time spent manually taking and distributing notes
- Important details being missed or forgotten
- Action items that aren't clearly tracked
- Difficulty finding specific information later

Mantis AI solves these problems by automatically processing meeting recordings to extract valuable information in a fraction of the time it would take manually.

## Solution Overview

This solution will:

1. Transcribe meeting recordings
2. Generate concise summaries
3. Extract action items, decisions, and key points
4. Save the results in a structured format

## Step-by-Step Implementation

### Basic Meeting Transcription

Start with a simple transcription of your meeting recording:

```python
import mantis

# Transcribe a meeting recording
meeting_transcript = mantis.transcribe("meeting_2023-03-12.mp3", clean_output=True)

# Print the transcript
print(meeting_transcript)
```

### Adding Meeting Summarization

Next, generate a concise summary of the meeting:

```python
# Summarize the meeting
meeting_summary = mantis.summarize("meeting_2023-03-12.mp3")

print("Meeting Summary:")
print(meeting_summary)
```

### Extracting Action Items

Extract action items and who's responsible for them:

```python
# Extract action items
action_items = mantis.extract(
    "meeting_2023-03-12.mp3",
    "List all action items mentioned in this meeting. For each action item, include: "
    "1. The specific task to be done "
    "2. Who is responsible for it "
    "3. Any mentioned deadline "
    "Format as a numbered list."
)

print("Action Items:")
print(action_items)
```

### Extracting Decisions

Extract key decisions made during the meeting:

```python
# Extract decisions
decisions = mantis.extract(
    "meeting_2023-03-12.mp3",
    "List all decisions and agreements made during this meeting. "
    "For each decision, include: "
    "1. What was decided "
    "2. Any context or reasoning mentioned "
    "Format as a numbered list."
)

print("Decisions:")
print(decisions)
```

### Complete Meeting Analysis Script

Here's a complete script that processes a meeting recording and saves the results to a file:

```python
import mantis
import os
from datetime import datetime

def process_meeting(audio_file, output_dir="meeting_notes"):
    """Process a meeting recording and save the results."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get meeting date from filename or use current date
    try:
        # Assuming filename format: meeting_YYYY-MM-DD.mp3
        meeting_date = os.path.basename(audio_file).replace("meeting_", "").replace(".mp3", "")
        # Validate date format
        datetime.strptime(meeting_date, "%Y-%m-%d")
    except (ValueError, IndexError):
        # Use current date if filename doesn't contain a valid date
        meeting_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Processing meeting from {meeting_date}...")
    
    # Transcribe the meeting
    print("Transcribing...")
    transcript = mantis.transcribe(audio_file, clean_output=True)
    
    # Summarize the meeting
    print("Summarizing...")
    summary = mantis.summarize(audio_file)
    
    # Extract action items
    print("Extracting action items...")
    action_items = mantis.extract(
        audio_file,
        "List all action items mentioned in this meeting. For each action item, include: "
        "1. The specific task to be done "
        "2. Who is responsible for it "
        "3. Any mentioned deadline "
        "Format as a numbered list."
    )
    
    # Extract decisions
    print("Extracting decisions...")
    decisions = mantis.extract(
        audio_file,
        "List all decisions and agreements made during this meeting. "
        "For each decision, include: "
        "1. What was decided "
        "2. Any context or reasoning mentioned "
        "Format as a numbered list."
    )
    
    # Extract key points
    print("Extracting key points...")
    key_points = mantis.extract(
        audio_file,
        "List the 5-7 most important points discussed in this meeting. "
        "Format as a bulleted list."
    )
    
    # Save results
    output_file = os.path.join(output_dir, f"meeting_notes_{meeting_date}.md")
    with open(output_file, "w") as f:
        f.write(f"# Meeting Notes: {meeting_date}\n\n")
        
        f.write("## Summary\n\n")
        f.write(summary)
        f.write("\n\n")
        
        f.write("## Key Points\n\n")
        f.write(key_points)
        f.write("\n\n")
        
        f.write("## Action Items\n\n")
        f.write(action_items)
        f.write("\n\n")
        
        f.write("## Decisions\n\n")
        f.write(decisions)
        f.write("\n\n")
        
        f.write("## Full Transcript\n\n")
        f.write("```\n")
        f.write(transcript)
        f.write("\n```\n")
    
    print(f"Meeting notes saved to {output_file}")
    return output_file

# Example usage
if __name__ == "__main__":
    process_meeting("meeting_2023-03-12.mp3")
```

## Processing Multiple Meetings

To process multiple meeting recordings at once:

```python
import mantis
import os
import glob

def process_all_meetings(meetings_dir, output_dir="meeting_notes"):
    """Process all meeting recordings in a directory."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all meeting recordings
    meeting_files = glob.glob(os.path.join(meetings_dir, "*.mp3"))
    
    print(f"Found {len(meeting_files)} meeting recordings")
    
    # Process each meeting
    for audio_file in meeting_files:
        try:
            process_meeting(audio_file, output_dir)
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
    
    print("All meetings processed")

# Example usage
process_all_meetings("meetings/")
```

## Customization Tips

### Tailoring Extraction Prompts

You can customize the extraction prompts to fit your specific meeting format and information needs:

- For technical meetings, add prompts to extract technical decisions or architecture changes
- For project status meetings, focus on progress updates and blockers
- For sales meetings, extract customer requirements and follow-up items

### Improving Extraction Quality

To get better extraction results:

- Be specific about the format you want (numbered lists, bullet points, etc.)
- Provide examples in your prompt if the format is complex
- Break down complex extractions into multiple focused prompts

### Handling Long Meetings

For meetings longer than 30 minutes:

- Consider implementing progress tracking to provide feedback during processing
- Use more specific extraction prompts to focus on the most important information
- Process the meeting in segments if needed

## Common Challenges and Solutions

### Challenge: Meeting Audio Quality

Poor audio quality can affect transcription accuracy.

**Solutions:**
- Use a good quality microphone for recording meetings
- Position microphones closer to speakers
- Consider using a meeting recording tool with audio enhancement features

### Challenge: Multiple Speakers

Meetings with multiple speakers can be challenging to transcribe accurately.

**Solutions:**
- In your extraction prompts, ask for speaker identification when relevant
- Use clean_output=True to remove disfluencies and make the transcript more readable
- For critical meetings, consider using a dedicated meeting recording solution with speaker diarization

### Challenge: Technical Terminology

Technical meetings often include specialized terminology that may not be transcribed correctly.

**Solutions:**
- In extraction prompts, include context about the technical domain
- For recurring meetings on the same topic, create custom extraction prompts that include common terminology

## Next Steps

- Explore [Customer Service Analysis](customer-service.md) for processing customer calls
- Learn about [Podcast Processing](podcasts.md) for content creation
- Check out [Interview Analysis](interviews.md) for research applications 