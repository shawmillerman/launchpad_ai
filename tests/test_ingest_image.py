"""Regression tests for the image ingestion pipeline.

Coverage:
- ImageIngestionPipeline._call_vision_api  — extraction, edge cases, warning population
- ImageIngestionPipeline.extract_text      — public interface and graceful failure handling
- ingest_image() in ingest.py              — record schema, warning propagation, dispatcher routing
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import modules under test at the top level so `app` registers ingest_image
# and ingest as attributes — required for patch() to resolve dotted paths.
import app.ingest_image  # noqa: F401  (side-effect: registers app.ingest_image)
import app.ingest        # noqa: F401  (side-effect: registers app.ingest)
from app.ingest_image import ImageIngestionPipeline


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_png(tmp_path: Path, name: str = "test.png") -> Path:
    """Write a minimal 1×1 white PNG using Pillow and return its path."""
    from PIL import Image as PILImage

    img = PILImage.new("RGB", (1, 1), color=(255, 255, 255))
    p = tmp_path / name
    img.save(str(p))
    return p


def _mock_genai_client(text: str = "extracted text") -> MagicMock:
    """Return a mock genai.Client whose generate_content call returns `text`."""
    client = MagicMock()
    response = MagicMock()
    response.text = text
    client.models.generate_content.return_value = response
    return client


# ---------------------------------------------------------------------------
# Fixture: patch genai.Client so no constructor ever hits the network/env
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_client_factory():
    """Yields a callable that returns a mock client and patches the constructor."""
    def _factory(text: str = "extracted text"):
        return _mock_genai_client(text)
    return _factory


# ---------------------------------------------------------------------------
# _call_vision_api
# ---------------------------------------------------------------------------

class TestCallVisionApi:

    def test_happy_path_returns_raw_text(self, tmp_path, mock_client_factory):
        img_path = _make_png(tmp_path)
        client = mock_client_factory("Hello\nWorld")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        warnings = []
        result = pipeline._call_vision_api(str(img_path), warnings)

        assert result == "Hello\nWorld"
        assert warnings == []

    def test_missing_file_raises_file_not_found(self, tmp_path, mock_client_factory):
        client = mock_client_factory()

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        with pytest.raises(FileNotFoundError):
            pipeline._call_vision_api(str(tmp_path / "ghost.png"), [])

    def test_empty_file_adds_warning_and_returns_empty_string(self, tmp_path, mock_client_factory):
        img_path = tmp_path / "empty.png"
        img_path.write_bytes(b"")
        client = mock_client_factory()

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        warnings = []
        result = pipeline._call_vision_api(str(img_path), warnings)

        assert result == ""
        assert any("Empty file" in w for w in warnings)

    def test_empty_api_response_adds_warning_and_returns_empty_string(self, tmp_path, mock_client_factory):
        img_path = _make_png(tmp_path)
        client = mock_client_factory(text="")  # API returns empty string

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        warnings = []
        result = pipeline._call_vision_api(str(img_path), warnings)

        assert result == ""
        assert any("empty" in w.lower() for w in warnings)

    def test_unknown_extension_adds_mime_fallback_warning(self, tmp_path, mock_client_factory):
        # Write a file whose extension mimetypes cannot resolve.
        img_path = tmp_path / "image.xyz123"
        img_path.write_bytes(b"\x89PNG fake content")
        client = mock_client_factory("some text")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        warnings = []
        try:
            pipeline._call_vision_api(str(img_path), warnings)
        except Exception:
            pass  # Processing may still fail; warning accumulation is what matters here.

        assert any("MIME" in w for w in warnings)

    def test_unsupported_mime_type_adds_warning(self, tmp_path, mock_client_factory):
        # .bmp is a real MIME type but not in the supported list.
        img_path = tmp_path / "image.bmp"
        from PIL import Image as PILImage
        PILImage.new("RGB", (1, 1)).save(str(img_path), format="BMP")
        client = mock_client_factory("some text")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        warnings = []
        try:
            pipeline._call_vision_api(str(img_path), warnings)
        except Exception:
            pass

        assert any("Unsupported MIME type" in w for w in warnings)

    def test_api_exception_adds_warning_and_reraises(self, tmp_path):
        img_path = _make_png(tmp_path)
        client = MagicMock()
        client.models.generate_content.side_effect = RuntimeError("network error")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        warnings = []
        with pytest.raises(RuntimeError, match="network error"):
            pipeline._call_vision_api(str(img_path), warnings)

        assert any("Gemini API Exception" in w for w in warnings)


# ---------------------------------------------------------------------------
# extract_text
# ---------------------------------------------------------------------------

class TestExtractText:

    def test_returns_correct_dict_structure(self, tmp_path, mock_client_factory):
        img_path = _make_png(tmp_path)
        client = mock_client_factory("Extracted content")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        result = pipeline.extract_text(str(img_path))

        assert result["content"] == "Extracted content"
        assert result["source_file"] == str(img_path)
        assert "quality_signals" in result["metadata"]
        assert "extraction_warnings" in result["metadata"]["quality_signals"]

    def test_no_warnings_on_clean_extraction(self, tmp_path, mock_client_factory):
        img_path = _make_png(tmp_path)
        client = mock_client_factory("Clean text")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        result = pipeline.extract_text(str(img_path))

        assert result["metadata"]["quality_signals"]["extraction_warnings"] == []

    def test_exception_returns_empty_content_with_warning(self, tmp_path):
        img_path = _make_png(tmp_path)
        client = MagicMock()
        client.models.generate_content.side_effect = RuntimeError("api down")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        result = pipeline.extract_text(str(img_path))

        assert result["content"] == ""
        warnings = result["metadata"]["quality_signals"]["extraction_warnings"]
        assert any("Gemini API Exception" in w for w in warnings)

    def test_exception_does_not_propagate(self, tmp_path):
        img_path = _make_png(tmp_path)
        client = MagicMock()
        client.models.generate_content.side_effect = RuntimeError("boom")

        with patch("google.genai.Client", return_value=client):
            pipeline = ImageIngestionPipeline()

        # Must not raise — graceful degradation is the contract of extract_text.
        result = pipeline.extract_text(str(img_path))
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# ingest_image() dispatcher in ingest.py
# ---------------------------------------------------------------------------

class TestIngestImageDispatcher:

    def _pipeline_returning(self, text: str = "content", warnings: list = None) -> MagicMock:
        mock = MagicMock()
        mock.extract_text.return_value = {
            "source_file": "test.png",
            "content": text,
            "metadata": {
                "quality_signals": {
                    "extraction_warnings": list(warnings or [])
                }
            },
        }
        return mock

    def test_records_have_required_metadata_keys(self, tmp_path):
        img_path = _make_png(tmp_path)
        mock_pipeline = self._pipeline_returning("some text from image")

        with (
            patch("app.ingest_image.ImageIngestionPipeline", return_value=mock_pipeline),
            patch("app.ingest.embed_texts", return_value=[[0.1] * 8]),
        ):
            from app.ingest import ingest_image
            records = ingest_image(str(img_path), base_metadata={"doc_id": "abc-1"})

        assert len(records) >= 1
        md = records[0]["metadata"]
        assert md["source_type"] == "image_ocr"
        assert md["source_file"] == img_path.name
        assert "extraction_warnings" in md
        assert "chunk_index" in md
        assert md["doc_id"] == "abc-1"

    def test_warnings_present_in_every_record(self, tmp_path):
        img_path = _make_png(tmp_path)
        injected_warning = "MIME type could not be inferred; defaulting to image/jpeg."
        # Use enough words to guarantee multiple chunks at the default token limit.
        mock_pipeline = self._pipeline_returning(
            "word " * 600,
            warnings=[injected_warning],
        )

        with (
            patch("app.ingest_image.ImageIngestionPipeline", return_value=mock_pipeline),
            patch("app.ingest.embed_texts", side_effect=lambda chunks: [[0.0] * 8 for _ in chunks]),
        ):
            from app.ingest import ingest_image
            records = ingest_image(str(img_path))

        assert len(records) > 1, "Expected multiple chunks for warning propagation test"
        for record in records:
            assert injected_warning in record["metadata"]["extraction_warnings"]

    def test_empty_content_raises_value_error(self, tmp_path):
        img_path = _make_png(tmp_path)
        mock_pipeline = self._pipeline_returning(text="")

        with patch("app.ingest_image.ImageIngestionPipeline", return_value=mock_pipeline):
            from app.ingest import ingest_image
            with pytest.raises(ValueError, match="No OCR text extracted"):
                ingest_image(str(img_path))

    @pytest.mark.parametrize("suffix", [".png", ".jpg", ".jpeg", ".webp"])
    def test_ingest_by_extension_routes_image_formats(self, tmp_path, suffix):
        img_path = _make_png(tmp_path, name=f"img{suffix}")
        mock_pipeline = self._pipeline_returning("routed text")

        with (
            patch("app.ingest_image.ImageIngestionPipeline", return_value=mock_pipeline),
            patch("app.ingest.embed_texts", return_value=[[0.0] * 8]),
        ):
            from app.ingest import ingest_by_extension
            records = ingest_by_extension(str(img_path))

        assert records[0]["metadata"]["source_type"] == "image_ocr"

    def test_ingest_by_extension_rejects_unknown_format(self, tmp_path):
        txt_path = tmp_path / "data.csv"
        txt_path.write_text("a,b,c")

        from app.ingest import ingest_by_extension
        with pytest.raises(ValueError, match="Unsupported file format"):
            ingest_by_extension(str(txt_path))
