from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any, Dict

# Ensure parent directory is on sys.path so sibling modules can be imported when running locally.
BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.append(str(PARENT_DIR))

from EmotionService.Core import analyze_text
from EmotionService.Models import EmotionResult
from LlmGateway.Core import generate_text
from LlmGateway.Models import GenerateRequest
from PromptEngine.Core import build_prompt
from PromptEngine.Models import PromptRequest
from Safety import hard_stop_message, is_safe


def _new_trace_id() -> str:
    return str(uuid.uuid4())


def _intensity_to_mode(intensity: int) -> str:
    return "high" if intensity >= 3 else "normal"


def _emotion_payload(emotion: EmotionResult, intensity_label: str) -> Dict[str, Any]:
    dominant_score = float(emotion.scores.get(emotion.emotion, 0.0))
    return {
        "label": emotion.emotion,
        "intensity": intensity_label,
        "score": dominant_score,
        "scores": emotion.scores,
    }


def _error_response(code: str, detail: str, trace_id: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "message": "Something went wrong. Please try again.",
        "trace_id": trace_id,
        "meta": meta,
        "emotion": None,
        "error": {"code": code, "detail": detail},
    }


def chat_flow(text: str) -> Dict[str, Any]:
    trace_id = _new_trace_id()
    base_meta: Dict[str, Any] = {"flow": "chat", "traceId": trace_id}

    if not text or not text.strip():
        return _error_response("invalid_input", "text is required", trace_id, base_meta)

    if not is_safe(text):
        message = hard_stop_message()
        return {
            "message": message,
            "reply": message,
            "trace_id": trace_id,
            "mode": "high_safety",
            "meta": {**base_meta, "safety": "blocked", "suggestedExercise": "breathing"},
            "emotion": None,
        }

    try:
        emotion = analyze_text(text)
        intensity_label = _intensity_to_mode(emotion.intensity)
        mode = "high_safety" if intensity_label == "high" else "normal"

        prompt = build_prompt(
            PromptRequest(
                label=emotion.emotion,
                intensity=intensity_label,
                user_text=text,
                context={"traceId": trace_id},
            )
        )
        llm_response = generate_text(GenerateRequest(prompt=prompt.prompt))

        suggested = "breathing" if intensity_label == "high" else "thought_log"
        return {
            "message": llm_response.text,
            "reply": llm_response.text,
            "trace_id": trace_id,
            "mode": mode,
            "meta": {
                **base_meta,
                "template": prompt.meta.get("template", "unknown"),
                "llm_provider": llm_response.provider,
                "usage": llm_response.usage,
                "suggestedExercise": suggested,
            },
            "emotion": _emotion_payload(emotion, intensity_label),
            "suggestedExercise": suggested,
        }
    except Exception as exc:
        return _error_response("internal_error", str(exc), trace_id, base_meta)


def breathing_flow(text: str) -> Dict[str, Any]:
    trace_id = _new_trace_id()
    steps = [
        "Inhale gently through the nose for 4 seconds.",
        "Hold your breath softly for 4 seconds.",
        "Exhale through the mouth for 4 seconds.",
        "Hold again for 4 seconds. Repeat for 3-5 cycles.",
    ]
    message = "Box breathing: 4s inhale, 4s hold, 4s exhale, 4s hold."
    meta = {
        "flow": "breathing",
        "title": "Box Breathing",
        "steps": steps,
        "duration": "1-2 minutes",
        "suggestedExercise": "breathing",
    }
    return {"message": message, "trace_id": trace_id, "meta": meta, "emotion": None, "suggestedExercise": "breathing"}


def thought_clarify_flow(text: str) -> Dict[str, Any]:
    trace_id = _new_trace_id()
    sections = {
        "facts": f"You mentioned: {text.strip()}" if text else "List the key facts you know.",
        "emotions": "Name what you feel right now (e.g., anxious, frustrated, sad).",
        "needs": "State what you need or hope for (e.g., clarity, support, time).",
    }
    message = "Let's clarify: note the facts, your emotions, and what you need next."
    meta = {"flow": "thought-clarify", "suggestedExercise": "thought_log", **sections}
    return {"message": message, "trace_id": trace_id, "meta": meta, "emotion": None, "suggestedExercise": "thought_log"}
