import json
from pathlib import Path
from typing import Any

import pytest

import mantis
from mantis import extract
from mantis.utils import reset_genai_client_cache


class FakeUpload:
    def __init__(self):
        self.uri = "uploaded://audio"
        self.mime_type = "audio/wav"
        self.size_bytes = 2048


class FakeFiles:
    def __init__(self):
        self.calls = 0

    def upload(self, file, config):  # noqa: ANN001 - replicates SDK signature
        file.read()
        self.calls += 1
        return FakeUpload()


class FakeResponses:
    def __init__(self, payload: Any):
        self.payload = payload
        self.calls = 0
        self.last_kwargs = None

    def generate(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return self.payload


class FakeResponse:
    def __init__(self, text: str):
        self.output_text = text
        self.text = text


class FakeClient:
    def __init__(self, response_text: str):
        self.files = FakeFiles()
        self.responses = FakeResponses(FakeResponse(response_text))


@pytest.fixture(autouse=True)
def _clear_cache():
    reset_genai_client_cache()
    yield
    reset_genai_client_cache()


@pytest.fixture()
def audio_file(tmp_path: Path) -> Path:
    path = tmp_path / "sample.wav"
    path.write_bytes(b"RIFF....DATA")
    return path


def test_structured_extract_parses_json(monkeypatch, audio_file: Path):
    response_payload = json.dumps(
        {
            "summary": "Team aligned on launch plan",
            "key_points": ["QA complete", "Marketing assets scheduled"],
            "entities": ["Alice", "Bob"],
            "action_items": ["Finalize pricing"],
        }
    )
    fake_client = FakeClient(response_text=response_payload)
    monkeypatch.setattr(mantis.utils, "get_genai_client", lambda: fake_client)

    result = extract(
        audio_file=str(audio_file),
        prompt="Summarize the meeting",
        structured_output=True,
        raw_output=True,
    )

    assert result.structured_data["summary"] == "Team aligned on launch plan"
    assert "Finalize pricing" in result.structured_data["action_items"]
    assert fake_client.responses.last_kwargs["output_mime_type"] == "application/json"


def test_structured_extract_falls_back_on_invalid_json(monkeypatch, audio_file: Path):
    fake_client = FakeClient(response_text="{not-valid-json}")
    monkeypatch.setattr(mantis.utils, "get_genai_client", lambda: fake_client)

    result = extract(
        audio_file=str(audio_file),
        prompt="Summarize the meeting",
        structured_output=True,
        raw_output=True,
    )

    assert result.structured_data is None
    assert result.extraction == "{not-valid-json}"
