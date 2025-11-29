from __future__ import annotations

import math
from typing import Dict, List

from Models import EmotionResult


POSITIVE_KEYWORDS = ["great", "good", "happy", "joy", "love", "excited"]
NEGATIVE_KEYWORDS = ["bad", "sad", "angry", "upset", "anxious", "fear"]
HIGH_INTENSITY_WORDS = ["furious", "panic", "terrified", "ecstatic", "devastated"]


def _keyword_score(text: str, keywords: List[str]) -> int:
    lowered = text.lower()
    return sum(1 for kw in keywords if kw in lowered)


def analyze_text(text: str) -> EmotionResult:
    """
    Lightweight rule-based fallback emotion detector.
    Replace with a HF model call later.
    """
    pos_score = _keyword_score(text, POSITIVE_KEYWORDS)
    neg_score = _keyword_score(text, NEGATIVE_KEYWORDS)
    high_intensity = _keyword_score(text, HIGH_INTENSITY_WORDS)

    if pos_score > neg_score:
        label = "positive"
        score = pos_score / max(pos_score + neg_score, 1)
    elif neg_score > pos_score:
        label = "negative"
        score = neg_score / max(pos_score + neg_score, 1)
    elif pos_score == neg_score == 0:
        label = "neutral"
        score = 0.5
    else:
        label = "mixed"
        score = 0.5

    intensity_value = "low"
    if high_intensity > 0 or max(pos_score, neg_score) >= 2:
        intensity_value = "high"
    elif max(pos_score, neg_score) == 1:
        intensity_value = "medium"

    dominant_emotions: Dict[str, float] = {}
    if label == "positive":
        dominant_emotions["joy"] = score
    elif label == "negative":
        dominant_emotions["anger"] = score

    normalized_score = float(min(1.0, math.ceil(score * 100) / 100))
    return EmotionResult(
        label=label,
        intensity=intensity_value,
        score=normalized_score,
        dominant_emotions=list(dominant_emotions.keys()),
    )
