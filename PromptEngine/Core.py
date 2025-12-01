from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from .Models import PromptRequest, PromptResponse

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "Templates"

DEFAULT_LLM_PARAMS: Dict[str, Dict[str, float]] = {
    "normal": {"temperature": 0.4, "maxTokens": 320},
    "high_safety": {"temperature": 0.2, "maxTokens": 256},
}


def _normalize_intensity(intensity: int) -> int:
    try:
        value = int(intensity)
    except (TypeError, ValueError):
        return 1
    return max(1, value)


def _select_mode(intensity: int) -> str:
    """
    Use high_safety mode for intensity strictly above 3; otherwise normal.
    """
    return "high_safety" if intensity > 3 else "normal"


def _template_name(mode: str) -> str:
    return "HighIntensity.txt" if mode == "high_safety" else "NormalIntensity.txt"


def _load_template(name: str) -> Tuple[str, str]:
    path = TEMPLATES_DIR / name
    return path.read_text(encoding="utf-8"), name


def _context_block(context: Dict[str, str]) -> str:
    if not context:
        return "Context: none provided."
    lines = [f"- {k}: {v}" for k, v in context.items()]
    return "Context:\n" + "\n".join(lines)


def build_prompt(request: PromptRequest) -> PromptResponse:
    intensity = _normalize_intensity(request.intensity)
    mode = _select_mode(intensity)
    template_text, template_name = _load_template(_template_name(mode))

    prompt = template_text.format(
        user_text=request.text.strip(),
        emotion=request.emotion,
        intensity=intensity,
        context=_context_block(request.context or {}),
    ).strip()

    llm_params = DEFAULT_LLM_PARAMS.get(mode, DEFAULT_LLM_PARAMS["normal"])

    return PromptResponse(
        prompt=prompt,
        mode=mode,
        llmParams=llm_params,
        meta={"template": template_name},
    )
