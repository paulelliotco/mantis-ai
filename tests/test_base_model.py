import unittest
from pydantic import ValidationError
from mantis.models import BaseModel, TranscriptionResult, SummaryResult, ExtractionResult

class TestBaseModel(unittest.TestCase):
    def test_base_model_to_dict(self):
        # Create a simple model that inherits from BaseModel
        class TestModel(BaseModel):
            field1: str
            field2: int
            field3: list[str] = None
        
        # Create an instance of the model
        model = TestModel(field1="test", field2=42, field3=["a", "b", "c"])
        
        # Convert to dict
        model_dict = model.to_dict()
        
        # Verify the dict contains the expected data
        self.assertEqual(model_dict["field1"], "test")
        self.assertEqual(model_dict["field2"], 42)
        self.assertEqual(model_dict["field3"], ["a", "b", "c"])
    
    def test_base_model_to_json(self):
        # Create a simple model that inherits from BaseModel
        class TestModel(BaseModel):
            field1: str
            field2: int
            field3: list[str] = None
        
        # Create an instance of the model
        model = TestModel(field1="test", field2=42, field3=["a", "b", "c"])
        
        # Convert to JSON
        json_str = model.to_json()
        
        # Verify the JSON string contains the expected data
        self.assertIn('"field1": "test"', json_str)
        self.assertIn('"field2": 42', json_str)
        self.assertIn('"field3": ["a", "b", "c"]', json_str)
    
    def test_transcription_result_model(self):
        # Test the TranscriptionResult model
        text = "This is a transcription"
        
        # Create an instance of the model
        result = TranscriptionResult(text=text)
        
        # Verify the model contains the expected data
        self.assertEqual(result.text, text)
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict["text"], text)
    
    def test_summary_result_model(self):
        # Test the SummaryResult model
        text = "This is a summary"
        
        # Create an instance of the model
        result = SummaryResult(text=text)
        
        # Verify the model contains the expected data
        self.assertEqual(result.text, text)
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict["text"], text)
    
    def test_extraction_result_model(self):
        # Test the ExtractionResult model
        key_points = ["Point 1", "Point 2"]
        entities = ["Entity 1", "Entity 2"]
        summary = "This is a summary"
        raw_text = "Raw text"
        additional_data = {"extra_field": "Extra value"}
        
        # Create an instance of the model
        result = ExtractionResult(
            key_points=key_points,
            entities=entities,
            summary=summary,
            raw_text=raw_text,
            additional_data=additional_data
        )
        
        # Verify the model contains the expected data
        self.assertEqual(result.key_points, key_points)
        self.assertEqual(result.entities, entities)
        self.assertEqual(result.summary, summary)
        self.assertEqual(result.raw_text, raw_text)
        self.assertEqual(result.additional_data, additional_data)
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict["key_points"], key_points)
        self.assertEqual(result_dict["entities"], entities)
        self.assertEqual(result_dict["summary"], summary)
        self.assertEqual(result_dict["raw_text"], raw_text)
        self.assertEqual(result_dict["additional_data"], additional_data)
    
    def test_extraction_result_with_partial_data(self):
        # Test the ExtractionResult model with partial data
        key_points = ["Point 1", "Point 2"]
        
        # Create an instance of the model with only key_points
        result = ExtractionResult(key_points=key_points)
        
        # Verify the model contains the expected data
        self.assertEqual(result.key_points, key_points)
        self.assertIsNone(result.entities)
        self.assertIsNone(result.summary)
        self.assertIsNone(result.raw_text)
        self.assertEqual(result.additional_data, {})
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict["key_points"], key_points)
        self.assertIsNone(result_dict["entities"])
        self.assertIsNone(result_dict["summary"])
        self.assertIsNone(result_dict["raw_text"])
        self.assertEqual(result_dict["additional_data"], {})

if __name__ == "__main__":
    unittest.main() 