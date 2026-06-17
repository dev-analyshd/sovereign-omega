import json
import math
import os

STATE_FILE = "data/social_moat_state.json"


class CredibilityMoat:
    """
    SC_moat(t) = Λ₀_social · ∏ᵢ (1 + η_social_i · ρᵢ)
    Grows with every coherent correct post. Never decreases.
    """

    LAMBDA_0_SOCIAL = 0.005

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                state = json.load(f)
            self.log_lambda_social = state["log_lambda_social"]
            self.n_posts = state["n_posts"]
        else:
            self.log_lambda_social = math.log(self.LAMBDA_0_SOCIAL)
            self.n_posts = 0
            self._save()

    async def accumulate(self, platform: str, psi: float):
        eta = {"twitter": 1.0, "discord": 0.7, "telegram": 0.6}.get(platform, 0.5)
        old = math.exp(self.log_lambda_social)
        increment = math.log(1 + eta * psi)
        self.log_lambda_social += increment
        self.n_posts += 1
        self._save()
        print(f"[SOCIAL MOAT] SC_moat: {old:.6f} → {self.get_current():.6f}")

    def get_current(self) -> float:
        return math.exp(self.log_lambda_social)

    def _save(self):
        with open(STATE_FILE, "w") as f:
            json.dump({"log_lambda_social": self.log_lambda_social, "n_posts": self.n_posts}, f)
