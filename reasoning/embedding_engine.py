import hashlib
import math
import os
from typing import List

_MODEL = None

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


def _get_model():
    global _MODEL
    if _MODEL is None and TRANSFORMERS_AVAILABLE:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


class EmbeddingEngine:
    """Embeds text into vectors. Uses sentence-transformers when available, fallback otherwise."""

    DIM = 384

    def embed(self, text: str) -> List[float]:
        model = _get_model()
        if model is not None:
            vec = model.encode(text, normalize_embeddings=True).tolist()
            return vec
        return self._fallback_embed(text)

    def _fallback_embed(self, text: str) -> List[float]:
        h1 = hashlib.sha256(text.encode()).digest()
        h2 = hashlib.sha256((text + "b").encode()).digest()
        h3 = hashlib.sha256((text + "c").encode()).digest()
        raw = list(h1) + list(h2) + list(h3)
        vec = [(b / 255.0) * 2 - 1 for b in raw[: self.DIM]]
        while len(vec) < self.DIM:
            vec.append(0.0)
        norm = math.sqrt(sum(x ** 2 for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec
