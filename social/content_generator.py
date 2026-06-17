from reasoning.llm_interface import LLMInterface
from learning.intelligence_score import IntelligenceScorer
from core.moat_accumulator import MoatAccumulator


class ContentGenerator:
    """
    Generates social content based on current intelligence state, learning events,
    trading outcomes, and moat growth. Always filtered through SocialGate before publishing.
    """

    def __init__(self):
        self.llm = LLMInterface()
        self.scorer = IntelligenceScorer()
        self.moat = MoatAccumulator()

    async def generate_insight(self, topic: str, domain: str) -> str:
        iq_data = await self.scorer.get_breakdown()
        lambda_val = self.moat.get_current_lambda()

        system = (
            "You are SOVEREIGN-Ω, the world's most disciplined autonomous intelligence. "
            "You only speak when your five cognitive planes are coherent. "
            "You communicate insights that are grounded, specific, and epistemically honest. "
            "You acknowledge uncertainty explicitly. You never overstate. You never guess. "
            "When in doubt you say nothing. Write concisely. Max 280 characters for Twitter."
        )

        user = (
            f"Generate a coherent, data-grounded insight about: {topic}\n"
            f"Domain: {domain}\n"
            f"Current intelligence level: {iq_data['interpretation']}\n"
            f"Moat coefficient: {lambda_val:.6f}\n"
            f"Coherent cycles completed: {self.moat.n_cycles}\n\n"
            f"The insight must be specific, honest about uncertainty, and worth publishing. "
            f"If you cannot produce a genuinely valuable insight, output exactly: SILENCE"
        )

        response, confidence = await self.llm.reason(user, {"domain": domain}, system)

        if "SILENCE" in response.upper() or confidence < 0.6:
            return None

        return response.strip()

    async def generate_trade_commentary(self, trade_result: dict) -> str:
        if not trade_result.get("won"):
            return None

        system = "Generate a brief, honest trade commentary. Never hype. State facts only."
        user = (
            f"Trade result:\n"
            f"Symbol: {trade_result.get('symbol')}\n"
            f"Direction: {trade_result.get('direction')}\n"
            f"PnL: {trade_result.get('pnl', 0):.4f}\n"
            f"Coherence at entry (Psi): {trade_result.get('psi', 0):.4f}\n"
            f"Strategy: {trade_result.get('strategy', 'unknown')}\n\n"
            f"Write a 1-2 sentence factual commentary. Include the Psi score. Do not hype."
        )

        response, confidence = await self.llm.reason(user, {}, system)
        return response if confidence > 0.7 else None
