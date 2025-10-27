import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # pragma: no cover - prefer real SDK when available
    from google import genai  # type: ignore  # noqa: F401
    from google.genai import types as _types  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    google_module = types.ModuleType("google")
    genai_module = types.ModuleType("google.genai")
    types_module = types.ModuleType("google.genai.types")

    class Client:  # Minimal placeholder used only in tests
        def __init__(self, *_, **__):
            self.files = None
            self.responses = None

    class HttpOptions:
        def __init__(self, api_endpoint=None, api_region=None):
            self.api_endpoint = api_endpoint
            self.api_region = api_region

    class SafetySetting:
        def __init__(self, category=None, threshold=None):
            self.category = category
            self.threshold = threshold

    class HarmCategory:
        HARM_CATEGORY_HARASSMENT = "harassment"
        HARM_CATEGORY_HATE_SPEECH = "hate_speech"
        HARM_CATEGORY_SEXUAL_CONTENT = "sexual_content"
        HARM_CATEGORY_DANGEROUS_CONTENT = "dangerous_content"

    class HarmBlockThreshold:
        BLOCK_NONE = "block_none"

    class Type:
        OBJECT = "object"
        ARRAY = "array"
        STRING = "string"

    class Schema:
        def __init__(self, type=None, properties=None, items=None, description=None):
            self.type = type
            self.properties = properties or {}
            self.items = items
            self.description = description

    types_module.HttpOptions = HttpOptions
    types_module.SafetySetting = SafetySetting
    types_module.HarmCategory = HarmCategory
    types_module.HarmBlockThreshold = HarmBlockThreshold
    types_module.Type = Type
    types_module.Schema = Schema

    genai_module.Client = Client
    genai_module.types = types_module

    sys.modules.setdefault("google", google_module)
    sys.modules.setdefault("google.genai", genai_module)
    sys.modules.setdefault("google.genai.types", types_module)
    google_module.genai = genai_module
    genai_module.__dict__["types"] = types_module
