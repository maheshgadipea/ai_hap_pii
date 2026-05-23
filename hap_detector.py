"""HAP (Hate, Abuse, Profanity) detection using toxic-bert via detoxify."""

import logging
import warnings
import os

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from detoxify import Detoxify

_model = None


def get_model() -> Detoxify:
    global _model
    if _model is None:
        _model = Detoxify("original")
    return _model


def analyze(text: str, threshold: float = 0.5) -> dict:
    scores = {k: float(v) for k, v in get_model().predict(text).items()}
    flagged = {k: v for k, v in scores.items() if v >= threshold}
    return {
        "scores": scores,
        "flagged": flagged,
        "is_hap": len(flagged) > 0,
    }
