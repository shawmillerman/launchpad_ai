"""Regression tests for app/quality.py and quality-gate integration in ingest_by_extension."""
import pytest
from unittest.mock import MagicMock, patch

import app.quality
import app.ingest
from app.quality import apply_quality_gates, QualityResult, PASS, NEEDS_REVIEW


# ---------------------------------------------------------------------------
# apply_quality_gates — core gate logic
# ---------------------------------------------------------------------------

class TestApplyQualityGates:

    def test_clean_text_passes(self):
        text = "word " * 50
        result = apply_quality_gates(text, text, [])
        assert result.status == PASS
        assert result.passed is True
        assert result.reasons == []

    def test_returns_quality_result_instance(self):
        result = apply_quality_gates("hello world " * 20, "hello world " * 20, [])
        assert isinstance(result, QualityResult)

    def test_word_count_populated(self):
        text = "one two three four five"
        result = apply_quality_gates(text, text, [])
        assert result.word_count == 5

    def test_retention_ratio_populated(self):
        raw = "a" * 200
        cleaned = "a" * 100
        result = apply_quality_gates(raw, cleaned, [])
        assert abs(result.retention_ratio - 0.5) < 0.001

    # --- word count gate ---

    def test_below_min_word_count_fails(self):
        text = "only five words here"   # 4 words
        result = apply_quality_gates(text, text, [], min_word_count=30)
        assert result.status == NEEDS_REVIEW
        assert any("low_word_count" in r for r in result.reasons)

    def test_exactly_min_word_count_passes(self):
        text = " ".join(["word"] * 30)
        result = apply_quality_gates(text, text, [], min_word_count=30)
        assert result.passed

    def test_custom_min_word_count_respected(self):
        text = "one two three"
        assert apply_quality_gates(text, text, [], min_word_count=2).passed
        assert not apply_quality_gates(text, text, [], min_word_count=10).passed

    # --- retention ratio gate ---

    def test_below_min_retention_ratio_fails(self):
        raw = "a" * 1000
        cleaned = "a" * 10   # 1 % retention
        result = apply_quality_gates(raw, cleaned, [], min_word_count=0, min_retention_ratio=0.15)
        assert result.status == NEEDS_REVIEW
        assert any("low_retention_ratio" in r for r in result.reasons)

    def test_zero_length_raw_does_not_divide_by_zero(self):
        result = apply_quality_gates("", "", [], min_word_count=0)
        assert isinstance(result, QualityResult)

    def test_same_raw_and_cleaned_always_passes_ratio(self):
        text = "word " * 50
        result = apply_quality_gates(text, text, [], min_word_count=0)
        assert result.retention_ratio == pytest.approx(1.0)

    # --- extraction warnings forwarding ---

    def test_extraction_warnings_forwarded_as_reasons(self):
        text = "word " * 50
        warnings = ["vision_empty_response", "MIME type could not be inferred; defaulting to image/jpeg."]
        result = apply_quality_gates(text, text, warnings)
        assert result.status == NEEDS_REVIEW
        for w in warnings:
            assert w in result.reasons

    def test_empty_warnings_list_does_not_fail(self):
        text = "word " * 50
        result = apply_quality_gates(text, text, [])
        assert result.passed

    # --- multiple gates accumulate ---

    def test_multiple_failures_all_appear_in_reasons(self):
        raw = "a" * 1000
        cleaned = "word"   # short + low ratio
        result = apply_quality_gates(raw, cleaned, ["extraction_error"],
                                     min_word_count=5, min_retention_ratio=0.5)
        assert "low_word_count:1" in result.reasons
        assert any("low_retention_ratio" in r for r in result.reasons)
        assert "extraction_error" in result.reasons

    # --- reasons list is independent copy ---

    def test_reasons_list_is_not_shared(self):
        text = "word " * 50
        r1 = apply_quality_gates(text, text, ["w1"])
        r2 = apply_quality_gates(text, text, ["w2"])
        assert r1.reasons != r2.reasons


