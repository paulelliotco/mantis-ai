import unittest
import importlib.util
import os
from unittest.mock import patch
import sys

spec = importlib.util.spec_from_file_location("mantis.summarize", os.path.join("mantis", "summarize.py"))
summarize_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarize_module)
sys.modules["mantis.summarize"] = summarize_module


class TestSummarization(unittest.TestCase):
    def test_summarize_with_local_file(self):
        # Mock is_youtube_url to return False
        with patch("mantis.utils.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = False

            with patch("mantis.utils.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("mantis.summarize.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.summarize.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Summary of local file."}
                        )

                        # Perform summarization using the module's function
                        result = summarize_module.summarize("sample_audio.mp3")

                        # Assertions
                        self.assertEqual(result.summary, "Summary of local file.")
                        mock_is_url.assert_called_once_with("sample_audio.mp3")
                        mock_upload.assert_called_once_with("sample_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_summarize_with_youtube_url(self):
        # Mock is_youtube_url to return True
        with patch("mantis.utils.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = True

            with patch("mantis.utils.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("mantis.summarize.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.summarize.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Summary of YouTube audio."}
                        )

                        # Perform summarization using the module's function
                        result = summarize_module.summarize(
                            "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
                        )

                        # Assertions
                        self.assertEqual(result.summary, "Summary of YouTube audio.")
                        mock_is_url.assert_called_once_with(
                            "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
                        )
                        mock_stream.assert_called_once_with(
                            "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
                        )
                        mock_upload.assert_called_once_with("temp_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_summarize_invalid_input(self):
        with self.assertRaises(ValueError):
            summarize_module.summarize("invalid_audio_file.xyz")


if __name__ == "__main__":
    unittest.main()
