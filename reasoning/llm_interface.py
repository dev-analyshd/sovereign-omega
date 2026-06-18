import os
import re
import asyncio
import hashlib
from typing import Tuple

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class LLMInterface:
    """
    LLM reasoning interface.
    Priority: NVIDIA NIM → MiniMax → Anthropic (Claude) → Mock
    Extracts CONFIDENCE score from responses.
    """

    ANTHROPIC_MODEL = "claude-haiku-4-5"
    MINIMAX_MODEL = "MiniMax-Text-01"
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
    NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
    NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

    def __init__(self):
        self.provider = None
        self.client = None

        nvidia_key = os.getenv("NVIDIA_API_KEY")
        if nvidia_key and HTTPX_AVAILABLE:
            import asyncio
            self.provider = "nvidia"
            self.nvidia_key = nvidia_key
            self._nvidia_client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=10.0, read=45.0, write=10.0, pool=10.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
            self._nvidia_sem = asyncio.Semaphore(1)
            print("[LLM] Using NVIDIA NIM API (Llama-3.3-70B)")
            return

        minimax_key = os.getenv("MINIMAX_API_KEY")
        if minimax_key and HTTPX_AVAILABLE:
            self.provider = "minimax"
            self.minimax_key = minimax_key
            self.minimax_group_id = os.getenv("MINIMAX_GROUP_ID", "")
            print("[LLM] Using MiniMax API")
            return

        if ANTHROPIC_AVAILABLE:
            base_url = os.getenv("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")
            api_key = (
                os.getenv("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY")
            )
            if api_key:
                kwargs = {"api_key": api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                self.client = anthropic.AsyncAnthropic(**kwargs)
                self.provider = "anthropic"
                print("[LLM] Using Anthropic Claude")
                return

        print("[LLM] No API key found — using mock reasoning mode")
        self.provider = "mock"

    async def reason(
        self,
        query: str,
        context: dict,
        system_prompt: str = "",
    ) -> Tuple[str, float]:
        """Returns (response_text, confidence_score)."""

        if self.provider == "nvidia":
            return await self._reason_nvidia(query, context, system_prompt)
        elif self.provider == "minimax":
            return await self._reason_minimax(query, context, system_prompt)
        elif self.provider == "anthropic":
            return await self._reason_anthropic(query, context, system_prompt)
        else:
            return self._mock_response(query), self._mock_confidence(query)

    async def _reason_nvidia(
        self, query: str, context: dict, system_prompt: str
    ) -> Tuple[str, float]:
        system = system_prompt or (
            "You are SOVEREIGN-Ω, a disciplined autonomous reasoning agent. "
            "Reason carefully and end every response with: CONFIDENCE: 0.XX"
        )
        payload = {
            "model": self.NVIDIA_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.nvidia_key}",
            "Content-Type": "application/json",
        }
        for attempt in range(2):
            try:
                async with self._nvidia_sem:
                    resp = await self._nvidia_client.post(
                        f"{self.NVIDIA_BASE_URL}/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                confidence = self._extract_confidence(text)
                return text, confidence
            except Exception as e:
                if attempt == 0:
                    import asyncio
                    await asyncio.sleep(2)
                    continue
                print(f"[LLM NVIDIA] Error ({type(e).__name__}): {e} — falling back to mock")
                return self._mock_response(query), self._mock_confidence(query)

    async def _reason_minimax(
        self, query: str, context: dict, system_prompt: str
    ) -> Tuple[str, float]:
        system = system_prompt or (
            "You are SOVEREIGN-Ω, a disciplined autonomous reasoning agent. "
            "Reason carefully and end every response with: CONFIDENCE: 0.XX"
        )
        payload = {
            "model": self.MINIMAX_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.minimax_key}",
            "Content-Type": "application/json",
        }
        if self.minimax_group_id:
            url = f"{self.MINIMAX_BASE_URL}/text/chatcompletion_v2"
            params = {"GroupId": self.minimax_group_id}
        else:
            url = f"{self.MINIMAX_BASE_URL}/chat/completions"
            params = {}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, json=payload, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()
                if "choices" in data:
                    text = data["choices"][0]["message"]["content"]
                elif "reply" in data:
                    text = data["reply"]
                else:
                    text = str(data)
                confidence = self._extract_confidence(text)
                return text, confidence
        except Exception as e:
            print(f"[LLM MiniMax] Error: {e}")
            return self._mock_response(query), self._mock_confidence(query)

    async def _reason_anthropic(
        self, query: str, context: dict, system_prompt: str
    ) -> Tuple[str, float]:
        system = system_prompt or (
            "You are SOVEREIGN-Ω, a disciplined autonomous reasoning agent. "
            "You reason carefully and end every response with: CONFIDENCE: 0.XX (a decimal between 0.0 and 1.0)."
        )
        try:
            message = await self.client.messages.create(
                model=self.ANTHROPIC_MODEL,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": query}],
            )
            text = message.content[0].text
            confidence = self._extract_confidence(text)
            return text, confidence
        except Exception as e:
            print(f"[LLM Anthropic] Error: {e}")
            return self._mock_response(query), self._mock_confidence(query)

    def _extract_confidence(self, text: str) -> float:
        match = re.search(r"CONFIDENCE:\s*(0\.\d+|1\.0)", text)
        if match:
            return float(match.group(1))
        return 0.5

    def _mock_confidence(self, query: str) -> float:
        h = int(hashlib.sha256(query.encode()).hexdigest()[:8], 16)
        return 0.55 + (h % 100) / 1000.0

    def _mock_response(self, query: str) -> str:
        h = int(hashlib.sha256(query.encode()).hexdigest()[:8], 16)
        conf = 0.55 + (h % 100) / 1000.0
        templates = [
            f"The analysis of '{query[:60]}' reveals moderate uncertainty. Proceeding with caution. CONFIDENCE: {conf:.2f}",
            f"Evaluating '{query[:60]}': conditions appear neutral with some volatility signals. CONFIDENCE: {conf:.2f}",
            f"Reasoning through '{query[:60]}': insufficient data for high-confidence action. CONFIDENCE: {conf:.2f}",
            f"Assessment of '{query[:60]}': mixed signals detected across channels. CONFIDENCE: {conf:.2f}",
            f"Inference on '{query[:60]}': baseline conditions met, monitoring advised. CONFIDENCE: {conf:.2f}",
        ]
        idx = h % len(templates)
        return templates[idx]
