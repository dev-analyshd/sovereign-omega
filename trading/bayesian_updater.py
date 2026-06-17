import json
import os
from typing import Tuple


STATE_FILE = "data/bayesian_state.json"


def compute_kelly_fraction(p_win: float, avg_win: float, avg_loss: float, risk_cap: float = 0.02) -> float:
    if avg_loss <= 0:
        return 0.0
    b = avg_win / avg_loss
    f_star = (p_win * b - (1.0 - p_win)) / b
    return max(0.0, min(f_star, risk_cap))


def compute_expected_edge(p_win: float, avg_win: float, avg_loss: float) -> float:
    return p_win * avg_win - (1.0 - p_win) * avg_loss


class BayesianUpdater:
    """
    Beta-distribution Bayesian model over p_win per (symbol, strategy) pair.
    Updates α, β after each trade outcome.
    """

    def __init__(self):
        self.states = {}
        self._load()

    def _load(self):
        os.makedirs("data", exist_ok=True)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                raw = json.load(f)
            self.states = {tuple(k.split("|")): v for k, v in raw.items()}

    def _save(self):
        serializable = {f"{k[0]}|{k[1]}": v for k, v in self.states.items()}
        with open(STATE_FILE, "w") as f:
            json.dump(serializable, f)

    def _default_state(self):
        return {"alpha": 1.0, "beta": 1.0, "avg_win": 0.02, "avg_loss": 0.01, "p_win": 0.5, "n_trades": 0}

    def get_edge_params(self, symbol: str, strategy: str) -> Tuple[float, float, float, float]:
        key = (symbol, strategy)
        state = self.states.get(key, self._default_state())
        p_win = state["alpha"] / (state["alpha"] + state["beta"])
        kelly = compute_kelly_fraction(p_win, state["avg_win"], state["avg_loss"])
        return p_win, state["avg_win"], state["avg_loss"], kelly

    async def update_after_trade(self, symbol: str, strategy: str, won: bool, pnl_pct: float):
        key = (symbol, strategy)
        if key not in self.states:
            self.states[key] = self._default_state()

        state = self.states[key]
        n = state["n_trades"]

        if won:
            state["alpha"] += 1.0
            state["avg_win"] = (state["avg_win"] * n + abs(pnl_pct)) / (n + 1)
        else:
            state["beta"] += 1.0
            state["avg_loss"] = (state["avg_loss"] * n + abs(pnl_pct)) / (n + 1)

        state["p_win"] = state["alpha"] / (state["alpha"] + state["beta"])
        state["n_trades"] += 1
        self._save()
