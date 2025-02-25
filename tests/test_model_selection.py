import unittest
from unittest.mock import patch, MagicMock
import os
from mantis import transcribe, summarize, extract

class TestModelSelection(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_audio_dir = os.path.join(self.test_dir, "sample_audio")
        self.sample_audio = os.path.join(self.sample_audio_dir, "sample_audio.mp3")
    
    @patch('mantis.utils.genai.upload_file')
    @patch('mantis.utils.genai.GenerativeModel')
    @patch('mantis.utils.is_youtube_url')
    def test_transcribe_model_selection(self, mock_is_url, mock_model_class, mock_upload):
        # Setup mocks
        mock_is_url.return_value = False
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(text="Transcribed text")
        mock_upload.return_value = "uploaded_file_id"
        
        # Test default model
        transcribe(self.sample_audio)
        mock_model_class.assert_called_with("gemini-1.5-flash")
        
        # Reset mocks
        mock_model_class.reset_mock()
        
        # Test custom model
        custom_model = "gemini-1.5-pro"
        transcribe(self.sample_audio, model=custom_model)
        mock_model_class.assert_called_with(custom_model)
    
    @patch('mantis.utils.genai.upload_file')
    @patch('mantis.utils.genai.GenerativeModel')
    @patch('mantis.utils.is_youtube_url')
    def test_summarize_model_selection(self, mock_is_url, mock_model_class, mock_upload):
        # Setup mocks
        mock_is_url.return_value = False
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(text="Summarized text")
        mock_upload.return_value = "uploaded_file_id"
        
        # Test default model
        summarize(self.sample_audio)
        mock_model_class.assert_called_with("gemini-1.5-flash")
        
        # Reset mocks
        mock_model_class.reset_mock()
        
        # Test custom model
        custom_model = "gemini-1.5-pro"
        summarize(self.sample_audio, model=custom_model)
        mock_model_class.assert_called_with(custom_model)
    
    @patch('mantis.utils.genai.upload_file')
    @patch('mantis.utils.genai.GenerativeModel')
    @patch('mantis.utils.is_youtube_url')
    def test_extract_model_selection(self, mock_is_url, mock_model_class, mock_upload):
        # Setup mocks
        mock_is_url.return_value = False
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.return_value = MagicMock(text="Extracted information")
        mock_upload.return_value = "uploaded_file_id"
        
        # Test default model
        extract(self.sample_audio, "Extract information")
        mock_model_class.assert_called_with("gemini-1.5-flash")
        
        # Reset mocks
        mock_model_class.reset_mock()
        
        # Test custom model
        custom_model = "gemini-1.5-pro"
        extract(self.sample_audio, "Extract information", model=custom_model)
        mock_model_class.assert_called_with(custom_model)
    
    @patch('mantis.utils.process_audio_with_gemini')
    def test_model_parameter_passing(self, mock_process):
        # Setup mock
        mock_process.return_value = "Result"
        
        # Test model parameter is passed correctly in each function
        custom_model = "gemini-1.5-pro"
        
        transcribe(self.sample_audio, model=custom_model)
        args, kwargs = mock_process.call_args
        self.assertEqual(kwargs['model_name'], custom_model)
        
        mock_process.reset_mock()
        
        summarize(self.sample_audio, model=custom_model)
        args, kwargs = mock_process.call_args
        self.assertEqual(kwargs['model_name'], custom_model)
        
        mock_process.reset_mock()
        
        extract(self.sample_audio, "Extract information", model=custom_model)
        args, kwargs = mock_process.call_args
        self.assertEqual(kwargs['model_name'], custom_model)

if __name__ == "__main__":
    unittest.main() 