from __future__ import annotations

"""
Utility to pre-download the Hugging Face model so runtime stays offline.
This version downloads *only* the PyTorch + tokenizer files, 
avoiding huge Flax/Rust snapshots and wrong directory structures.
"""

import os
from pathlib import Path
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)


MODEL_ID = "facebook/bart-large-mnli"

# This directory uses a clean, correct HF-style name
DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / ".models" / MODEL_ID.split("/")[-1]


def download_model(model_id: str = MODEL_ID, target_dir: Path | None = None) -> Path:
    """
    Download only needed model files (PyTorch + tokenizer), 
    not the full HF snapshot (~1.6 GB instead of 6 GB).
    """
    dest = target_dir or Path(os.environ.get("EMOTION_MODEL_DIR", DEFAULT_MODEL_DIR))
    dest.mkdir(parents=True, exist_ok=True)

    # Download PyTorch model
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id,
        from_flax=False,          # don't download Flax weights
        trust_remote_code=False,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    model.save_pretrained(dest)
    tokenizer.save_pretrained(dest)

    return dest


if __name__ == "__main__":
    path = download_model()
    print(f"Model cached at: {path}")
