from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

from huggingface_hub import snapshot_download
from transformers import pipeline

from EmotionService.Models import EmotionResult

EMOTION_LABELS: List[str] = ["anxious", "angry", "sad", "tired", "neutral"]
MODEL_ID = "facebook/bart-large-mnli"
# Keep in sync with download_models.py default path
DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / ".models" / MODEL_ID.split("/")[-1]

def _resolve_model_dir() -> Path:
    """
    Locate a locally cached HF model without hitting the network.
    """
    configured_dir = Path(os.environ.get("EMOTION_MODEL_DIR", DEFAULT_MODEL_DIR))

    if configured_dir.exists():
        return configured_dir

    # If the model was downloaded to the default HF cache, reuse it.
    try:
        cached = Path(
            snapshot_download(
                repo_id=MODEL_ID,
                local_files_only=True,
            )
        )
        return cached
    except Exception as exc:  # pragma: no cover - fail fast with hint
        raise RuntimeError(
            f"Model not found at {configured_dir}. "
            "Run `python download_models.py` (or set EMOTION_MODEL_DIR to a pre-downloaded path)."
        ) from exc


_MODEL_DIR = _resolve_model_dir()
_classifier = pipeline(
    "zero-shot-classification",
    model=str(_MODEL_DIR),
    tokenizer=str(_MODEL_DIR),
    local_files_only=True,
)


def _scores_to_intensity(max_score: float) -> int:
    """
    Map confidence to discrete intensity (1-3).
    """
    if max_score >= 0.66:
        return 3
    if max_score >= 0.33:
        return 2
    return 1


def analyze_text(text: str) -> EmotionResult:
    """
    Use HF zero-shot classification to map text into predefined emotion labels.
    """
    result = _classifier(text, candidate_labels=EMOTION_LABELS, multi_label=True)
    label_scores: Dict[str, float] = {label: 0.0 for label in EMOTION_LABELS}

    for label, score in zip(result["labels"], result["scores"]):
        if label in label_scores:
            label_scores[label] = float(score)

    # normalize to top-1 dominant emotion
    dominant = max(label_scores.items(), key=lambda kv: kv[1])
    intensity = _scores_to_intensity(dominant[1])

    return EmotionResult(emotion=dominant[0], intensity=intensity, scores=label_scores)
