# Google Drive Integration

This guide demonstrates how to integrate Mantis AI with Google Drive to automatically process audio files, creating transcriptions, summaries, and extracting key information.

## Overview

Integrating Mantis AI with Google Drive enables:

- Automatic processing of audio files uploaded to specific folders
- Creation of transcription documents alongside original audio
- Generation of meeting summaries and action item lists
- Building a searchable archive of audio content

## Prerequisites

- Google Cloud Platform account
- Google Drive API and Google Docs API enabled
- Python 3.9+ environment
- Mantis AI package installed (`pip install mantisai`)
- Google API credentials

## Setup

### 1. Set Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API and Google Docs API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" or "Web application"
   - Download the credentials JSON file

### 2. Configure Authentication

For a service that will run on a server:

1. Create a service account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Grant appropriate roles (e.g., "Drive File Creator")
   - Create and download the service account key (JSON)

2. Share the target Google Drive folders with the service account email

## Implementation

### Basic Google Drive Integration

```python
import os
import io
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from mantisai import transcribe, summarize, extract
from mantisai.models import TranscriptionInput, SummarizeInput, ExtractInput

# Set up Google Drive API client
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account-key.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=credentials)

# Set up Google Docs API client
def get_docs_service():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account-key.json',
        scopes=['https://www.googleapis.com/auth/documents']
    )
    return build('docs', 'v1', credentials=credentials)

# Monitor a specific folder for new audio files
def monitor_folder(folder_id):
    drive_service = get_drive_service()
    
    # Get the last check time
    last_check_time = get_last_check_time()
    
    # Search for audio files created after the last check
    query = f"'{folder_id}' in parents and (mimeType contains 'audio/' or mimeType contains 'video/') and createdTime > '{last_check_time}'"
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType)'
    ).execute()
    
    # Process each new file
    for file in results.get('files', []):
        process_file(file['id'], file['name'], drive_service)
    
    # Update the last check time
    update_last_check_time()

def get_last_check_time():
    # Implementation to retrieve the last check time
    # Could be stored in a database or file
    # ...
    return '2023-01-01T00:00:00'

def update_last_check_time():
    # Implementation to update the last check time
    # ...
    pass

def process_file(file_id, file_name, drive_service):
    # Download the file
    request = drive_service.files().get_media(fileId=file_id)
    file_path = f"/tmp/{file_name}"
    
    with io.FileIO(file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    
    # Process with Mantis AI
    try:
        # Transcribe
        transcription_result = transcribe(
            TranscriptionInput(audio_path=file_path)
        )
        
        # Summarize
        summary_result = summarize(
            SummarizeInput(text=transcription_result.text)
        )
        
        # Extract information
        extraction_result = extract(
            ExtractInput(
                text=transcription_result.text,
                extraction_type="meeting"
            )
        )
        
        # Create Google Docs with the results
        create_google_docs(
            file_name, 
            transcription_result, 
            summary_result, 
            extraction_result, 
            drive_service
        )
    finally:
        # Clean up the temporary file
        os.remove(file_path)

def create_google_docs(file_name, transcription, summary, extraction, drive_service):
    docs_service = get_docs_service()
    
    # Create a Google Doc for the transcription
    doc_metadata = {
        'name': f"{file_name} - Transcription",
        'mimeType': 'application/vnd.google-apps.document',
    }
    
    doc = drive_service.files().create(
        body=doc_metadata,
        fields='id'
    ).execute()
    
    # Add content to the document
    doc_content = {
        'requests': [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': transcription.text
                }
            }
        ]
    }
    
    docs_service.documents().batchUpdate(
        documentId=doc.get('id'),
        body=doc_content
    ).execute()
    
    # Create a Google Doc for the summary and action items
    summary_doc_metadata = {
        'name': f"{file_name} - Summary and Action Items",
        'mimeType': 'application/vnd.google-apps.document',
    }
    
    summary_doc = drive_service.files().create(
        body=summary_doc_metadata,
        fields='id'
    ).execute()
    
    # Format action items and decisions
    action_items = "\n".join([f"• {item}" for item in extraction.action_items])
    decisions = "\n".join([f"• {item}" for item in extraction.decisions])
    
    # Add content to the summary document
    summary_content = {
        'requests': [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': f"Summary:\n\n{summary.summary}\n\nAction Items:\n\n{action_items}\n\nDecisions:\n\n{decisions}"
                }
            }
        ]
    }
    
    docs_service.documents().batchUpdate(
        documentId=summary_doc.get('id'),
        body=summary_content
    ).execute()

# Main function to run periodically
def main():
    # Folder ID to monitor (replace with your folder ID)
    folder_id = 'your_folder_id_here'
    
    while True:
        try:
            monitor_folder(folder_id)
        except Exception as e:
            print(f"Error: {e}")
        
        # Wait before checking again (e.g., every 5 minutes)
        time.sleep(300)

if __name__ == "__main__":
    main()
```

### Advanced Features

#### Automatic Organization

Organize processed files into categorized folders based on content:

```python
def categorize_content(extraction_result, drive_service):
    # Determine category based on content
    categories = determine_categories(extraction_result)
    
    # Move or tag files accordingly
    for category in categories:
        # Implementation to organize by category
        # ...
```

#### Collaborative Workflows

Create shared documents with assigned action items:

```python
def assign_action_items(extraction_result, drive_service):
    # Parse action items to identify assignees
    for item in extraction_result.action_items:
        assignee = extract_assignee(item)
        if assignee:
            # Create task or share document with assignee
            # ...
```

## Deployment

### Hosting Options

1. **Google Cloud Functions**: Serverless option triggered by Cloud Scheduler
2. **Google Compute Engine**: VM-based hosting for continuous processing
3. **Google Cloud Run**: Container-based deployment with scaling

### Environment Variables

Set these environment variables in your deployment environment:

```
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
GOOGLE_API_KEY=your-gemini-api-key
MONITORED_FOLDER_ID=your-google-drive-folder-id
```

## Best Practices

1. **Incremental Processing**: Only process new files to avoid redundant work
2. **Error Handling**: Implement robust error handling and logging
3. **Rate Limiting**: Respect Google API quotas and rate limits
4. **Security**: Store credentials securely and use least-privilege access
5. **Notifications**: Implement notification systems for processing status

## Example Use Cases

### Team Knowledge Base

Create a searchable knowledge base from:
- Team meetings and presentations
- Training sessions and workshops
- Company town halls and announcements

### Content Production

Streamline content creation workflow:
- Process interview recordings for articles or blog posts
- Generate podcast show notes automatically
- Create video captions and descriptions

### Research and Analysis

Support research activities:
- Process research interviews and focus groups
- Analyze field recordings and observations
- Extract insights from conference presentations

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Solution: Verify service account permissions and check that folders are shared properly

2. **API Quotas**:
   - Solution: Implement exponential backoff and monitor quota usage

3. **Large File Processing**:
   - Solution: Implement chunking for large files or use Google Cloud Storage as an intermediate step

## Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [Google Cloud Platform Documentation](https://cloud.google.com/docs)
- [Mantis AI Documentation](https://github.com/paulelliotco/mantis-ai) 