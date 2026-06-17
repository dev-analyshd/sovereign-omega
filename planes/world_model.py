import statistics
from typing import Dict


class WorldModelPlane:
    """
    W(t) = 1 - (1/m) Σⱼ clamp(|eⱼ - μ_env|/σ_env, 0, 1)
    Any z-score > 3.0 → W(t) = 0.0 immediately. Rule 11.
    """

    Z_SCORE_LIMIT = 3.0
    HISTORY_SIZE = 200

    def __init__(self):
        self.history: Dict[str, list] = {}

    def compute(self, env_signals: Dict[str, float]) -> float:
        if not env_signals:
            return 0.7

        for key, val in env_signals.items():
            if key not in self.history:
                self.history[key] = []
            self.history[key].append(val)
            if len(self.history[key]) > self.HISTORY_SIZE:
                self.history[key].pop(0)

        deviations = []
        for key, val in env_signals.items():
            hist = self.history.get(key, [val])
            if len(hist) < 3:
                deviations.append(0.0)
                continue

            mu = statistics.mean(hist)
            try:
                sigma = statistics.stdev(hist)
            except statistics.StatisticsError:
                sigma = 0.0

            if sigma < 1e-9:
                deviations.append(0.0)
                continue

            z = abs(val - mu) / sigma

            if z > self.Z_SCORE_LIMIT:
                return 0.0

            deviations.append(min(z / self.Z_SCORE_LIMIT, 1.0))

        if not deviations:
            return 0.7

        w = 1.0 - (sum(deviations) / len(deviations))
        return max(0.0, min(1.0, w))
