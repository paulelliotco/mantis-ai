import unittest
from mantis import extract
from unittest.mock import patch
from mantis.extract import is_youtube_url

class TestExtraction(unittest.TestCase):
    @patch('mantis.extract.genai.upload_file')
    @patch('mantis.extract.genai.GenerativeModel')
    @patch('mantis.extract.is_youtube_url')
    @patch('mantis.extract.stream_youtube_audio')
    def test_extract_with_local_file(self, mock_stream, mock_is_url, mock_model, mock_upload):
        # Mock is_youtube_url to return False
        mock_is_url.return_value = False

        # Mock the upload_file and model
        mock_upload.return_value = "uploaded_file_id"
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = type('Response', (object,), {'text': 'Extracted information from local file.'})

        # Perform extraction
        result = extract("sample_audio.mp3", "Extract key points from this audio.")


        # Assertions
        self.assertEqual(result.extraction, "Extracted information from local file.")
        mock_is_url.assert_called_once_with("sample_audio.mp3")
        mock_upload.assert_called_once_with("sample_audio.mp3")
        mock_model.assert_called_once_with("gemini-1.5-flash")
        mock_instance.generate_content.assert_called_once()


    @patch('mantis.extract.genai.upload_file')
    @patch('mantis.extract.genai.GenerativeModel')
    @patch('mantis.extract.is_youtube_url')
    @patch('mantis.extract.stream_youtube_audio')
    def test_extract_with_youtube_url(self, mock_stream, mock_is_url, mock_model, mock_upload):
        # Mock is_youtube_url to return True
        mock_is_url.return_value = True

        # Mock the stream_youtube_audio to return a temp file path
        mock_stream.return_value = "temp_audio.mp3"

        # Mock the upload_file and model
        mock_upload.return_value = "uploaded_file_id"
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = type('Response', (object,), {'text': 'Extracted information from YouTube audio.'})

        # Perform extraction
        result = extract("https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast", "Extract key points from this audio.")

        # Assertions
        self.assertEqual(result.extraction, "Extracted information from YouTube audio.")
        mock_is_url.assert_called_once_with("https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast")
        mock_stream.assert_called_once_with("https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast")
        mock_upload.assert_called_once_with("temp_audio.mp3")
        mock_model.assert_called_once_with("gemini-1.5-flash")
        mock_instance.generate_content.assert_called_once()

    def test_extract_invalid_input(self):
        with self.assertRaises(ValueError):
            extract("invalid_audio_file.xyz", "Extract key points.")

if __name__ == '__main__':
    unittest.main() 