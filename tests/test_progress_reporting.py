import unittest
from unittest.mock import patch, MagicMock, call
import os
from mantis import transcribe
from mantis.models import ProcessingProgress

class TestProgressReporting(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_audio_dir = os.path.join(self.test_dir, "sample_audio")
        self.sample_audio = os.path.join(self.sample_audio_dir, "sample_audio.mp3")
    
    @patch('mantis.utils.process_audio_with_gemini')
    def test_progress_callback_is_passed(self, mock_process):
        # Setup mock
        mock_process.return_value = "Transcribed text"
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Call the function with the callback
        transcribe(self.sample_audio, progress_callback=mock_callback)
        
        # Verify the callback was passed to process_audio_with_gemini
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        self.assertEqual(kwargs['progress_callback'], mock_callback)
    
    @patch('mantis.utils.genai.upload_file')
    @patch('mantis.utils.genai.GenerativeModel')
    @patch('mantis.utils.is_youtube_url')
    def test_progress_reporting_local_file(self, mock_is_url, mock_model_class, mock_upload):
        # Setup mocks
        mock_is_url.return_value = False
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(text="Transcribed text")
        mock_upload.return_value = "uploaded_file_id"
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Call the function with the callback
        transcribe(self.sample_audio, progress_callback=mock_callback)
        
        # Verify the callback was called with the expected progress updates
        expected_calls = [
            call(ProcessingProgress("Starting processing", 0.0)),
            call(ProcessingProgress("Processing with AI model", 0.5)),
            call(ProcessingProgress("Processing complete", 1.0))
        ]
        mock_callback.assert_has_calls(expected_calls, any_order=False)
    
    @patch('mantis.utils.stream_youtube_audio')
    @patch('mantis.utils.genai.upload_file')
    @patch('mantis.utils.genai.GenerativeModel')
    @patch('mantis.utils.is_youtube_url')
    def test_progress_reporting_youtube(self, mock_is_url, mock_model_class, mock_upload, mock_stream):
        # Setup mocks
        mock_is_url.return_value = True
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(text="Transcribed text")
        mock_upload.return_value = "uploaded_file_id"
        mock_stream.return_value = self.sample_audio
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Call the function with the callback
        transcribe("https://www.youtube.com/watch?v=example", progress_callback=mock_callback)
        
        # Verify the callback was called with the expected progress updates
        # Note: We don't check the exact calls because stream_youtube_audio will make its own calls
        self.assertTrue(mock_callback.call_count >= 3)
        
        # Verify the stream_youtube_audio was called with the callback
        mock_stream.assert_called_once()
        args, kwargs = mock_stream.call_args
        self.assertEqual(kwargs['progress_callback'], mock_callback)

if __name__ == "__main__":
    unittest.main() 