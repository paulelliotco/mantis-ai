import unittest
from unittest.mock import patch, MagicMock, call
import os
import io
import sys
from mantis.cli import format_transcription, format_summary, format_extraction
from mantis.models import ExtractionResult

class TestCLIOutput(unittest.TestCase):
    def setUp(self):
        # Capture stdout for testing
        self.captured_output = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output
    
    def tearDown(self):
        # Reset stdout
        sys.stdout = self.original_stdout
    
    def test_format_transcription(self):
        # Test formatting of transcription output
        test_text = "This is a test transcription."
        
        format_transcription(test_text)
        
        output = self.captured_output.getvalue()
        
        # Check that the output contains the expected formatting
        self.assertIn("TRANSCRIPTION", output)
        self.assertIn(test_text, output)
        self.assertIn("═", output)  # Check for fancy border
    
    def test_format_summary(self):
        # Test formatting of summary output
        test_text = "This is a test summary."
        
        format_summary(test_text)
        
        output = self.captured_output.getvalue()
        
        # Check that the output contains the expected formatting
        self.assertIn("SUMMARY", output)
        self.assertIn(test_text, output)
        self.assertIn("═", output)  # Check for fancy border
    
    def test_format_extraction_with_all_fields(self):
        # Test formatting of extraction output with all fields
        extraction_result = ExtractionResult(
            key_points=["Point 1", "Point 2"],
            entities=["Entity 1", "Entity 2"],
            summary="This is a summary",
            raw_text=None,
            additional_data={"extra_field": "Extra value"}
        )
        
        format_extraction(extraction_result)
        
        output = self.captured_output.getvalue()
        
        # Check that the output contains the expected formatting
        self.assertIn("EXTRACTION RESULTS", output)
        self.assertIn("KEY POINTS", output)
        self.assertIn("Point 1", output)
        self.assertIn("Point 2", output)
        self.assertIn("ENTITIES", output)
        self.assertIn("Entity 1", output)
        self.assertIn("Entity 2", output)
        self.assertIn("SUMMARY", output)
        self.assertIn("This is a summary", output)
        self.assertIn("ADDITIONAL DATA", output)
        self.assertIn("extra_field", output)
        self.assertIn("Extra value", output)
        self.assertIn("═", output)  # Check for fancy border
    
    def test_format_extraction_with_partial_fields(self):
        # Test formatting of extraction output with partial fields
        extraction_result = ExtractionResult(
            key_points=["Point 1", "Point 2"],
            entities=None,
            summary=None,
            raw_text=None,
            additional_data={}
        )
        
        format_extraction(extraction_result)
        
        output = self.captured_output.getvalue()
        
        # Check that the output contains the expected formatting
        self.assertIn("EXTRACTION RESULTS", output)
        self.assertIn("KEY POINTS", output)
        self.assertIn("Point 1", output)
        self.assertIn("Point 2", output)
        
        # Check that missing sections are not included
        self.assertNotIn("ENTITIES", output)
        self.assertNotIn("SUMMARY", output)
        self.assertNotIn("ADDITIONAL DATA", output)
    
    def test_format_extraction_with_raw_text(self):
        # Test formatting of extraction output with raw text
        extraction_result = ExtractionResult(
            key_points=None,
            entities=None,
            summary=None,
            raw_text="This is raw text that couldn't be parsed as JSON",
            additional_data={}
        )
        
        format_extraction(extraction_result)
        
        output = self.captured_output.getvalue()
        
        # Check that the output contains the expected formatting
        self.assertIn("EXTRACTION RESULTS", output)
        self.assertIn("RAW OUTPUT", output)
        self.assertIn("This is raw text that couldn't be parsed as JSON", output)
        
        # Check that missing sections are not included
        self.assertNotIn("KEY POINTS", output)
        self.assertNotIn("ENTITIES", output)
        self.assertNotIn("SUMMARY", output)
        self.assertNotIn("ADDITIONAL DATA", output)

if __name__ == "__main__":
    unittest.main() 