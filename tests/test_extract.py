import unittest
from unittest.mock import patch
import mantis  # Global import to access mantis.extract


class TestExtraction(unittest.TestCase):
    def test_extract_with_local_file(self):
        # Mock is_youtube_url to return False
        with patch("mantis.utils.is_youtube_url") as mock_is_url:
            mock_is_url.return_value = False

            with patch("mantis.utils.stream_youtube_audio") as mock_stream:
                mock_stream.return_value = "temp_audio.mp3"

                with patch("google.generativeai.upload_file") as mock_upload:
                    mock_upload.return_value = "uploaded_file_id"

                    with patch("google.generativeai.GenerativeModel") as mock_model:
                        mock_instance = mock_model.return_value
                        mock_instance.generate_content.return_value = type(
                            "Response", (object,), {"text": "Extracted information from local file."}
                        )

                        # Perform extraction using the global mantis function
                        result = mantis.extract("sample_audio.mp3", "Extract key points from this audio.")

                        # Assertions
                        self.assertEqual(result.extraction, "Extracted information from local file.")
                        mock_is_url.assert_called_once_with("sample_audio.mp3")
                        mock_upload.assert_called_once_with("sample_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_extract_invalid_input(self):
        with self.assertRaises(ValueError):
            mantis.extract("invalid_audio_file.xyz", "Extract info")


if __name__ == "__main__":
    unittest.main()
