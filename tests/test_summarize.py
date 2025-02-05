import unittest
from unittest.mock import patch, MagicMock
from mantis import summarize


class TestSummarize(unittest.TestCase):
    @patch('mantis.summarize.process_audio_with_gemini')
    def test_summarize_returns_summary_string(self, mock_process_audio):
        # Simulate a dummy summarization output
        dummy_result = MagicMock()
        dummy_result.summary = "dummy summary text"
        mock_process_audio.return_value = dummy_result

        audio_file = "dummy.mp3"
        result = summarize(audio_file)
        self.assertEqual(result, "dummy summary text")


if __name__ == "__main__":
    unittest.main()
