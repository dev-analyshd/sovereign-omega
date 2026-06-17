import json
import math
import os
from datetime import datetime, timezone

STATE_FILE = "data/moat_state.json"


class MoatAccumulator:
    """
    Compounding Moat in log-space for numerical stability.
    log(Λ(t)) = log(Λ₀) + Σᵢ₌₁ᴺ log(1 + ηᵢ · ρᵢ)
    Λ₀ = 0.01. Λ never decreases. Ever.
    """

    LAMBDA_0 = 0.01

    def __init__(self):
        self._load_or_init()

    def _load_or_init(self):
        os.makedirs("data", exist_ok=True)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                state = json.load(f)
            self.log_lambda = state["log_lambda"]
            self.n_cycles = state["n_cycles"]
            self.t_start = state["t_start"]
        else:
            self.log_lambda = math.log(self.LAMBDA_0)
            self.n_cycles = 0
            self.t_start = datetime.now(timezone.utc).timestamp()
            self._save()

    def accumulate(self, eta_i: float, rho_i: float, cycle_id: str = ""):
        """Accumulate moat. Λ can only grow."""
        if eta_i <= 0 or rho_i <= 0:
            return
        increment = math.log(1 + eta_i * rho_i)
        old_log = self.log_lambda
        self.log_lambda = old_log + increment
        self.n_cycles += 1
        self._save()

    def get_current_lambda(self) -> float:
        return math.exp(self.log_lambda)

    def get_t_normalized(self) -> float:
        elapsed = datetime.now(timezone.utc).timestamp() - self.t_start
        return elapsed / (30 * 24 * 3600)

    def _save(self):
        with open(STATE_FILE, "w") as f:
            json.dump(
                {
                    "log_lambda": self.log_lambda,
                    "n_cycles": self.n_cycles,
                    "t_start": self.t_start,
                },
                f,
            )
