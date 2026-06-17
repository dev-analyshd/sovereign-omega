import math
from core.coherence_engine import CoherenceEngine
from core.action_gate import ActionGate
from core.silence_protocol import SilenceProtocol
from core.moat_accumulator import MoatAccumulator


class SocialGate:
    """
    SC(t) = [Ψ_social(t) ≥ Δ_social] · quality(content) · e^(Λ·t)
    Δ_social = 0.70 — Rule 5: higher than trading because social errors live forever.
    Rule 13: silence is the default social state.
    """

    DELTA_SOCIAL = 0.70

    def __init__(self):
        self.coherence = CoherenceEngine()
        self.silence = SilenceProtocol()
        self.moat = MoatAccumulator()

    async def evaluate(self, content: str, context: dict, platform: str) -> dict:
        social_context = {**context, "task_type": "social", "platform": platform,
                          "input_channels": {"content": [len(content) / 500.0]},
                          "environmental_signals": {}}

        query = f"Is this social post coherent and worth publishing on {platform}? Content: {content[:200]}"
        cycle_id = f"social_{abs(hash(content)) % 1000000}"

        plane_scores = await self.coherence.compute_all_planes(query, social_context, cycle_id)
        psi = plane_scores["psi_total"]

        if psi < self.DELTA_SOCIAL:
            reason = self.silence.log_silence(cycle_id, psi, self.DELTA_SOCIAL, plane_scores)
            return {"approved": False, "reason": reason, "psi": psi}

        quality = self._assess_quality(content)
        lambda_val = self.moat.get_current_lambda()
        t_norm = self.moat.get_t_normalized()
        sc_value = quality * math.exp(lambda_val * t_norm)

        return {"approved": True, "psi": psi, "quality": quality, "sc_value": sc_value, "platform": platform}

    def _assess_quality(self, content: str) -> float:
        score = 0.5
        if len(content) > 30:
            score += 0.1
        if any(c.isdigit() for c in content):
            score += 0.1
        if "?" not in content:
            score += 0.1
        if len(content) < 500:
            score += 0.1
        if not any(w in content.lower() for w in ["definitely", "certainly", "always", "never"]):
            score += 0.1
        return min(score, 1.0)
