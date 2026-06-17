import math
import numpy as np
from typing import List


class InferentialPlane:
    """
    I(t) = 1 - (σ_R / (μ_R + 0.001))
    Contradiction (cosine < -0.3 between any two chains) → I(t) = 0.0 hard stop
    Rule 10: No averaging. Hard stop.
    """

    CONTRADICTION_THRESHOLD = -0.3

    def compute(self, reasoning_chains: List[dict]) -> float:
        if not reasoning_chains:
            return 0.5

        confidences = [c.get("confidence", 0.5) for c in reasoning_chains]
        vectors = [c.get("vector") for c in reasoning_chains if c.get("vector") is not None]

        if len(vectors) >= 2:
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    cosine = self._cosine_similarity(vectors[i], vectors[j])
                    if cosine < self.CONTRADICTION_THRESHOLD:
                        return 0.0

        if not confidences:
            return 0.5

        mu = sum(confidences) / len(confidences)
        variance = sum((c - mu) ** 2 for c in confidences) / len(confidences)
        sigma = math.sqrt(variance)

        i_score = 1.0 - (sigma / (mu + 0.001))
        return max(0.0, min(1.0, i_score))

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        va = np.array(a, dtype=float)
        vb = np.array(b, dtype=float)
        na = np.linalg.norm(va)
        nb = np.linalg.norm(vb)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(va, vb) / (na * nb))
