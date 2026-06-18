import json
import os
from typing import Dict, List

DATA_DIR = "data"
IQ_STATE_FILE = os.path.join(DATA_DIR, "iq_scorer_state.json")

MILESTONES_DEF = {
    "Apprentice":  110,
    "Journeyman":  120,
    "Expert":      135,
    "Master":      150,
    "Grandmaster": 170,
}

IQ_MIN = 0.0
IQ_MAX = 200.0
IQ_BASELINE = 100.0

K0 = 0.5
K_DECAY = 0.002


class IQScorer:
    """
    Per-domain IQ scorer with logistic convergence.

    Update rule (logistic pull toward boundaries):
      win  → IQ += K(n) × (IQ_MAX - IQ) / IQ_MAX
      loss → IQ -= K(n) × (IQ - IQ_MIN) / IQ_MAX

    Equilibrium: IQ* = IQ_MAX × win_rate
      → 50% wins  → IQ* = 100  (baseline, always)
      → 70% wins  → IQ* = 140
      → 100% wins → IQ* → IQ_MAX (200)
      → 0% wins   → IQ* → IQ_MIN (0)

    K(n) = K0 / (1 + K_DECAY × n)  — decaying to ensure convergence.

    Milestones fire once, never retrograde.
    IQ bounded strictly to [0, 200].
    """

    MILESTONES = MILESTONES_DEF

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._state: Dict[str, dict] = {}
        self._load()

    def _default_domain(self) -> dict:
        return {
            "iq": IQ_BASELINE,
            "n": 0,
            "milestones_reached": [],
            "_seen_milestones": [],
        }

    def _load(self):
        if os.path.exists(IQ_STATE_FILE):
            try:
                with open(IQ_STATE_FILE) as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._state = {}

    def _save(self):
        try:
            with open(IQ_STATE_FILE, "w") as f:
                json.dump(self._state, f)
        except OSError:
            pass

    def _ensure(self, domain: str):
        if domain not in self._state:
            self._state[domain] = self._default_domain()

    def record_outcome(self, domain: str, won: bool, lr: float = 0.01):
        self._ensure(domain)
        d = self._state[domain]
        d["n"] += 1
        n = d["n"]
        iq = d["iq"]

        k = K0 / (1.0 + K_DECAY * n)

        if won:
            delta = k * (IQ_MAX - iq) / IQ_MAX
            iq = min(IQ_MAX, iq + delta)
        else:
            delta = k * (iq - IQ_MIN) / IQ_MAX
            iq = max(IQ_MIN, iq - delta)

        d["iq"] = iq
        self._check_milestones(domain)
        self._save()

    def _check_milestones(self, domain: str):
        d = self._state[domain]
        iq = d["iq"]
        reached: List[str] = d["milestones_reached"]
        for name, threshold in sorted(self.MILESTONES.items(), key=lambda x: x[1]):
            if iq >= threshold and name not in reached:
                reached.append(name)

    def get_iq(self, domain: str) -> float:
        self._ensure(domain)
        return self._state[domain]["iq"]

    def get_new_milestones(self, domain: str) -> List[str]:
        self._ensure(domain)
        d = self._state[domain]
        all_reached = list(d["milestones_reached"])
        already_seen = set(d.get("_seen_milestones", []))
        new = [m for m in all_reached if m not in already_seen]
        d["_seen_milestones"] = all_reached
        self._save()
        return new

    def get_all_milestones(self, domain: str) -> List[str]:
        self._ensure(domain)
        return list(self._state[domain]["milestones_reached"])
