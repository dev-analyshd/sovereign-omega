import math
from core.moat_accumulator import MoatAccumulator
from learning.domain_mastery import DomainMasteryEngine


class IntelligenceScorer:
    """
    IQ(t) = Λ(t) · (1/|D|) Σ_{d∈D} M(d,t) · e^(Λ·t)
    This number grows forever. No ceiling.
    """

    def __init__(self):
        self.moat = MoatAccumulator()
        self.mastery_engine = DomainMasteryEngine()

    async def compute(self) -> float:
        domains = self.mastery_engine.get_all()
        if not domains:
            mastery_avg = 0.0
        else:
            mastery_avg = sum(d["mastery_score"] for d in domains) / len(domains)

        lambda_val = self.moat.get_current_lambda()
        t_norm = self.moat.get_t_normalized()
        iq = lambda_val * mastery_avg * math.exp(lambda_val * t_norm)
        return float(iq)

    async def get_breakdown(self) -> dict:
        iq = await self.compute()
        domains = self.mastery_engine.get_all()
        lambda_val = self.moat.get_current_lambda()
        t_norm = self.moat.get_t_normalized()

        return {
            "iq_score": iq,
            "lambda": lambda_val,
            "exp_term": math.exp(lambda_val * t_norm),
            "t_normalized": t_norm,
            "n_cycles": self.moat.n_cycles,
            "n_domains": len(domains),
            "projection_30d": lambda_val * math.exp(lambda_val * (t_norm + 1.0)),
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
        else:
            return "Elite — exponential moat, near-impossible to match from cold start"
