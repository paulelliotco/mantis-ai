import unittest
from unittest.mock import patch, MagicMock
from mantis import extract


class TestExtract(unittest.TestCase):
    @patch('mantis.extract.process_audio_with_gemini')
    def test_extract_returns_extraction_text(self, mock_process_audio):
        # Instead of a MagicMock with an 'extraction' attribute,
        # we directly return the string output.
        mock_process_audio.return_value = "dummy extraction content"

        audio_file = "dummy.mp3"
        prompt = "dummy prompt"
        result = extract(audio_file, prompt)
        self.assertEqual(result, "dummy extraction content")


if __name__ == "__main__":
    unittest.main()