# ---------------------------------------------------------------------------
# ingest_by_extension — quality metadata wired into records
# ---------------------------------------------------------------------------

class TestIngestByExtensionQualityWiring:
    """Verify quality_status and quality_reasons appear in every record
    returned by ingest_by_extension for each supported format."""

    def _txt_file(self, tmp_path, content: str = "word " * 50) -> str:
        p = tmp_path / "doc.txt"
        p.write_text(content, encoding="utf-8")
        return str(p)

    def _png_file(self, tmp_path) -> str:
        from PIL import Image as PILImage
        p = tmp_path / "img.png"
        PILImage.new("RGB", (1, 1), color=(255, 255, 255)).save(str(p))
        return str(p)

    # -- txt --

    def test_txt_records_carry_quality_pass(self, tmp_path):
        path = self._txt_file(tmp_path)
        with patch("app.ingest_text_file.embed_texts", side_effect=lambda chunks: [[0.0] * 8 for _ in chunks]):
            records = app.ingest.ingest_by_extension(path)
        for r in records:
            assert r["metadata"]["quality_status"] == PASS
            assert r["metadata"]["quality_reasons"] == []

    def test_txt_short_content_tagged_needs_review(self, tmp_path):
        path = self._txt_file(tmp_path, content="hi")
        with patch("app.ingest_text_file.embed_texts", return_value=[[0.0] * 8]):
            records = app.ingest.ingest_by_extension(path)
        assert records[0]["metadata"]["quality_status"] == NEEDS_REVIEW
        assert any("low_word_count" in r for r in records[0]["metadata"]["quality_reasons"])

    def test_strict_quality_raises_on_needs_review(self, tmp_path):
        path = self._txt_file(tmp_path, content="hi")
        with patch("app.ingest_text_file.embed_texts", return_value=[[0.0] * 8]):
            with pytest.raises(ValueError, match="Quality gate failed"):
                app.ingest.ingest_by_extension(path, strict_quality=True)

    def test_strict_quality_does_not_raise_on_pass(self, tmp_path):
        path = self._txt_file(tmp_path)
        with patch("app.ingest_text_file.embed_texts", side_effect=lambda chunks: [[0.0] * 8 for _ in chunks]):
            records = app.ingest.ingest_by_extension(path, strict_quality=True)
        assert all(r["metadata"]["quality_status"] == PASS for r in records)

    def test_quality_metadata_in_every_record(self, tmp_path):
        # Multiple chunks — every single record must carry quality metadata.
        path = self._txt_file(tmp_path, content="word " * 600)
        with patch("app.ingest_text_file.embed_texts", side_effect=lambda chunks: [[0.0] * 8 for _ in chunks]):
            records = app.ingest.ingest_by_extension(path)
        assert len(records) > 1
        for r in records:
            assert "quality_status" in r["metadata"]
            assert "quality_reasons" in r["metadata"]

    # -- image --

    def test_image_extraction_warnings_flow_into_quality_reasons(self, tmp_path):
        path = self._png_file(tmp_path)
        injected_warning = "MIME type could not be inferred; defaulting to image/jpeg."
        mock_pipeline = MagicMock()
        mock_pipeline.extract_text.return_value = {
            "source_file": path,
            "content": "word " * 50,
            "metadata": {"quality_signals": {"extraction_warnings": [injected_warning]}},
        }
        with (
            patch("app.ingest_image.ImageIngestionPipeline", return_value=mock_pipeline),
            patch("app.ingest.embed_texts", side_effect=lambda chunks: [[0.0] * 8 for _ in chunks]),
        ):
            records = app.ingest.ingest_by_extension(path)

        for r in records:
            assert injected_warning in r["metadata"]["quality_reasons"]
            assert r["metadata"]["quality_status"] == NEEDS_REVIEW
