from __future__ import annotations

from typing import Dict, List

from transformers import pipeline

from Models import EmotionResult

EMOTION_LABELS: List[str] = ["anxious", "angry", "sad", "tired", "neutral"]


_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
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
