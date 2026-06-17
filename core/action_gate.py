class ActionGate:
    """
    Δ(t) = Δ_base · (1 + κ·V(t)) · (1 + σ_n·N(t))
    Δ_base=0.65, κ=0.20, σ_n=0.15
    Max possible: 0.897
    """

    DELTA_BASE = 0.65
    KAPPA = 0.20
    SIGMA_N = 0.15
    MAX_DELTA = 0.897

    def compute_threshold(self, volatility: float = 0.0, novelty: float = 0.0) -> float:
        v = max(0.0, min(1.0, volatility))
        n = max(0.0, min(1.0, novelty))
        delta = self.DELTA_BASE * (1 + self.KAPPA * v) * (1 + self.SIGMA_N * n)
        return min(delta, self.MAX_DELTA)

    def is_open(self, psi: float, delta: float) -> bool:
        return psi >= delta
