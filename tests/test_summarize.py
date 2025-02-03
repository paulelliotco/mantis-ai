import unittest
from unittest.mock import patch
import mantis  # Global import; we call functions as mantis.summarize


class TestSummarization(unittest.TestCase):
    def test_summarize_with_local_file(self):
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
                            "Response", (object,), {"text": "Summary of local file."}
                        )

                        # Use the global mantis function for summarization
                        result = mantis.summarize("sample_audio.mp3")

                        # Assertions
                        self.assertEqual(result.summary, "Summary of local file.")
                        mock_is_url.assert_called_once_with("sample_audio.mp3")
                        mock_upload.assert_called_once_with("sample_audio.mp3")
                        mock_model.assert_called_once_with("gemini-1.5-flash")
                        mock_instance.generate_content.assert_called_once()

    def test_summarize_invalid_input(self):
        with self.assertRaises(ValueError):
            mantis.summarize("invalid_audio_file.xyz")


if __name__ == "__main__":
    unittest.main()
