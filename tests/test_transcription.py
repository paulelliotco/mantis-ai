import unittest
from mantis import transcribe
from unittest.mock import patch
from mantis.utils import is_youtube_url

class TestTranscription(unittest.TestCase):
    @patch('mantis.transcription.genai.upload_file')
    @patch('mantis.transcription.genai.GenerativeModel')
    @patch('mantis.transcription.is_youtube_url')
    @patch('mantis.transcription.stream_youtube_audio')
    def test_transcribe_with_local_file(self, mock_stream, mock_is_url, mock_model, mock_upload):
        # Mock is_youtube_url to return False
        mock_is_url.return_value = False

        # Mock the upload_file and model
        mock_upload.return_value = "uploaded_file_id"
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = type('Response', (object,), {'text': 'Transcribed text from local file.'})

        # Perform transcription
        result = transcribe("sample_audio.mp3")

        # Assertions
        self.assertEqual(result.transcription, "Transcribed text from local file.")
        mock_is_url.assert_called_once_with("sample_audio.mp3")
        mock_upload.assert_called_once_with("sample_audio.mp3")
        mock_model.assert_called_once_with("gemini-1.5-flash")
        mock_instance.generate_content.assert_called_once()


    @patch('mantis.transcription.genai.upload_file')
    @patch('mantis.transcription.genai.GenerativeModel')
    @patch('mantis.transcription.is_youtube_url')
    @patch('mantis.transcription.stream_youtube_audio')
    def test_transcribe_with_youtube_url(self, mock_stream, mock_is_url, mock_model, mock_upload):
        # Mock is_youtube_url to return True
        mock_is_url.return_value = True

        # Mock the stream_youtube_audio to return a temp file path
        mock_stream.return_value = "temp_audio.mp3"

        # Mock the upload_file and model
        mock_upload.return_value = "uploaded_file_id"
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = type('Response', (object,), {'text': 'Transcribed text from YouTube.'})

        # Perform transcription
        result = transcribe("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Assertions
        self.assertEqual(result.transcription, "Transcribed text from YouTube.")
        mock_is_url.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_stream.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_upload.assert_called_once_with("temp_audio.mp3")
        mock_model.assert_called_once_with("gemini-1.5-flash")
        mock_instance.generate_content.assert_called_once()

    def test_transcribe_invalid_input(self):
        with self.assertRaises(ValueError):
            transcribe("invalid_audio_file.xyz")

if __name__ == '__main__':
    unittest.main()
