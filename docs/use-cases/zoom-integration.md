# Zoom Integration

This guide demonstrates how to integrate Mantis AI with Zoom to automatically process meeting recordings, providing transcriptions, summaries, and extracting key information.

## Overview

Integrating Mantis AI with Zoom enables:

- Automatic processing of Zoom meeting recordings
- Generation of meeting transcripts, summaries, and action items
- Distribution of meeting insights to participants
- Creation of searchable meeting archives

## Prerequisites

- Zoom account with admin access
- Zoom API credentials
- Python 3.9+ environment
- Mantis AI package installed (`pip install mantisai`)
- Cloud storage for meeting recordings (optional)

## Setup

### 1. Create a Zoom App

1. Go to the [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" > "Build App"
3. Select "Server-to-Server OAuth" app type
4. Provide app information and create the app
5. Note the Account ID, Client ID, and Client Secret

### 2. Configure App Scopes

1. In your app settings, go to "Scopes"
2. Add the following scopes:
   - `recording:read:admin`
   - `recording:write:admin`
   - `meeting:read:admin`
   - `user:read:admin`

### 3. Enable Webhooks (Optional)

1. In your app settings, go to "Feature" > "Webhook"
2. Enable the webhook and provide an endpoint URL
3. Subscribe to the following events:
   - `recording.completed`

## Implementation

### Basic Zoom Integration

```python
import os
import requests
import time
import base64
import json
from datetime import datetime, timedelta
from mantisai import transcribe, summarize, extract
from mantisai.models import TranscriptionInput, SummarizeInput, ExtractInput

# Zoom API configuration
ZOOM_ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"

# Get access token for Zoom API
def get_zoom_access_token():
    url = f"https://zoom.us/oauth/token"
    
    # Create the authorization header
    auth_string = f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "account_credentials",
        "account_id": ZOOM_ACCOUNT_ID
    }
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    
    return response.json()["access_token"]

# Get recent completed recordings
def get_recent_recordings(access_token):
    # Calculate date range (e.g., last 24 hours)
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    to_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get all users
    users_url = f"{ZOOM_API_BASE_URL}/users"
    users_response = requests.get(users_url, headers=headers)
    users_response.raise_for_status()
    
    users = users_response.json().get("users", [])
    
    all_recordings = []
    
    # Get recordings for each user
    for user in users:
        user_id = user["id"]
        recordings_url = f"{ZOOM_API_BASE_URL}/users/{user_id}/recordings"
        params = {
            "from": from_date,
            "to": to_date,
            "page_size": 100
        }
        
        recordings_response = requests.get(recordings_url, headers=headers, params=params)
        recordings_response.raise_for_status()
        
        meetings = recordings_response.json().get("meetings", [])
        all_recordings.extend(meetings)
    
    return all_recordings

# Download recording file
def download_recording(recording_files, access_token):
    # Find MP4 recording
    mp4_recording = None
    for file in recording_files:
        if file.get("file_type") == "MP4":
            mp4_recording = file
            break
    
    if not mp4_recording:
        return None
    
    # Get download URL
    download_url = mp4_recording.get("download_url")
    if not download_url:
        return None
    
    # Add access token to URL
    download_url_with_token = f"{download_url}?access_token={access_token}"
    
    # Download the file
    response = requests.get(download_url_with_token)
    response.raise_for_status()
    
    # Save to temporary file
    file_path = f"/tmp/zoom_recording_{int(time.time())}.mp4"
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

# Send email with meeting insights
def send_meeting_insights(meeting_topic, participants, summary, extraction):
    # This would integrate with an email service like SendGrid or SMTP
    # For demonstration purposes, we'll just print the content
    
    # Format action items and decisions
    action_items = "\n".join([f"- {item}" for item in extraction.action_items])
    decisions = "\n".join([f"- {item}" for item in extraction.decisions])
    
    email_content = f"""
    Meeting Summary: {meeting_topic}
    
    Summary:
    {summary.summary}
    
    Action Items:
    {action_items}
    
    Decisions:
    {decisions}
    """
    
    print(f"Would send email to {len(participants)} participants with content:")
    print(email_content)
    
    # Actual implementation would use an email service
    # ...

# Store processed meeting data
def store_meeting_data(meeting_id, meeting_topic, transcription, summary, extraction):
    # This would store the data in a database or file system
    # For demonstration purposes, we'll just create a JSON file
    
    meeting_data = {
        "meeting_id": meeting_id,
        "meeting_topic": meeting_topic,
        "transcription": transcription.text,
        "summary": summary.summary,
        "action_items": extraction.action_items,
        "decisions": extraction.decisions,
        "processed_at": datetime.utcnow().isoformat()
    }
    
    # Save to file
    file_path = f"/tmp/meeting_{meeting_id}.json"
    with open(file_path, 'w') as f:
        json.dump(meeting_data, f, indent=2)
    
    return file_path

# Main function to process recent recordings
def process_recent_recordings():
    try:
        # Get access token
        access_token = get_zoom_access_token()
        
        # Get recent recordings
        recordings = get_recent_recordings(access_token)
        
        for meeting in recordings:
            meeting_id = meeting.get("id")
            meeting_topic = meeting.get("topic", "Untitled Meeting")
            recording_files = meeting.get("recording_files", [])
            participants = meeting.get("participants", [])
            
            # Check if we've already processed this meeting
            if is_meeting_processed(meeting_id):
                continue
            
            # Download recording
            file_path = download_recording(recording_files, access_token)
            if not file_path:
                continue
            
            try:
                # Process recording
                transcription, summary, extraction = process_recording(file_path)
                
                # Send insights to participants
                send_meeting_insights(meeting_topic, participants, summary, extraction)
                
                # Store processed data
                store_meeting_data(meeting_id, meeting_topic, transcription, summary, extraction)
                
                # Mark meeting as processed
                mark_meeting_processed(meeting_id)
            finally:
                # Clean up
                if os.path.exists(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"Error processing recordings: {e}")

def is_meeting_processed(meeting_id):
    # Implementation to check if meeting has been processed
    # This could check a database or file system
    # ...
    return False

def mark_meeting_processed(meeting_id):
    # Implementation to mark meeting as processed
    # This could update a database or file system
    # ...
    pass

# Webhook handler for recording.completed event
def handle_recording_completed_webhook(request_data):
    # Extract meeting information from webhook payload
    payload = request_data.get("payload", {})
    meeting_id = payload.get("object", {}).get("id")
    
    if not meeting_id:
        return {"status": "error", "message": "Invalid webhook payload"}
    
    # Process the specific meeting
    try:
        access_token = get_zoom_access_token()
        
        # Get meeting details
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        meeting_url = f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}"
        meeting_response = requests.get(meeting_url, headers=headers)
        meeting_response.raise_for_status()
        
        meeting = meeting_response.json()
        
        # Get recording files
        recordings_url = f"{ZOOM_API_BASE_URL}/meetings/{meeting_id}/recordings"
        recordings_response = requests.get(recordings_url, headers=headers)
        recordings_response.raise_for_status()
        
        recording_files = recordings_response.json().get("recording_files", [])
        
        # Process the recording
        file_path = download_recording(recording_files, access_token)
        if file_path:
            try:
                transcription, summary, extraction = process_recording(file_path)
                
                # Send insights to participants
                participants = meeting.get("participants", [])
                send_meeting_insights(meeting.get("topic"), participants, summary, extraction)
                
                # Store processed data
                store_meeting_data(meeting_id, meeting.get("topic"), transcription, summary, extraction)
                
                return {"status": "success", "message": "Meeting processed successfully"}
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return {"status": "error", "message": "Failed to download recording"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Run periodically or as a webhook handler
    process_recent_recordings()
```

### Advanced Features

#### Custom Zoom App with UI

Create a Zoom Marketplace app with a custom UI:

```python
# This would be part of a web application (e.g., using Flask)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/zoom/auth', methods=['GET'])
def zoom_auth():
    # Handle Zoom OAuth flow
    # ...
    return "Authentication successful"

@app.route('/zoom/webhook', methods=['POST'])
def zoom_webhook():
    # Verify webhook signature
    # ...
    
    # Process the webhook
    result = handle_recording_completed_webhook(request.json)
    return jsonify(result)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Display a dashboard of processed meetings
    # ...
    return render_template('dashboard.html', meetings=meetings)
```

#### Meeting Analytics

Generate analytics from processed meetings:

```python
def generate_meeting_analytics(user_id, access_token):
    # Get all processed meetings for the user
    # ...
    
    # Calculate analytics
    analytics = {
        "total_meetings": len(meetings),
        "total_duration_minutes": sum(m.get("duration", 0) for m in meetings),
        "average_duration_minutes": sum(m.get("duration", 0) for m in meetings) / len(meetings) if meetings else 0,
        "action_items_per_meeting": sum(len(m.get("action_items", [])) for m in meetings) / len(meetings) if meetings else 0,
        "most_active_participants": get_most_active_participants(meetings),
        # More analytics...
    }
    
    return analytics
```

## Deployment

### Hosting Options

1. **AWS Lambda**: Serverless option for webhook handling and periodic processing
2. **Heroku**: Simple deployment for web applications
3. **Docker**: Containerized deployment for better isolation

### Environment Variables

Set these environment variables in your deployment environment:

```
ZOOM_ACCOUNT_ID=your-zoom-account-id
ZOOM_CLIENT_ID=your-zoom-client-id
ZOOM_CLIENT_SECRET=your-zoom-client-secret
GOOGLE_API_KEY=your-gemini-api-key
```

## Best Practices

1. **Webhook Verification**: Always verify Zoom webhook signatures
2. **Error Handling**: Implement robust error handling for API failures
3. **Rate Limiting**: Respect Zoom API rate limits
4. **Security**: Store credentials securely
5. **Logging**: Implement comprehensive logging for troubleshooting

## Example Use Cases

### Team Meetings

Process regular team meetings to:
- Create searchable transcripts for reference
- Track action items and decisions over time
- Analyze meeting effectiveness and participation

### Webinars and Training

Process webinar recordings to:
- Create transcripts for accessibility
- Generate summaries for marketing content
- Extract frequently asked questions

### Client Meetings

Enhance client interactions by:
- Creating accurate records of client discussions
- Tracking client requests and commitments
- Analyzing client sentiment and engagement

## Troubleshooting

### Common Issues

1. **Recording Access Issues**:
   - Solution: Verify API permissions and ensure recordings are cloud-based

2. **Large File Processing**:
   - Solution: Implement chunking for large files or use cloud storage as an intermediate step

3. **Webhook Reliability**:
   - Solution: Implement a backup periodic check for missed webhook events

## Resources

- [Zoom API Documentation](https://marketplace.zoom.us/docs/api-reference/introduction)
- [Zoom Webhooks Documentation](https://marketplace.zoom.us/docs/api-reference/webhook-reference)
- [Zoom App Types](https://marketplace.zoom.us/docs/guides/build/app-types)
- [Mantis AI Documentation](https://github.com/paulelliotco/mantis-ai) 