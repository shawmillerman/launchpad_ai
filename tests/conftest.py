import sys
from pathlib import Path
from unittest.mock import MagicMock

# Make the `app` package importable when tests are run from any working directory.
sys.path.insert(0, str(Path(__file__).parent.parent))

# Stub google.genai + google.genai.types so app.ingest_image can be imported
# and unit-tested without the live google-genai SDK installed.
try:
    from google import genai as _  # noqa: F401
except ImportError:
    import google as _google  # google namespace package exists from google-auth
    _genai_stub = MagicMock(name="google.genai")
    _genai_stub.Client = MagicMock(name="google.genai.Client")
    sys.modules["google.genai"] = _genai_stub
    sys.modules["google.genai.types"] = MagicMock(name="google.genai.types")
    _google.genai = _genai_stub
