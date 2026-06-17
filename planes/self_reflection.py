import math
import os
import json
import numpy as np
from typing import List


class SelfReflectionPlane:
    """
    S(t) = tanh(D(t) / D_ref)
    D(t) = (1/k) Σᵢ exp(-||q - vᵢ||² / 2σ²)
    Measures how familiar this query is relative to past queries.
    """

    D_REF = 0.5
    SIGMA = 1.0
    MEMORY_FILE = "data/self_reflection_memory.json"
    MAX_MEMORY = 500

    def __init__(self):
        self.past_embeddings: List[List[float]] = []
        self._load()

    def _load(self):
        os.makedirs("data", exist_ok=True)
        if os.path.exists(self.MEMORY_FILE):
            with open(self.MEMORY_FILE) as f:
                self.past_embeddings = json.load(f)

    _SAVE_EVERY = 20

    def _save(self):
        with open(self.MEMORY_FILE, "w") as f:
            json.dump(self.past_embeddings[-self.MAX_MEMORY :], f)

    def compute(self, query: str) -> float:
        query_vec = self._embed(query)

        if not self.past_embeddings:
            self.past_embeddings.append(query_vec)
            self._save()
            return 0.3

        q = np.array(query_vec)
        densities = []
        for vec in self.past_embeddings[-100:]:
            v = np.array(vec)
            if v.shape != q.shape:
                continue
            dist_sq = float(np.sum((q - v) ** 2))
            density = math.exp(-dist_sq / (2 * self.SIGMA ** 2))
            densities.append(density)

        d_t = sum(densities) / len(densities)
        s = math.tanh(d_t / self.D_REF)

        self.past_embeddings.append(query_vec)
        # Batch saves: write to disk every _SAVE_EVERY calls instead of every call
        if len(self.past_embeddings) % self._SAVE_EVERY == 0:
            self._save()

        return max(0.0, min(1.0, s))

    def _embed(self, text: str) -> List[float]:
        try:
            from reasoning.embedding_engine import EmbeddingEngine
            return EmbeddingEngine().embed(text)
        except Exception:
            return self._fallback_embed(text)

    def _fallback_embed(self, text: str) -> List[float]:
        import hashlib
        DIM = 384
        h1 = hashlib.sha256(text.encode()).digest()
        h2 = hashlib.sha256((text + "b").encode()).digest()
        h3 = hashlib.sha256((text + "c").encode()).digest()
        raw = list(h1) + list(h2) + list(h3)
        vec = [(b / 255.0) * 2 - 1 for b in raw[:DIM]]
        while len(vec) < DIM:
            vec.append(0.0)
        norm = math.sqrt(sum(x ** 2 for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec
