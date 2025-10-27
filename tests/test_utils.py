from pathlib import Path

import pytest

from mantis.utils import (
    _build_contents,
    _extract_output_text,
    _upload_audio_file,
    process_audio_with_gemini,
    reset_genai_client_cache,
)


class DummyUpload:
    def __init__(self, uri: str, mime_type: str, size_bytes: int):
        self.uri = uri
        self.mime_type = mime_type
        self.size_bytes = size_bytes


class DummyFiles:
    def __init__(self):
        self.calls = 0
        self.last_config = None

    def upload(self, file, config):  # noqa: ANN001 - signature mirrors google-genai
        # Consume the file-like object to simulate upload streaming.
        file.read()
        self.calls += 1
        self.last_config = config
        return DummyUpload(uri="uploaded://file", mime_type=config.get("mime_type", "audio/mpeg"), size_bytes=1024)


class DummyResponse:
    def __init__(self, output_text: str = ""):  # noqa: ANN001 - simple helper for tests
        self.output_text = output_text
        self.candidates = []


class DummyResponses:
    def __init__(self, output_text: str):
        self.calls = 0
        self.last_kwargs = None
        self.output_text = output_text

    def generate(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return DummyResponse(output_text=self.output_text)


class DummyClient:
    def __init__(self, output_text: str):
        self.files = DummyFiles()
        self.responses = DummyResponses(output_text=output_text)


@pytest.fixture(autouse=True)
def _reset_cache():
    reset_genai_client_cache()
    yield
    reset_genai_client_cache()


@pytest.fixture()
def audio_file(tmp_path: Path) -> Path:
    path = tmp_path / "sample.wav"
    path.write_bytes(b"RIFF....DATA")
    return path


def test_upload_audio_file_is_cached(audio_file: Path):
    client = DummyClient(output_text="transcript")

    first = _upload_audio_file(client, str(audio_file))
    second = _upload_audio_file(client, str(audio_file))

    assert first is second
    assert client.files.calls == 1
    assert client.files.last_config["display_name"] == audio_file.name


def test_process_audio_with_gemini_invokes_responses_api(audio_file: Path):
    client = DummyClient(output_text="transcript")

    progress_events = []

    def progress_cb(event):
        progress_events.append((event.stage, event.progress))

    result = process_audio_with_gemini(
        audio_file=str(audio_file),
        validate_input=lambda x: x,
        create_output=lambda text: text.upper(),
        model_prompt="Please transcribe",
        model_name="gemini-test",
        progress_callback=progress_cb,
        client=client,
    )

    assert result == "TRANSCRIPT"
    assert client.files.calls == 1
    assert client.responses.calls == 1
    assert client.responses.last_kwargs["model"] == "gemini-test"
    assert progress_events[0][0] == "Starting processing"
    assert progress_events[-1][0] == "Done"


def test_extract_output_text_falls_back_to_candidates():
    class CandidatePart:
        def __init__(self, text):
            self.text = text

    class CandidateContent:
        def __init__(self, text):
            self.parts = [CandidatePart(text=text)]

    class Candidate:
        def __init__(self, text):
            self.content = CandidateContent(text=text)

    class Response:
        def __init__(self):
            self.output_text = ""
            self.candidates = [Candidate("hello world")]

    assert _extract_output_text(Response()) == "hello world"


def test_build_contents_includes_prompt_and_file():
    file = DummyUpload(uri="uploaded://file", mime_type="audio/wav", size_bytes=128)
    payload = _build_contents("Summarize", file)

    assert payload[0]["role"] == "user"
    parts = payload[0]["parts"]
    assert {"text": "Summarize"} in parts
    assert {"file_data": {"file_uri": file.uri, "mime_type": file.mime_type}} in parts
