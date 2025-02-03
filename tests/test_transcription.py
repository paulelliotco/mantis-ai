import unittest
from unittest.mock import patch
import mantis  # Global import to access mantis.transcribe


class TestTranscription(unittest.TestCase):
    def test_transcribe_with_local_file(self):
        # Mock is_youtube_url to return False
        with patch("mantis.utils.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = False

            with patch("mantis.utils.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("mantis.transcription.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.transcription.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Transcribed text from local file."}
                        )

                        # Perform transcription using the global mantis function
                        result = mantis.transcribe("sample_audio.mp3")

                        # Assertions
                        self.assertEqual(result.transcription, "Transcribed text from local file.")
                        mock_is_url.assert_called_once_with("sample_audio.mp3")
                        mock_upload.assert_called_once_with("sample_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_transcribe_invalid_input(self):
        with self.assertRaises(ValueError):
            mantis.transcribe("invalid_audio_file.xyz")


if __name__ == "__main__":
    unittest.main()
