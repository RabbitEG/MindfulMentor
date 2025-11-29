from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Dict

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
from Safety import is_safe, hard_stop_message


def _new_trace_id() -> str:
    return str(uuid.uuid4())


def chat_flow(text: str) -> Dict:
    if not is_safe(text):
        return {
            "message": hard_stop_message(),
            "trace_id": _new_trace_id(),
            "meta": {"flow": "chat", "safety": "blocked"},
            "emotion": None,
        }

    emotion = analyze_text(text)
    prompt = build_prompt(
        PromptRequest(label=emotion.label, intensity=emotion.intensity, user_text=text)
    )
    llm_response = generate_text(GenerateRequest(prompt=prompt.prompt, provider="mock"))

    return {
        "message": llm_response.text,
        "trace_id": _new_trace_id(),
        "meta": {"flow": "chat", "template": prompt.meta.get("template", "unknown")},
        "emotion": emotion.dict(),
    }


def breathing_flow(text: str) -> Dict:
    # Simple scripted breathing guidance
    guidance = (
        "Let's do a box breathing together: inhale 4s, hold 4s, exhale 4s, hold 4s. "
        "Repeat for 3-5 cycles while noticing bodily sensations."
    )
    return {
        "message": guidance,
        "trace_id": _new_trace_id(),
        "meta": {"flow": "breathing"},
        "emotion": None,
    }


def thought_clarify_flow(text: str) -> Dict:
    prompt = (
        "I hear you. To clarify your thoughts, consider: "
        "1) What matters most right now? 2) What is in your control? "
        "3) What small next step feels doable?"
    )
    return {
        "message": prompt,
        "trace_id": _new_trace_id(),
        "meta": {"flow": "thought-clarify"},
        "emotion": None,
    }
