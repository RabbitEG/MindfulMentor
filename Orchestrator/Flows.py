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
from LlmGateway.Core import generate_text
from LlmGateway.Models import GenerateRequest
from PromptEngine.Core import build_prompt
from PromptEngine.Models import PromptRequest
from .Safety import hard_stop_message, is_safe
import datetime

LOG_FILE = BASE_DIR.parent / ".logs" / "orchestrator.log"

def _new_trace_id() -> str:
    return str(uuid.uuid4())


def _emotion_payload(emotion) -> Dict[str, Any]:
    dominant_score = float(emotion.scores.get(emotion.emotion, 0.0))
    return {
        "label": emotion.emotion,
        "intensity": emotion.intensity,
        "score": dominant_score,
        "scores": emotion.scores,
    }


def _error_response(code: str, detail: str, trace_id: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    _append_log(trace_id, status="error", detail=detail)
    return {
        "message": "Something went wrong. Please try again.",
        "trace_id": trace_id,
        "meta": meta,
        "emotion": None,
        "error": {"code": code, "detail": detail},
    }


def _append_log(trace_id: str, *, status: str, user_text: str | None = None, detail: str | None = None):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"\n--- Orchestrator @ {timestamp} ---\n")
            f.write(f"trace_id: {trace_id}\n")
            f.write(f"status: {status}\n")
            if user_text:
                f.write(f"user_text: {user_text}\n")
            if detail:
                f.write(f"detail: {detail}\n")
    except Exception:
        pass


def chat_flow(text: str) -> Dict[str, Any]:
    trace_id = _new_trace_id()
    base_meta: Dict[str, Any] = {"flow": "chat", "traceId": trace_id}

    if not text or not text.strip():
        return _error_response("invalid_input", "text is required", trace_id, base_meta)

    if not is_safe(text):
        message = hard_stop_message()
        _append_log(trace_id, status="blocked", user_text=text, detail="safety_block")
        return {
            "message": message,
            "reply": message,
            "trace_id": trace_id,
            "mode": "high_safety",
            "meta": {**base_meta, "safety": "blocked", "suggestedExercise": "grounding"},
            "emotion": None,
        }

    try:
        emotion = analyze_text(text)
        prompt = build_prompt(
            PromptRequest(
                text=text,
                emotion=emotion.emotion,
                intensity=emotion.intensity,
                context={"traceId": trace_id},
            )
        )
        mode = prompt.mode
        llm_response = generate_text(
            GenerateRequest(
                prompt=prompt.prompt,
            )
        )

        suggested = "grounding" if mode == "high_safety" else "thought_log"
        _append_log(trace_id, status="ok", user_text=text)
        return {
            "message": llm_response.text,
            "reply": llm_response.text,
            "trace_id": trace_id,
            "mode": mode,
            "meta": {
                **base_meta,
                "template": prompt.meta.get("template", "unknown"),
                "llmParams": prompt.llmParams,
                "llm_provider": llm_response.provider,
                "usage": llm_response.usage,
                "suggestedExercise": suggested,
            },
            "emotion": _emotion_payload(emotion),
            "suggestedExercise": suggested,
        }
    except Exception as exc:
        _append_log(trace_id, status="exception", user_text=text, detail=str(exc))
        return _error_response("internal_error", str(exc), trace_id, base_meta)


__all__ = ["chat_flow"]
