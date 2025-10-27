import json
import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib

extract_module = importlib.import_module("mantis.extract")
from mantis.response_schemas import SpeakerSummarySchema


def test_extract_structured_output_success(monkeypatch):
    expected_payload: Dict[str, Any] = {
        "summary": "Quarterly revenue increased due to new product launches.",
        "key_points": [
            "Revenue up 12% quarter over quarter",
            "Launch of Mantis Pro credited as main driver",
        ],
        "action_items": [],
        "speakers": [],
        "entities": [
            {"name": "Mantis Pro", "type": "product", "context": "New flagship release"}
        ],
        "sentiment": None,
    }
    captured_schema = {}

    def fake_process_audio(**kwargs):
        kwargs["validate_input"](kwargs["audio_file"])
        captured_schema["schema"] = kwargs.get("response_schema")
        return kwargs["create_output"](json.dumps(expected_payload))

    monkeypatch.setattr(extract_module, "process_audio_with_gemini", fake_process_audio)

    result = extract_module.extract(
        audio_file="sample.mp3",
        prompt="Provide detailed insights",
        raw_output=True,
        structured_output=True,
    )

    assert result.extraction
    assert result.structured_data == expected_payload
    assert captured_schema["schema"]["type"] == "object"
    assert "action_items" in captured_schema["schema"]["properties"]


def test_extract_structured_output_failure(monkeypatch):
    raw_text = "Action items: 1) Follow up with Alex"

    def fake_process_audio(**kwargs):
        kwargs["validate_input"](kwargs["audio_file"])
        return kwargs["create_output"](raw_text)

    monkeypatch.setattr(extract_module, "process_audio_with_gemini", fake_process_audio)

    result = extract_module.extract(
        audio_file="sample.mp3",
        prompt="List every action item",
        raw_output=True,
        structured_output=True,
    )

    assert result.extraction == raw_text
    assert result.structured_data is None


def test_extract_with_custom_schema_class(monkeypatch):
    payload = {
        "speakers": [
            {
                "speaker": "Alex",
                "highlights": ["Agreed to lead the launch plan"],
                "sentiment": "positive",
            }
        ]
    }

    def fake_process_audio(**kwargs):
        kwargs["validate_input"](kwargs["audio_file"])
        assert kwargs.get("response_schema") == SpeakerSummarySchema.model_json_schema()
        return kwargs["create_output"](json.dumps(payload))

    monkeypatch.setattr(extract_module, "process_audio_with_gemini", fake_process_audio)

    result = extract_module.extract(
        audio_file="sample.mp3",
        prompt="Summarize the speakers",
        raw_output=True,
        structured_output=True,
        response_schema=SpeakerSummarySchema,
    )

    assert result.structured_data == payload
