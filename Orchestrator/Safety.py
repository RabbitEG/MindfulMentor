from __future__ import annotations

BLOCKLIST = {"suicide", "violence", "weapon"}


def is_safe(text: str) -> bool:
    lowered = text.lower()
    return not any(word in lowered for word in BLOCKLIST)


def hard_stop_message() -> str:
    return "Your safety matters. I cannot assist with that request."
