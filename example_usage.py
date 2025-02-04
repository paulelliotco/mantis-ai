import os
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel, Field
from typing import List, Optional
import mantis
from mantis.models import ProcessingOptions

# Set your API key
os.environ["GEMINI_API_KEY"] = "GEMINI_API_KEY"

# Basic Usage
# -----------

# 1. Simple transcription
transcript = mantis.transcribe("meeting.mp3")
print("\n=== Transcription ===")
print(transcript)

# 2. Summarization
summary = mantis.summarize("https://youtube.com/watch?v=example")
print("\n=== Summary ===")
print(summary)

# 3. Custom information extraction
prompt = "Extract all action items and their assigned owners"
extracted_info = mantis.extract("meeting.mp3", prompt)
print("\n=== Extracted Information ===")
print(extracted_info)

# Structured Data Extraction
# ------------------------

# Define custom schemas using Pydantic
class Speaker(BaseModel):
    name: str = Field(..., description="Name of the speaker")
    topics: List[str] = Field(..., description="Topics discussed by this speaker")
    speaking_time: float = Field(..., description="Total speaking time in minutes")

class MeetingAnalysis(BaseModel):
    title: str = Field(..., description="Title or topic of the meeting")
    speakers: List[Speaker] = Field(..., description="List of speakers and their contributions")
    action_items: List[str] = Field(..., description="Action items discussed in the meeting")
    decisions: List[str] = Field(..., description="Key decisions made during the meeting")
    next_steps: List[str] = Field(..., description="Agreed upon next steps")
    duration: float = Field(..., description="Meeting duration in minutes")

# Extract structured data
meeting_data = mantis.extract_structured(
    "meeting.mp3",
    model=MeetingAnalysis,
    description="Analyze this business meeting focusing on decisions and actions"
)

print("\n=== Structured Meeting Analysis ===")
print(f"Meeting: {meeting_data.title}")
print(f"Duration: {meeting_data.duration} minutes")
print("\nSpeakers:")
for speaker in meeting_data.speakers:
    print(f"- {speaker.name} ({speaker.speaking_time} mins)")
    print(f"  Topics: {', '.join(speaker.topics)}")
print("\nAction Items:")
for item in meeting_data.action_items:
    print(f"- {item}")
print("\nDecisions:")
for decision in meeting_data.decisions:
    print(f"- {decision}")

# Advanced Usage
# -------------

# 1. Using processing options
options = ProcessingOptions(
    chunk_size=2048 * 1024,  # Larger chunks for faster processing
    max_retries=5,           # More retries for reliability
    timeout=600              # Longer timeout for large files
)

result = mantis.transcribe("long_audio.mp3", options=options)

# 2. Progress tracking
def progress_callback(progress):
    print(f"Stage: {progress.stage}, Progress: {progress.progress:.2%}")

options_with_progress = ProcessingOptions(progress_callback=progress_callback)
result = mantis.summarize("long_podcast.mp3", options=options_with_progress)

# 3. Error handling
try:
    result = mantis.transcribe("nonexistent.mp3")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# 4. Working with YouTube URLs
youtube_transcript = mantis.transcribe("https://youtube.com/watch?v=example")
youtube_summary = mantis.summarize("https://youtube.com/watch?v=example")

# Custom Schema for YouTube Content
class VideoAnalysis(BaseModel):
    title: str = Field(..., description="Video title")
    main_points: List[str] = Field(..., description="Main points discussed")
    timestamps: dict[str, float] = Field(..., description="Key moments with timestamps")
    sentiment: str = Field(..., description="Overall sentiment of the content")
    engagement_factors: List[str] = Field(..., description="Factors likely to drive engagement")

video_analysis = mantis.extract_structured(
    "https://youtube.com/watch?v=example",
    model=VideoAnalysis,
    description="Analyze this video's content and engagement factors"
)

print("\n=== YouTube Video Analysis ===")
print(f"Title: {video_analysis.title}")
print("\nMain Points:")
for point in video_analysis.main_points:
    print(f"- {point}")
print("\nKey Moments:")
for moment, timestamp in video_analysis.timestamps.items():
    print(f"- {moment}: {timestamp:.2f}s")
print(f"\nOverall Sentiment: {video_analysis.sentiment}")

