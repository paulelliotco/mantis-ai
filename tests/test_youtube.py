# tests/test_youtube.py
import unittest
from unittest.mock import patch
import mantis  # Global import


class TestYouTubeProcessing(unittest.TestCase):
    def test_transcribe_youtube_url(self):
        # Test transcription for a YouTube URL
        youtube_url = "https://www.youtube.com/watch?v=example"
        with (
            patch("mantis.utils.is_youtube_url") as mock_is_url,
            patch("mantis.utils.stream_youtube_audio") as mock_stream,
            patch("google.generativeai.upload_file") as mock_upload,
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            mock_is_url.return_value = True
            mock_stream.return_value = "temp_audio.mp3"
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = type(
                "Response", (object,), {"text": "YouTube transcription output"}
            )

            result = mantis.transcribe(youtube_url)
            self.assertEqual(result.transcription, "YouTube transcription output")

    def test_summarize_youtube_url(self):
        # Test summarization for a YouTube URL
        youtube_url = "https://www.youtube.com/watch?v=example"
        with (
            patch("mantis.utils.is_youtube_url") as mock_is_url,
            patch("mantis.utils.stream_youtube_audio") as mock_stream,
            patch("google.generativeai.upload_file") as mock_upload,
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            mock_is_url.return_value = True
            mock_stream.return_value = "temp_audio.mp3"
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = type(
                "Response", (object,), {"text": "YouTube summary output"}
            )

            result = mantis.summarize(youtube_url)
            self.assertEqual(result.summary, "YouTube summary output")

    def test_extract_youtube_url(self):
        # Test extraction for a YouTube URL with a custom prompt
        youtube_url = "https://www.youtube.com/watch?v=example"
        with (
            patch("mantis.utils.is_youtube_url") as mock_is_url,
            patch("mantis.utils.stream_youtube_audio") as mock_stream,
            patch("google.generativeai.upload_file") as mock_upload,
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            mock_is_url.return_value = True
            mock_stream.return_value = "temp_audio.mp3"
            mock_upload.return_value = "uploaded_file_id"
            mock_instance = mock_model.return_value
            mock_instance.generate_content.return_value = type(
                "Response", (object,), {"text": "YouTube extraction output"}
            )

            result = mantis.extract(youtube_url, "Extract info")
            self.assertEqual(result.extraction, "YouTube extraction output")


if __name__ == "__main__":
    unittest.main()
