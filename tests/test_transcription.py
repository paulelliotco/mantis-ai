import unittest
from unittest.mock import patch
import os
import mantis  # Global import to access mantis.transcribe


class TestTranscription(unittest.TestCase):
    def setUp(self):
        # Get the absolute path to the test directory
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_audio_dir = os.path.join(self.test_dir, "sample_audio")

    def test_transcribe_with_local_file_multiple_formats(self):
        test_files = [
            os.path.join(self.sample_audio_dir, "sample_audio.mp3"),
            os.path.join(self.sample_audio_dir, "sample_audio.wav"),
            os.path.join(self.sample_audio_dir, "sample_audio.m4a"),
            os.path.join(self.sample_audio_dir, "sample_audio.ogg")
        ]
        
        for audio_file in test_files:
            with self.subTest(audio_file=audio_file):
                with (
                    patch("mantis.utils.is_youtube_url") as mock_is_url,
                    patch("mantis.utils.stream_youtube_audio") as mock_stream,
                    patch("mantis.transcription.genai.upload_file") as mock_upload,
                    patch("mantis.transcription.genai.GenerativeModel") as mock_model
                ):
                    mock_is_url.return_value = False
                    mock_stream.return_value = "temp_audio.mp3"
                    mock_upload.return_value = "uploaded_file_id"
                    mock_instance = mock_model.return_value
                    mock_instance.generate_content.return_value = type(
                        "Response", (object,), {"text": f"Transcribed text from {os.path.basename(audio_file)}."}
                    )

                    result = mantis.transcribe(audio_file)
                    self.assertEqual(
                        result.transcription, 
                        f"Transcribed text from {os.path.basename(audio_file)}."
                    )
                    mock_is_url.assert_called_once_with(audio_file)
                    mock_upload.assert_called_once_with(audio_file)
                    mock_model.assert_called_once_with("gemini-1.5-flash")
                    mock_instance.generate_content.assert_called_once()

    def test_transcribe_invalid_input(self):
        invalid_file = os.path.join(self.test_dir, "invalid_audio_file.xyz")
        with self.assertRaises(ValueError):
            mantis.transcribe(invalid_file)


if __name__ == "__main__":
    unittest.main()
