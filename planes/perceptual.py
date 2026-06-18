import math
from typing import Dict, List


class PerceptualPlane:
    """
    P(t) = H(X₁,...,Xₙ) / H_max  — frequency-based Shannon entropy.
    Values are quantized to 6 sig-figs to group similar readings;
    unique-value frequency drives diversity scoring.
    Alert if P(t) < 0.35 → floor to 0.0
    """

    ALERT_THRESHOLD = 0.35

    def compute(self, input_channels: Dict[str, List[float]]) -> float:
        all_values = []
        for channel_values in input_channels.values():
            all_values.extend(channel_values)

        if not all_values:
            return 0.0

        n = len(all_values)
        if n == 1:
            return 0.0

        entropy = self._shannon_entropy(all_values)
        h_max = math.log2(n)
        p = entropy / h_max if h_max > 0 else 0.0
        p = max(0.0, min(1.0, p))

        if p < self.ALERT_THRESHOLD:
            return 0.0

        return p

    def _shannon_entropy(self, values: List[float]) -> float:
        """Frequency-based Shannon entropy over quantized value buckets."""
        if not values:
            return 0.0
        n = len(values)

        counts: Dict[str, int] = {}
        for v in values:
            key = self._quantize(v)
            counts[key] = counts.get(key, 0) + 1

        probs = [c / n for c in counts.values()]
        return -sum(p * math.log2(p) for p in probs if p > 0)

    @staticmethod
    def _quantize(v: float) -> str:
        """Round to 4 significant figures so near-identical floats share a bucket."""
        if v == 0.0:
            return "0"
        magnitude = math.floor(math.log10(abs(v)))
        factor = 10 ** (4 - 1 - magnitude)
        rounded = round(v * factor) / factor
        return str(rounded)
