import os
import re
import asyncio
from typing import Tuple

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMInterface:
    """
    LLM reasoning interface. Uses Anthropic Claude via Replit AI Integration when available.
    Extracts CONFIDENCE score from responses.
    """

    DEFAULT_MODEL = "claude-haiku-4-5"

    def __init__(self):
        if ANTHROPIC_AVAILABLE:
            base_url = os.getenv("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")
            api_key = os.getenv("AI_INTEGRATIONS_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("[LLM] No API key found — using mock reasoning mode")
                self.client = None
            else:
                kwargs = {"api_key": api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                self.client = anthropic.AsyncAnthropic(**kwargs)
        else:
            self.client = None

    async def reason(
        self,
        query: str,
        context: dict,
        system_prompt: str = "",
    ) -> Tuple[str, float]:
        """Returns (response_text, confidence_score)."""

        if self.client is None:
            return self._mock_response(query), 0.6

        system = system_prompt or (
            "You are SOVEREIGN-Ω, a disciplined autonomous reasoning agent. "
            "You reason carefully and end every response with: CONFIDENCE: 0.XX (a decimal between 0.0 and 1.0)."
        )

        try:
            message = await self.client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": query}],
            )
            text = message.content[0].text
            confidence = self._extract_confidence(text)
            return text, confidence
        except Exception as e:
            print(f"[LLM] Error: {e}")
            return f"[LLM ERROR] {e}", 0.0

    def _extract_confidence(self, text: str) -> float:
        match = re.search(r"CONFIDENCE:\s*(0\.\d+|1\.0)", text)
        if match:
            return float(match.group(1))
        return 0.5

    def _mock_response(self, query: str) -> str:
        return f"[MOCK] Analysis of: {query[:80]}... CONFIDENCE: 0.60"
