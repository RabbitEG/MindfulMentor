from __future__ import annotations

"""
Utility to pre-download the Hugging Face model so runtime stays offline.
Usage:
  python download_models.py            # downloads to EmotionService/.models/...
  EMOTION_MODEL_DIR=/tmp/mm-models python download_models.py
"""

import os
from pathlib import Path

from huggingface_hub import snapshot_download

MODEL_ID = "facebook/bart-large-mnli"
DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / ".models" / MODEL_ID.replace("/", "--")


def download_model(model_id: str = MODEL_ID, target_dir: Path | None = None) -> Path:
    """
    Download the HF repo locally (no symlinks so the folder is self-contained).
    """
    dest = target_dir or Path(os.environ.get("EMOTION_MODEL_DIR", DEFAULT_MODEL_DIR))
    dest.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id=model_id,
        local_dir=str(dest),
        local_dir_use_symlinks=False,
        revision=None,
    )
    return dest


if __name__ == "__main__":
    path = download_model()
    print(f"Model cached at: {path}")
