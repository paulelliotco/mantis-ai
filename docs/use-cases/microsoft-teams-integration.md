# Microsoft Teams Integration

This guide demonstrates how to integrate Mantis AI with Microsoft Teams to automatically process meeting recordings, providing transcriptions, summaries, and extracting key information.

## Overview

Integrating Mantis AI with Microsoft Teams enables:

- Automatic processing of Teams meeting recordings
- Generation of meeting transcripts, summaries, and action items
- Distribution of meeting insights to team channels
- Creation of follow-up tasks based on extracted action items

## Prerequisites

- Microsoft 365 account with admin access
- Microsoft Azure subscription
- Microsoft Graph API access
- Python 3.9+ environment
- Mantis AI package installed (`pip install mantisai`)
- Microsoft Teams app development tools

## Setup

### 1. Register an Azure AD Application

1. Go to the [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Provide a name for your application
5. Set the redirect URI (Web or Single-page application)
6. Click "Register"
7. Note the Application (client) ID and Directory (tenant) ID

### 2. Configure API Permissions

1. In your app registration, go to "API permissions"
2. Click "Add a permission"
3. Select "Microsoft Graph" > "Application permissions"
4. Add the following permissions:
   - `OnlineMeetings.Read.All`
   - `OnlineMeetingRecording.Read.All`
   - `ChannelMessage.Send`
   - `Group.Read.All`
   - `Tasks.ReadWrite`
5. Click "Grant admin consent"

### 3. Create a Client Secret

1. In your app registration, go to "Certificates & secrets"
2. Click "New client secret"
3. Provide a description and select an expiration period
4. Click "Add"
5. Copy the secret value (you won't be able to see it again)

## Implementation

### Basic Teams Integration

```python
import os
import requests
import time
from datetime import datetime, timedelta
from mantisai import transcribe, summarize, extract
from mantisai.models import TranscriptionInput, SummarizeInput, ExtractInput

# Microsoft Graph API configuration
TENANT_ID = os.environ.get("MS_TENANT_ID")
CLIENT_ID = os.environ.get("MS_CLIENT_ID")
CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

# Get access token for Microsoft Graph API
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        'client_id': CLIENT_ID,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

# Get recent meetings with recordings
def get_recent_meetings(access_token):
    # Calculate date for recent meetings (e.g., last 24 hours)
    start_time = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get online meetings
    url = f"{GRAPH_API_ENDPOINT}/users/AllUsers/onlineMeetings?$filter=startDateTime ge {start_time}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    meetings = response.json().get('value', [])
    return meetings

# Get recording for a specific meeting
def get_meeting_recording(meeting_id, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get recording info
    url = f"{GRAPH_API_ENDPOINT}/users/AllUsers/onlineMeetings/{meeting_id}/recordings"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    recordings = response.json().get('value', [])
    if not recordings:
        return None
    
    # Get the download URL for the first recording
    recording_id = recordings[0]['id']
    url = f"{GRAPH_API_ENDPOINT}/users/AllUsers/onlineMeetings/{meeting_id}/recordings/{recording_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    download_url = response.json().get('downloadUrl')
    return download_url

# Download recording file
def download_recording(download_url):
    response = requests.get(download_url)
    response.raise_for_status()
    
    # Save to temporary file
    file_path = f"/tmp/recording_{int(time.time())}.mp4"
    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    return file_path

# Process recording with Mantis AI
def process_recording(file_path):
    # Transcribe the recording
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
            extraction_type="meeting"
        )
    )
    
    return transcription_result, summary_result, extraction_result

# Post results to Teams channel
def post_to_teams_channel(team_id, channel_id, meeting_subject, summary, extraction, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Format action items and decisions
    action_items = "\n\n".join([f"- {item}" for item in extraction.action_items])
    decisions = "\n\n".join([f"- {item}" for item in extraction.decisions])
    
    # Create message content
    message_content = {
        "body": {
            "contentType": "html",
            "content": f"<h1>Meeting Summary: {meeting_subject}</h1><h2>Summary</h2><p>{summary.summary}</p><h2>Action Items</h2><p>{action_items}</p><h2>Decisions</h2><p>{decisions}</p>"
        }
    }
    
    # Post to channel
    url = f"{GRAPH_API_ENDPOINT}/teams/{team_id}/channels/{channel_id}/messages"
    response = requests.post(url, headers=headers, json=message_content)
    response.raise_for_status()
    
    return response.json()

# Create tasks for action items
def create_tasks_from_action_items(team_id, extraction, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get Planner plans for the team
    url = f"{GRAPH_API_ENDPOINT}/groups/{team_id}/planner/plans"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    plans = response.json().get('value', [])
    if not plans:
        return None
    
    plan_id = plans[0]['id']
    
    # Create tasks for each action item
    for item in extraction.action_items:
        # Try to extract assignee from the action item
        assignee = extract_assignee(item)
        
        task = {
            "planId": plan_id,
            "title": item,
            "assignments": {}
        }
        
        if assignee:
            # Would need to map assignee name to user ID
            # This is a simplified example
            pass
        
        # Create task
        url = f"{GRAPH_API_ENDPOINT}/planner/tasks"
        response = requests.post(url, headers=headers, json=task)
        response.raise_for_status()

def extract_assignee(action_item):
    # Implementation to extract assignee from action item text
    # This would use NLP or pattern matching
    # ...
    return None

# Main function to process recent meetings
def process_recent_meetings():
    try:
        # Get access token
        access_token = get_access_token()
        
        # Get recent meetings
        meetings = get_recent_meetings(access_token)
        
        for meeting in meetings:
            meeting_id = meeting['id']
            meeting_subject = meeting.get('subject', 'Untitled Meeting')
            
            # Get recording URL
            download_url = get_meeting_recording(meeting_id, access_token)
            if not download_url:
                continue
            
            # Download recording
            file_path = download_recording(download_url)
            
            try:
                # Process recording
                transcription, summary, extraction = process_recording(file_path)
                
                # Post results to Teams channel
                team_id = meeting.get('teamId')  # This might need to be retrieved differently
                channel_id = "General"  # Default channel, could be configured
                
                if team_id:
                    post_to_teams_channel(
                        team_id, 
                        channel_id, 
                        meeting_subject, 
                        summary, 
                        extraction, 
                        access_token
                    )
                    
                    # Create tasks for action items
                    create_tasks_from_action_items(team_id, extraction, access_token)
            finally:
                # Clean up
                if os.path.exists(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"Error processing meetings: {e}")

if __name__ == "__main__":
    # Run periodically
    process_recent_meetings()
```

### Advanced Features

#### Custom Teams App

Create a dedicated Teams app for better integration:

```python
# This would be part of a Teams bot implementation
from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity, ActivityTypes

# Bot implementation that responds to commands
async def on_message_activity(turn_context: TurnContext):
    text = turn_context.activity.text.lower()
    
    if "process meeting" in text:
        # Extract meeting ID from command
        meeting_id = extract_meeting_id(text)
        
        # Process specific meeting
        await turn_context.send_activity("Processing meeting recording...")
        
        # Implementation to process the meeting
        # ...
```

#### Meeting Insights Dashboard

Create a Power BI dashboard with meeting analytics:

```python
def generate_meeting_analytics(team_id, access_token):
    # Get all processed meetings for the team
    # ...
    
    # Generate analytics data
    analytics_data = {
        "meeting_count": len(meetings),
        "total_duration": sum(m.get('duration', 0) for m in meetings),
        "action_items_count": sum(len(m.get('action_items', [])) for m in meetings),
        "action_items_completed": sum(len([a for a in m.get('action_items', []) if a.get('completed')]) for m in meetings),
        # More analytics...
    }
    
    # Save analytics data for Power BI
    # ...
```

## Deployment

### Hosting Options

1. **Azure Functions**: Serverless option triggered by a timer
2. **Azure App Service**: Web app hosting for continuous processing
3. **Azure Container Instances**: Container-based deployment

### Environment Variables

Set these environment variables in your deployment environment:

```
MS_TENANT_ID=your-tenant-id
MS_CLIENT_ID=your-client-id
MS_CLIENT_SECRET=your-client-secret
GOOGLE_API_KEY=your-gemini-api-key
```

## Best Practices

1. **Incremental Processing**: Track processed meetings to avoid duplicates
2. **Error Handling**: Implement robust error handling for API failures
3. **Rate Limiting**: Respect Microsoft Graph API rate limits
4. **Security**: Store credentials securely using Azure Key Vault
5. **Logging**: Implement comprehensive logging for troubleshooting

## Example Use Cases

### Executive Meetings

Process executive team meetings to:
- Create secure, searchable transcripts
- Distribute key decisions to leadership
- Track strategic initiatives and action items

### Project Status Meetings

Enhance project management by:
- Automatically updating project plans with new action items
- Tracking decisions that impact project scope or timeline
- Creating a searchable history of project discussions

### Training Sessions

Support learning and development by:
- Creating transcripts of training sessions
- Extracting key learning points and resources
- Making training content searchable for future reference

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Solution: Verify app permissions and consent status

2. **Recording Access Issues**:
   - Solution: Ensure the app has proper permissions to access meeting recordings

3. **Teams Message Formatting**:
   - Solution: Test message formatting with smaller content first, as there are size limits

## Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/overview)
- [Microsoft Teams API Documentation](https://docs.microsoft.com/en-us/graph/teams-concept-overview)
- [Azure Active Directory Documentation](https://docs.microsoft.com/en-us/azure/active-directory/)
- [Mantis AI Documentation](https://github.com/paulelliotco/mantis-ai) 