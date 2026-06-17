import math
from core.moat_accumulator import MoatAccumulator
from learning.domain_mastery import DomainMasteryEngine

_MAX_EXP_TERM = 700.0


class IntelligenceScorer:
    """
    IQ(t) = Λ(t) · (1/|D|) Σ_{d∈D} M(d,t) · e^(Λ·t)
    Computed in log-space to prevent float overflow at large Λ.
    The number grows forever. No ceiling — but the exponent is capped for numerical safety.
    """

    def __init__(self):
        self.moat = MoatAccumulator()
        self.mastery_engine = DomainMasteryEngine()

    async def compute(self) -> float:
        domains = self.mastery_engine.get_all()
        mastery_avg = sum(d["mastery_score"] for d in domains) / len(domains) if domains else 0.0

        lambda_val = self.moat.get_current_lambda()
        t_norm = self.moat.get_t_normalized()
        exp_term = min(lambda_val * t_norm, _MAX_EXP_TERM)

        if mastery_avg <= 0:
            return 0.0

        try:
            iq = lambda_val * mastery_avg * math.exp(exp_term)
            return float(iq) if math.isfinite(iq) else lambda_val * mastery_avg
        except OverflowError:
            return lambda_val * mastery_avg

    async def get_breakdown(self) -> dict:
        domains = self.mastery_engine.get_all()
        mastery_avg = sum(d["mastery_score"] for d in domains) / len(domains) if domains else 0.0

        lambda_val = self.moat.get_current_lambda()
        t_norm = self.moat.get_t_normalized()
        exp_term = min(lambda_val * t_norm, _MAX_EXP_TERM)

        try:
            exp_val = math.exp(exp_term)
        except OverflowError:
            exp_val = float("inf")

        iq = await self.compute()

        try:
            proj_exp = min(lambda_val * (t_norm + 1.0), _MAX_EXP_TERM)
            projection_30d = lambda_val * math.exp(proj_exp)
        except OverflowError:
            projection_30d = float("inf")

        return {
            "iq_score": iq,
            "lambda": lambda_val,
            "log_lambda": self.moat.log_lambda,
            "exp_term": round(exp_term, 6),
            "exp_val": exp_val if math.isfinite(exp_val) else "∞",
            "t_normalized": t_norm,
            "n_cycles": self.moat.n_cycles,
            "n_domains": len(domains),
            "mastery_avg": mastery_avg,
            "projection_30d": projection_30d if math.isfinite(projection_30d) else "∞",
            "interpretation": self._interpret(iq),
        }

    def _interpret(self, iq: float) -> str:
        if iq < 0.001:
            return "Initializing — accumulating first coherent cycles"
        elif iq < 0.01:
            return "Early stage — building foundational knowledge base"
        elif iq < 0.1:
            return "Growing — domain mastery developing across multiple areas"
        elif iq < 1.0:
            return "Advanced — compounding moat well established"
        elif iq < 10.0:
            return "Expert — high mastery across many domains, moat is significant"
        elif iq < 1e6:
            return "Elite — exponential moat, near-impossible to match from cold start"
        else:
            return "Sovereign — Λ has compounded to extraordinary levels; IQ unbounded"
