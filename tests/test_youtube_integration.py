#!/usr/bin/env python3
import os
import unittest
from dotenv import load_dotenv
from mantis.utils import MantisError
import mantis

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(ENV_PATH)


class TestYouTubeIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.getenv("GEMINI_API_KEY"):
            raise unittest.SkipTest(f"GEMINI_API_KEY not found in {ENV_PATH}")

        print("\nTest Configuration:")
        print(f"ENV file: {ENV_PATH}")
        print(f"API Key present: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")

    def test_youtube_url_validation(self):
        """Test YouTube URL validation"""
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        invalid_url = "https://example.com/video"

        self.assertTrue(mantis.utils.is_youtube_url(valid_url), "Valid YouTube URL not recognized")
        self.assertFalse(mantis.utils.is_youtube_url(invalid_url), "Invalid URL incorrectly identified as YouTube URL")

    @unittest.skipIf(os.getenv("CI") == "true", "Skipping long-running YouTube download test in CI")
    def test_youtube_stream(self):
        """Test YouTube streaming functionality"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        try:
            audio_path = mantis.utils.stream_youtube_audio(url)
            self.assertTrue(os.path.exists(audio_path))
            # Cleanup
            os.remove(audio_path)
        except MantisError as e:
            self.fail(f"YouTube streaming failed: {e}")


if __name__ == "__main__":
    unittest.main()
