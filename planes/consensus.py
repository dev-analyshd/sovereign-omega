import math
import numpy as np
from typing import List


class ConsensusPlane:
    """
    C(t) = (1/k(k-1)) · Σᵢ≠ⱼ [sim(Rᵢ,Rⱼ) · (1 - e^(-τᵢⱼ/τ_ref))]
    Slow independent convergence → higher score.
    Fast convergence → lower score.
    """

    TAU_REF = 5.0

    def compute(self, reasoning_chains: List[dict]) -> float:
        k = len(reasoning_chains)
        if k < 2:
            return 0.5

        vectors = [c.get("vector") for c in reasoning_chains if c.get("vector") is not None]
        times = [c.get("elapsed_ms", 1000.0) for c in reasoning_chains]

        if len(vectors) < 2:
            return 0.5

        total = 0.0
        pairs = 0
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                sim = self._cosine_similarity(vectors[i], vectors[j])
                tau_ij = abs(times[i] - times[j]) / 1000.0
                weight = 1.0 - math.exp(-tau_ij / self.TAU_REF)
                total += sim * weight
                pairs += 1

        return max(0.0, min(1.0, total / pairs)) if pairs > 0 else 0.5

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        va = np.array(a, dtype=float)
        vb = np.array(b, dtype=float)
        na = np.linalg.norm(va)
        nb = np.linalg.norm(vb)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(va, vb) / (na * nb))
