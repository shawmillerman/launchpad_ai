"""Domain-agnostic quality gates for text extracted from any source.

All gates are checked in order and failures accumulate into `reasons`.
The final status is PASS if no gates fail, NEEDS_REVIEW otherwise.

Environment variables (all optional; defaults shown):
  MIN_WORD_COUNT=30        — minimum words in cleaned text
  MIN_RETENTION_RATIO=0.15 — minimum ratio of cleaned/raw character length
"""
import os
from dataclasses import dataclass, field
from typing import List

PASS = "PASS"
NEEDS_REVIEW = "NEEDS_REVIEW"

_DEFAULT_MIN_WORDS = int(os.getenv("MIN_WORD_COUNT", "30"))
_DEFAULT_MIN_RATIO = float(os.getenv("MIN_RETENTION_RATIO", "0.15"))


@dataclass
class QualityResult:
    """Outcome of a quality-gate check."""

    status: str                          # PASS | NEEDS_REVIEW
    reasons: List[str] = field(default_factory=list)
    word_count: int = 0
    retention_ratio: float = 0.0

    @property
    def passed(self) -> bool:
        return self.status == PASS


def apply_quality_gates(
    raw_text: str,
    cleaned_text: str,
    extraction_warnings: List[str],
    min_word_count: int = _DEFAULT_MIN_WORDS,
    min_retention_ratio: float = _DEFAULT_MIN_RATIO,
) -> QualityResult:
    """Evaluate text quality before expensive downstream processing.

    Args:
        raw_text: Text as extracted directly from the source (pre-cleaning).
        cleaned_text: Text after any normalisation/boilerplate removal.
            Pass the same string as ``raw_text`` when no cleaning step exists.
        extraction_warnings: Warning codes emitted during extraction (e.g.
            from OCR or format parsing).  Any non-empty list of warnings is
            forwarded to the result as additional reasons.
        min_word_count: Minimum number of words in ``cleaned_text``.
        min_retention_ratio: Minimum ratio of ``len(cleaned_text)`` to
            ``len(raw_text)``.  Catches cases where boilerplate removal
            stripped most of the content.

    Returns:
        :class:`QualityResult` with status PASS or NEEDS_REVIEW and the
        accumulated list of reasons.
    """
    reasons: List[str] = []

    word_count = len(cleaned_text.split())
    retention_ratio = len(cleaned_text) / max(len(raw_text), 1)

    if word_count < min_word_count:
        reasons.append(f"low_word_count:{word_count}")

    if retention_ratio < min_retention_ratio:
        reasons.append(f"low_retention_ratio:{retention_ratio:.2f}")

    if extraction_warnings:
        reasons.extend(extraction_warnings)

    status = NEEDS_REVIEW if reasons else PASS
    return QualityResult(
        status=status,
        reasons=list(reasons),
        word_count=word_count,
        retention_ratio=retention_ratio,
    )