class TestStructuredExtraction(unittest.TestCase):
    def setUp(self):
        # Define test models
        class Speaker(BaseModel):
            name: str = Field(..., description="Speaker name")
            duration: float = Field(..., description="Speaking duration in minutes")

        class Meeting(BaseModel):
            title: str = Field(..., description="Meeting title")
            speakers: List[Speaker] = Field(..., description="List of speakers")
            duration: float = Field(..., description="Total duration")

        self.Speaker = Speaker
        self.Meeting = Meeting

        # Sample valid JSON response from LLM
        self.valid_json_response = '''
        {
            "title": "Project Planning",
            "speakers": [
                {"name": "Alice", "duration": 15.5},
                {"name": "Bob", "duration": 10.0}
            ],
            "duration": 25.5
        }
        '''

    def test_extract_structured_local_file(self):
        """Test structured extraction from a local file"""
        with patch("mantis.utils.is_youtube_url") as mock_is_url, \
             patch("google.generativeai.upload_file") as mock_upload, \
             patch("google.generativeai.GenerativeModel") as mock_model:
            
            # Configure mocks
            mock_is_url.return_value = False
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = MagicMock(
                text=self.valid_json_response
            )

            # Perform extraction
            result = mantis.extract_structured(
                "meeting.mp3",
                model=self.Meeting,
                description="Analyze meeting"
            )

            # Verify result
            self.assertEqual(result.title, "Project Planning")
            self.assertEqual(len(result.speakers), 2)
            self.assertEqual(result.speakers[0].name, "Alice")
            self.assertEqual(result.duration, 25.5)

            # Verify mock calls
            mock_is_url.assert_called_once_with("meeting.mp3")
            mock_upload.assert_called_once_with("meeting.mp3")
            mock_model.assert_called_once_with("gemini-1.5-flash")

    def test_extract_structured_youtube(self):
        """Test structured extraction from a YouTube URL"""
        youtube_url = "https://youtube.com/watch?v=example"
        
        with patch("mantis.utils.is_youtube_url") as mock_is_url, \
             patch("mantis.utils.stream_youtube_audio") as mock_stream, \
             patch("google.generativeai.upload_file") as mock_upload, \
             patch("google.generativeai.GenerativeModel") as mock_model, \
             patch("os.remove") as mock_remove:

            # Configure mocks
            mock_is_url.return_value = True
            mock_stream.return_value = "temp_audio.mp3"
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = MagicMock(
                text=self.valid_json_response
            )

            # Perform extraction
            result = mantis.extract_structured(
                youtube_url,
                model=self.Meeting
            )

            # Verify result
            self.assertEqual(result.title, "Project Planning")
            self.assertEqual(len(result.speakers), 2)

            # Verify mock calls
            mock_is_url.assert_called_once_with(youtube_url)
            mock_stream.assert_called_once_with(youtube_url)
            mock_upload.assert_called_once_with("temp_audio.mp3")
            mock_remove.assert_called_once_with("temp_audio.mp3")

    def test_extract_structured_with_options(self):
        """Test structured extraction with ProcessingOptions"""
        options = ProcessingOptions(
            chunk_size=1024 * 1024,
            max_retries=3,
            timeout=300
        )

        with patch("mantis.utils.is_youtube_url") as mock_is_url, \
             patch("google.generativeai.upload_file") as mock_upload, \
             patch("google.generativeai.GenerativeModel") as mock_model:
            
            mock_is_url.return_value = False
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = MagicMock(
                text=self.valid_json_response
            )

            result = mantis.extract_structured(
                "meeting.mp3",
                model=self.Meeting,
                options=options
            )

            self.assertIsInstance(result, self.Meeting)

    def test_invalid_model(self):
        """Test handling of invalid model input"""
        with self.assertRaises(TypeError):
            mantis.extract_structured("audio.mp3", model="not_a_model")

    def test_invalid_json_response(self):
        """Test handling of invalid JSON response from LLM"""
        with patch("mantis.utils.is_youtube_url") as mock_is_url, \
             patch("google.generativeai.upload_file") as mock_upload, \
             patch("google.generativeai.GenerativeModel") as mock_model:
            
            mock_is_url.return_value = False
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = MagicMock(
                text="invalid json response"
            )

            with self.assertRaises(ValueError):
                mantis.extract_structured(
                    "meeting.mp3",
                    model=self.Meeting
                )

    def test_file_not_found(self):
        """Test handling of non-existent file"""
        with patch("mantis.utils.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = False
            
            with self.assertRaises(FileNotFoundError):
                mantis.extract_structured(
                    "nonexistent.mp3",
                    model=self.Meeting
                )

    def test_youtube_download_error(self):
        """Test handling of YouTube download errors"""
        with patch("mantis.utils.is_youtube_url") as mock_is_url, \
             patch("mantis.utils.stream_youtube_audio") as mock_stream:
            
            mock_is_url.return_value = True
            mock_stream.side_effect = ConnectionError("Download failed")

            with self.assertRaises(ConnectionError):
                mantis.extract_structured(
                    "https://youtube.com/watch?v=example",
                    model=self.Meeting
                )

if __name__ == '__main__':
    unittest.main()
