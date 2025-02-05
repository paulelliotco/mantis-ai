# tests/test_youtube.py
import unittest
from unittest.mock import patch, MagicMock
import os
import mantis  # Global import

YOUTUBE_URL = "https://www.youtube.com/watch?v=dummy"

class TestYouTubeProcessing(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        os.environ["CI"] = "true"
        self.youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def tearDown(self):
        # Clean up environment variables
        if "CI" in os.environ:
            del os.environ["CI"]

    @patch('mantis.transcription.process_audio_with_gemini')
    def test_transcribe_youtube_url(self, mock_proc):
        dummy_result = MagicMock()
        dummy_result.transcription = "YouTube transcription output"
        mock_proc.return_value = dummy_result

        result = mantis.transcribe(self.youtube_url)
        self.assertEqual(result, "YouTube transcription output")

    @patch('mantis.summarize.process_audio_with_gemini')
    def test_summarize_youtube_url(self, mock_proc):
        dummy_result = MagicMock()
        dummy_result.summary = "YouTube summary output"
        mock_proc.return_value = dummy_result

        result = mantis.summarize(self.youtube_url)
        self.assertEqual(result, "YouTube summary output")

    @patch('mantis.extract.process_audio_with_gemini')
    def test_extract_youtube_url(self, mock_proc):
        # Return the extraction output as a string.
        mock_proc.return_value = "YouTube extraction output"

        result = mantis.extract(self.youtube_url, "Extract info")
        self.assertEqual(result, "YouTube extraction output")


if __name__ == "__main__":
    unittest.main()
