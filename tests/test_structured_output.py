import unittest
from unittest.mock import patch, MagicMock
import os
import json
from mantis import extract
from mantis.models import ExtractionResult

class TestStructuredOutput(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_audio_dir = os.path.join(self.test_dir, "sample_audio")
        self.sample_audio = os.path.join(self.sample_audio_dir, "sample_audio.mp3")
    
    @patch('mantis.utils.process_audio_with_gemini')
    def test_extraction_returns_structured_output(self, mock_process):
        # Setup mock to return JSON string
        sample_json = {
            "key_points": ["Point 1", "Point 2"],
            "entities": ["Entity 1", "Entity 2"],
            "summary": "This is a summary"
        }
        mock_process.return_value = json.dumps(sample_json)
        
        # Call extract function
        result = extract(self.sample_audio, "Extract key points, entities, and summary")
        
        # Verify result is an ExtractionResult object
        self.assertIsInstance(result, ExtractionResult)
        
        # Verify the object contains the expected data
        self.assertEqual(result.key_points, sample_json["key_points"])
        self.assertEqual(result.entities, sample_json["entities"])
        self.assertEqual(result.summary, sample_json["summary"])
    
    @patch('mantis.utils.process_audio_with_gemini')
    def test_extraction_handles_invalid_json(self, mock_process):
        # Setup mock to return invalid JSON
        mock_process.return_value = "This is not JSON"
        
        # Call extract function
        result = extract(self.sample_audio, "Extract information")
        
        # Verify result is still an ExtractionResult object
        self.assertIsInstance(result, ExtractionResult)
        
        # Verify the raw text is stored in the result
        self.assertEqual(result.raw_text, "This is not JSON")
        
        # Verify other fields are None or empty
        self.assertIsNone(result.key_points)
        self.assertIsNone(result.entities)
        self.assertIsNone(result.summary)
    
    @patch('mantis.utils.process_audio_with_gemini')
    def test_extraction_handles_partial_json(self, mock_process):
        # Setup mock to return partial JSON (missing some fields)
        sample_json = {
            "key_points": ["Point 1", "Point 2"]
            # Missing entities and summary
        }
        mock_process.return_value = json.dumps(sample_json)
        
        # Call extract function
        result = extract(self.sample_audio, "Extract key points")
        
        # Verify result is an ExtractionResult object
        self.assertIsInstance(result, ExtractionResult)
        
        # Verify the object contains the expected data
        self.assertEqual(result.key_points, sample_json["key_points"])
        
        # Verify missing fields are None
        self.assertIsNone(result.entities)
        self.assertIsNone(result.summary)
    
    @patch('mantis.utils.process_audio_with_gemini')
    def test_extraction_handles_additional_fields(self, mock_process):
        # Setup mock to return JSON with additional fields
        sample_json = {
            "key_points": ["Point 1", "Point 2"],
            "entities": ["Entity 1", "Entity 2"],
            "summary": "This is a summary",
            "extra_field": "This is an extra field"
        }
        mock_process.return_value = json.dumps(sample_json)
        
        # Call extract function
        result = extract(self.sample_audio, "Extract information with extra fields")
        
        # Verify result is an ExtractionResult object
        self.assertIsInstance(result, ExtractionResult)
        
        # Verify the object contains the expected data
        self.assertEqual(result.key_points, sample_json["key_points"])
        self.assertEqual(result.entities, sample_json["entities"])
        self.assertEqual(result.summary, sample_json["summary"])
        
        # Verify extra fields are stored in additional_data
        self.assertEqual(result.additional_data.get("extra_field"), sample_json["extra_field"])

if __name__ == "__main__":
    unittest.main() 