import unittest
import importlib.util
import os
from unittest.mock import patch
import sys

spec = importlib.util.spec_from_file_location("mantis.transcription", os.path.join("mantis", "transcription.py"))
transcribe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transcribe_module)
sys.modules["mantis.transcription"] = transcribe_module


class TestTranscription(unittest.TestCase):
    def test_transcribe_with_local_file(self):
        # Mock is_youtube_url to return False
        with patch("mantis.transcription.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = False

            with patch("mantis.transcription.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("mantis.transcription.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.transcription.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Transcribed text from local file."}
                        )

                        # Perform transcription
                        result = transcribe_module.transcribe("sample_audio.mp3")

                        # Assertions
                        self.assertEqual(result.transcription, "Transcribed text from local file.")
                        mock_is_url.assert_called_once_with("sample_audio.mp3")
                        mock_upload.assert_called_once_with("sample_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_transcribe_with_youtube_url(self):
        # Mock is_youtube_url to return True
        with patch("mantis.transcription.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = True

            with patch("mantis.transcription.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("mantis.transcription.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.transcription.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Transcribed text from YouTube."}
                        )

                        # Perform transcription
                        result = transcribe_module.transcribe("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

                        # Assertions
                        self.assertEqual(result.transcription, "Transcribed text from YouTube.")
                        mock_is_url.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                        mock_stream.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                        mock_upload.assert_called_once_with("temp_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_transcribe_invalid_input(self):
        with self.assertRaises(ValueError):
            transcribe_module.transcribe("invalid_audio_file.xyz")


if __name__ == "__main__":
    unittest.main()
