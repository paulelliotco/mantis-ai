import unittest
from mantis import summarize
from unittest.mock import patch


class TestSummarization(unittest.TestCase):
    @patch("mantis.summarize.genai.upload_file")
    @patch("mantis.summarize.genai.GenerativeModel")
    @patch("mantis.summarize.is_youtube_url")
    @patch("mantis.summarize.stream_youtube_audio")
    def test_summarize_with_local_file(self, mock_stream, mock_is_url, mock_model, mock_upload):
        # Mock is_youtube_url to return False
        mock_is_url.return_value = False

        # Mock the upload_file and model
        mock_upload.return_value = "uploaded_file_id"
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = type("Response", (object,), {"text": "Summary of local file."})

        # Perform summarization
        result = summarize("sample_audio.mp3")

        # Assertions
        self.assertEqual(result.summary, "Summary of local file.")
        mock_is_url.assert_called_once_with("sample_audio.mp3")
        mock_upload.assert_called_once_with("sample_audio.mp3")
        mock_model.assert_called_once_with("gemini-1.5-flash")
        mock_instance.generate_content.assert_called_once()

    @patch("mantis.summarize.genai.upload_file")
    @patch("mantis.summarize.genai.GenerativeModel")
    @patch("mantis.summarize.is_youtube_url")
    @patch("mantis.summarize.stream_youtube_audio")
    def test_summarize_with_youtube_url(self, mock_stream, mock_is_url, mock_model, mock_upload):
        # Mock is_youtube_url to return True
        mock_is_url.return_value = True

        # Mock the stream_youtube_audio to return a temp file path
        mock_stream.return_value = "temp_audio.mp3"

        # Mock the upload_file and model
        mock_upload.return_value = "uploaded_file_id"
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = type("Response", (object,), {"text": "Summary of YouTube audio."})

        # Perform summarization
        result = summarize("https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast")

        # Assertions
        self.assertEqual(result.summary, "Summary of YouTube audio.")
        mock_is_url.assert_called_once_with("https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast")
        mock_stream.assert_called_once_with("https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast")
        mock_upload.assert_called_once_with("temp_audio.mp3")
        mock_model.assert_called_once_with("gemini-1.5-flash")
        mock_instance.generate_content.assert_called_once()

    def test_summarize_invalid_input(self):
        with self.assertRaises(ValueError):
            summarize("invalid_audio_file.xyz")


if __name__ == "__main__":
    unittest.main()
