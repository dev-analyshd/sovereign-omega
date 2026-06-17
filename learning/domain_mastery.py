import json
import math
import os
from datetime import datetime, timezone

STATE_FILE = "data/domain_mastery.json"
T_REF = 30 * 24 * 3600


class DomainMasteryEngine:
    """
    M(d, t) = tanh(Σ_{k∈domain d} CD(k,t) · KI(k,t))
    CD(k,t) = log(1 + N_tests_passed(k)) · (t - τ_created(k)) / t_ref
    KI(k,t) = (N_tests_passed(k) + 1) / (t - τ_created(k) + 1)
    """

    def __init__(self):
        self.domains = {}
        self._load()

    def _load(self):
        os.makedirs("data", exist_ok=True)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                self.domains = json.load(f)

    def _save(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.domains, f)

    async def update(self, domain: str, n_tests_passed: int = 1, created_at: float = None):
        now = datetime.now(timezone.utc).timestamp()
        if domain not in self.domains:
            self.domains[domain] = {
                "created_at": created_at or now,
                "tests_passed": 0,
                "mastery_score": 0.0,
                "knowledge_count": 0,
                "last_updated": now,
            }

        d = self.domains[domain]
        d["tests_passed"] += n_tests_passed
        d["knowledge_count"] += 1
        d["last_updated"] = now

        age = max(now - d["created_at"], 1)
        since_test = max(now - d["last_updated"], 1)
        n = d["tests_passed"]

        cd = math.log(1 + n) * age / T_REF
        ki = (n + 1) / since_test
        total_score = cd * ki

        d["mastery_score"] = float(math.tanh(total_score))
        self._save()

    def get_top_domain(self) -> dict:
        if not self.domains:
            return None
        top = max(self.domains.items(), key=lambda x: x[1]["mastery_score"])
        return {"domain": top[0], "score": top[1]["mastery_score"], "count": top[1]["knowledge_count"]}

    def get_all(self) -> list:
        return [
            {"domain": k, **v}
            for k, v in sorted(self.domains.items(), key=lambda x: x[1]["mastery_score"], reverse=True)
        ]
