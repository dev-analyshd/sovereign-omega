import math
from typing import Dict, List


class PerceptualPlane:
    """
    P(t) = H(X₁,...,Xₙ) / H_max
    H(X) = -Σᵢ p(xᵢ)·log₂(p(xᵢ))
    Alert if P(t) < 0.35 → floor to 0.0
    """

    ALERT_THRESHOLD = 0.35

    def compute(self, input_channels: Dict[str, List[float]]) -> float:
        all_values = []
        for channel_values in input_channels.values():
            all_values.extend(channel_values)

        if not all_values:
            return 0.0

        entropy = self._shannon_entropy(all_values)
        n = len(all_values)
        h_max = math.log2(n) if n > 1 else 1.0
        p = entropy / h_max if h_max > 0 else 0.0
        p = max(0.0, min(1.0, p))

        if p < self.ALERT_THRESHOLD:
            return 0.0

        return p

    def _shannon_entropy(self, values: List[float]) -> float:
        if not values:
            return 0.0
        total = sum(abs(v) for v in values)
        if total == 0:
            return 0.0
        probs = [abs(v) / total for v in values if v != 0]
        return -sum(p * math.log2(p) for p in probs if p > 0)
