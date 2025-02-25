import unittest
from unittest.mock import patch, MagicMock
import os
from mantis import transcribe, summarize, extract
from mantis.utils import (
    MantisError, 
    AudioProcessingError, 
    YouTubeDownloadError, 
    ModelInferenceError, 
    ValidationError
)

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_audio_dir = os.path.join(self.test_dir, "sample_audio")
        self.sample_audio = os.path.join(self.sample_audio_dir, "sample_audio.mp3")
    
    @patch('mantis.utils.is_youtube_url')
    def test_validation_error(self, mock_is_url):
        mock_is_url.return_value = False
        
        # Test with invalid file extension
        with self.assertRaises(ValidationError):
            transcribe("invalid_file.txt")
    
    @patch('mantis.utils.is_youtube_url')
    def test_youtube_download_error(self, mock_is_url):
        mock_is_url.return_value = True
        
        with patch('mantis.utils.stream_youtube_audio') as mock_stream:
            mock_stream.side_effect = YouTubeDownloadError("Failed to download")
            
            with self.assertRaises(YouTubeDownloadError):
                transcribe("https://www.youtube.com/watch?v=example")
    
    @patch('mantis.utils.is_youtube_url')
    @patch('mantis.utils.genai.upload_file')
    def test_model_inference_error(self, mock_upload, mock_is_url):
        mock_is_url.return_value = False
        mock_upload.return_value = "uploaded_file_id"
        
        with patch('mantis.utils.genai.GenerativeModel') as mock_model_class:
            mock_model = MagicMock()
            mock_model_class.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("Model error")
            
            with self.assertRaises(ModelInferenceError):
                transcribe(self.sample_audio)
    
    @patch('mantis.utils.is_youtube_url')
    def test_audio_processing_error(self, mock_is_url):
        mock_is_url.return_value = False
        
        # Test with file that doesn't exist
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True  # Bypass validation
            
            with patch('mantis.utils.genai.upload_file') as mock_upload:
                mock_upload.side_effect = Exception("Unexpected error")
                
                with self.assertRaises(AudioProcessingError):
                    transcribe(self.sample_audio)
    
    @patch('mantis.utils.is_youtube_url')
    def test_error_propagation_summarize(self, mock_is_url):
        mock_is_url.return_value = False
        
        with patch('mantis.utils.genai.upload_file') as mock_upload:
            mock_upload.side_effect = Exception("Unexpected error")
            
            with self.assertRaises(AudioProcessingError):
                summarize(self.sample_audio)
    
    @patch('mantis.utils.is_youtube_url')
    def test_error_propagation_extract(self, mock_is_url):
        mock_is_url.return_value = False
        
        with patch('mantis.utils.genai.upload_file') as mock_upload:
            mock_upload.side_effect = Exception("Unexpected error")
            
            with self.assertRaises(AudioProcessingError):
                extract(self.sample_audio, "Extract information")

if __name__ == "__main__":
    unittest.main() 