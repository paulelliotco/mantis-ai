import unittest
import importlib.util
import os
from unittest.mock import patch
import sys

spec = importlib.util.spec_from_file_location("mantis.extract", os.path.join("mantis", "extract.py"))
extract_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract_module)
sys.modules["mantis.extract"] = extract_module


class TestExtraction(unittest.TestCase):
    def test_extract_with_local_file(self):
        # Mock is_youtube_url to return False
        with patch("mantis.extract.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = False

            with patch("mantis.extract.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"  # Not really used in local file test

                with patch("mantis.extract.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.extract.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Extracted information from local file."}
                        )

                        # Perform extraction using the module's function
                        result = extract_module.extract("sample_audio.mp3", "Extract key points from this audio.")

                        # Assertions
                        self.assertEqual(result.extraction, "Extracted information from local file.")
                        mock_is_url.assert_called_once_with("sample_audio.mp3")  # Now assert against "sample_audio.mp3"
                        mock_upload.assert_called_once_with("sample_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_extract_with_youtube_url(self):
        # Mock is_youtube_url to return True
        with patch("mantis.extract.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = True

            with patch("mantis.extract.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("mantis.extract.genai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("mantis.extract.genai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Extracted information from YouTube audio."}
                        )

                        # Perform extraction using the module's function
                        result = extract_module.extract(
                            "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast",
                            "Extract key points from this audio.",
                        )

                        # Assertions
                        self.assertEqual(result.extraction, "Extracted information from YouTube audio.")
                        mock_is_url.assert_called_once_with(
                            "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
                        )
                        mock_stream.assert_called_once_with(
                            "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
                        )
                        mock_upload.assert_called_once_with("temp_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_extract_invalid_input(self):
        with self.assertRaises(ValueError):
            extract_module.extract("invalid_audio_file.xyz", "Extract key points.")


if __name__ == "__main__":
    unittest.main()
