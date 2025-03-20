# Slack Integration

This guide demonstrates how to integrate Mantis AI with Slack to automatically transcribe, summarize, and extract insights from audio files shared in your Slack channels.

## Overview

Integrating Mantis AI with Slack allows your team to:

- Automatically transcribe audio files shared in channels
- Generate summaries of meeting recordings
- Extract action items, decisions, and key points from discussions
- Make audio content searchable and accessible

## Prerequisites

- A Slack workspace with admin permissions
- A Slack app with the necessary permissions
- Python 3.9+ environment
- Mantis AI package installed (`pip install mantisai`)
- Slack API token

## Setup

### 1. Create a Slack App

1. Go to [Slack API](https://api.slack.com/apps) and click "Create New App"
2. Choose "From scratch" and provide a name and workspace
3. Navigate to "OAuth & Permissions" and add the following scopes:
   - `files:read`
   - `files:write`
   - `channels:history`
   - `chat:write`
   - `commands`
4. Install the app to your workspace
5. Copy the "Bot User OAuth Token" for later use

### 2. Set Up Event Subscriptions

1. Navigate to "Event Subscriptions" and enable events
2. Subscribe to the following bot events:
   - `file_shared`
   - `message.channels`
3. Set up a request URL (you'll need a server to handle these events)

## Implementation

### Basic Slack Bot Implementation

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from mantisai import transcribe, summarize, extract
from mantisai.models import ExtractInput, SummarizeInput, TranscriptionInput

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Handle file_shared events
@app.event("file_shared")
def handle_file_shared(event, client):
    # Get file info
    file_info = client.files_info(file=event["file_id"])
    file = file_info["file"]
    
    # Check if it's an audio file
    if file["mimetype"].startswith("audio/"):
        # Download the file
        file_path = download_file(file)
        
        # Process with Mantis AI
        process_audio(file_path, event["channel_id"], client)

def download_file(file):
    # Implementation to download file from Slack
    # ...
    return local_file_path

def process_audio(file_path, channel_id, client):
    # Transcribe the audio
    transcription_result = transcribe(
        TranscriptionInput(audio_path=file_path)
    )
    
    # Summarize the transcription
    summary_result = summarize(
        SummarizeInput(text=transcription_result.text)
    )
    
    # Extract key information
    extraction_result = extract(
        ExtractInput(
            text=transcription_result.text,
            extraction_type="meeting",
        )
    )
    
    # Format and post results to Slack
    post_results_to_slack(
        channel_id, 
        client, 
        transcription_result, 
        summary_result, 
        extraction_result
    )

def post_results_to_slack(channel_id, client, transcription, summary, extraction):
    # Post transcription as a snippet
    client.files_upload(
        channels=channel_id,
        content=transcription.text,
        title="Transcription",
        filetype="text"
    )
    
    # Post summary
    client.chat_postMessage(
        channel=channel_id,
        text=f"*Summary:*\n{summary.summary}"
    )
    
    # Post extracted information
    action_items = "\n".join([f"• {item}" for item in extraction.action_items])
    decisions = "\n".join([f"• {item}" for item in extraction.decisions])
    
    client.chat_postMessage(
        channel=channel_id,
        text=f"*Action Items:*\n{action_items}\n\n*Decisions:*\n{decisions}"
    )

# Start the app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

### Advanced Features

#### Slash Commands

You can add slash commands to trigger Mantis AI processing on demand:

```python
@app.command("/transcribe")
def transcribe_command(ack, command, client):
    ack()
    # Implementation to handle the command
    # ...
```

#### Interactive Components

Add buttons to let users choose what to extract:

```python
@app.action("extract_action_items")
def handle_extract_action_items(ack, body, client):
    ack()
    # Implementation to extract action items
    # ...
```

## Deployment

### Hosting Options

1. **Heroku**: Easy deployment with minimal configuration
2. **AWS Lambda**: Serverless option for cost-effective hosting
3. **Docker**: Containerized deployment for better isolation

### Environment Variables

Set these environment variables in your deployment environment:

```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
GOOGLE_API_KEY=your-gemini-api-key
```

## Best Practices

1. **Error Handling**: Implement robust error handling to manage API rate limits and failures
2. **Caching**: Cache results to avoid redundant processing
3. **User Feedback**: Provide status updates during processing
4. **Privacy**: Implement proper data retention policies
5. **Permissions**: Restrict the bot to specific channels where needed

## Example Use Cases

### Team Meetings

Automatically process recordings of team meetings to generate:
- Complete transcripts for reference
- Meeting summaries for those who couldn't attend
- Action item lists for follow-up

### Customer Calls

Process customer support or sales calls to:
- Extract customer pain points
- Identify product feature requests
- Analyze sentiment and satisfaction

### Interviews

For recruitment or research interviews:
- Generate transcripts for easier review
- Extract key qualifications or insights
- Summarize candidate strengths and weaknesses

## Troubleshooting

### Common Issues

1. **File Size Limits**: Slack has a 1GB file size limit
   - Solution: Implement pre-processing to compress or split large files

2. **API Rate Limits**: Slack and Gemini API have rate limits
   - Solution: Implement exponential backoff and retry logic

3. **Processing Time**: Long audio files take time to process
   - Solution: Implement asynchronous processing and status updates

## Resources

- [Slack API Documentation](https://api.slack.com/docs)
- [Slack Bolt Python Framework](https://slack.dev/bolt-python/concepts)
- [Mantis AI Documentation](https://github.com/paulelliotco/mantis-ai) 