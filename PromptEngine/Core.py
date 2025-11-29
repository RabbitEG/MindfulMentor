from __future__ import annotations

from pathlib import Path
from typing import Tuple

from Models import PromptRequest, PromptResponse

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "Templates"


def _load_template(intensity: str) -> Tuple[str, str]:
    """
    Select template by intensity; fallback to normal.
    """
    if intensity.lower() == "high":
        name = "HighIntensity.txt"
    else:
        name = "NormalIntensity.txt"
    path = TEMPLATES_DIR / name
    return path.read_text(encoding="utf-8"), name


def build_prompt(request: PromptRequest) -> PromptResponse:
    template_text, template_name = _load_template(request.intensity)
    prompt = template_text.format(
        user_text=request.user_text.strip(),
        label=request.label,
        intensity=request.intensity,
    )
    return PromptResponse(prompt=prompt, meta={"template": template_name})
