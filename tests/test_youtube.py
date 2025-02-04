# tests/test_youtube.py
import unittest
from unittest.mock import patch
import os
import mantis  # Global import


class TestYouTubeProcessing(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        os.environ["CI"] = "true"
        self.youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def tearDown(self):
        # Clean up environment variables
        if "CI" in os.environ:
            del os.environ["CI"]

    def test_transcribe_youtube_url(self):
        with (
            patch("mantis.utils.is_youtube_url") as mock_is_url,
            patch("google.generativeai.upload_file") as mock_upload,
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            mock_is_url.return_value = True
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = type(
                "Response", (object,), {"text": "YouTube transcription output"}
            )

            result = mantis.transcribe(self.youtube_url)
            self.assertEqual(result.transcription, "YouTube transcription output")

    def test_summarize_youtube_url(self):
        with (
            patch("mantis.utils.is_youtube_url") as mock_is_url,
            patch("google.generativeai.upload_file") as mock_upload,
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            mock_is_url.return_value = True
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = type(
                "Response", (object,), {"text": "YouTube summary output"}
            )

            result = mantis.summarize(self.youtube_url)
            self.assertEqual(result.summary, "YouTube summary output")

    def test_extract_youtube_url(self):
        with (
            patch("mantis.utils.is_youtube_url") as mock_is_url,
            patch("google.generativeai.upload_file") as mock_upload,
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            mock_is_url.return_value = True
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = type(
                "Response", (object,), {"text": "YouTube extraction output"}
            )

            result = mantis.extract(self.youtube_url, "Extract info")
            self.assertEqual(result.extraction, "YouTube extraction output")


if __name__ == "__main__":
    unittest.main()
