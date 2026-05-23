"""HAP (Hate, Abuse, Profanity) detection using local toxic-bert ONNX model."""

import os
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "models", "toxic-bert-onnx")
ONNX_PATH = os.path.join(MODEL_DIR, "onnx", "model.onnx")

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

_session: ort.InferenceSession | None = None
_tokenizer: AutoTokenizer | None = None


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def _get_session() -> ort.InferenceSession:
    global _session
    if _session is None:
        opts = ort.SessionOptions()
        opts.log_severity_level = 3  # suppress INFO/WARNING, show ERROR only
        _session = ort.InferenceSession(ONNX_PATH, sess_options=opts)
    return _session


def _get_tokenizer() -> AutoTokenizer:
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    return _tokenizer


def analyze(text: str, threshold: float = 0.5) -> dict:
    tokenizer = _get_tokenizer()
    session = _get_session()

    encoded = tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        max_length=512,
        padding=True,
    )

    # Only pass inputs the model actually expects
    expected_inputs = {inp.name for inp in session.get_inputs()}
    ort_inputs = {k: v for k, v in encoded.items() if k in expected_inputs}

    logits = session.run(None, ort_inputs)[0]
    scores = _sigmoid(logits[0])

    result = {label: float(score) for label, score in zip(LABELS, scores)}
    flagged = {k: v for k, v in result.items() if v >= threshold}

    return {
        "scores": result,
        "flagged": flagged,
        "is_hap": len(flagged) > 0,
    }
