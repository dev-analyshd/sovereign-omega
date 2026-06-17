import hashlib
import math
from typing import Dict
import numpy as np


class DualStrandMemory:
    """
    Dual-strand memory: K⁺ (positive embedding) and K⁻ (negative/inverse).
    Knowledge fingerprint hash prevents duplicate encoding.
    """

    DIM = 256

    def encode(self, text: str, domain: str = "general") -> Dict:
        kf_hash = hashlib.sha256(text.encode()).hexdigest()

        k_positive = self._embed(text)
        k_negative = self._embed(f"NOT: {text}")

        return {
            "kf_hash": kf_hash,
            "k_positive": k_positive,
            "k_negative": k_negative,
            "source_text": text[:500],
            "domain": domain,
        }

    def test_against_new_info(self, strand: Dict, new_text: str) -> str:
        new_vec = np.array(self._embed(new_text))
        k_pos = np.array(strand["k_positive"])
        k_neg = np.array(strand["k_negative"])

        cos_pos = self._cosine(new_vec, k_pos)
        cos_neg = self._cosine(new_vec, k_neg)

        if cos_pos > 0.7:
            return "confirmed"
        elif cos_neg > 0.7 or cos_pos < -0.3:
            return "contradiction"
        else:
            return "neutral"

    def _embed(self, text: str):
        h = hashlib.sha256(text.encode()).digest()
        h2 = hashlib.sha256((text + "salt2").encode()).digest()
        raw = list(h) + list(h2)
        vec = [(b / 255.0) * 2 - 1 for b in raw[: self.DIM]]
        while len(vec) < self.DIM:
            vec.append(0.0)
        norm = math.sqrt(sum(x ** 2 for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))
