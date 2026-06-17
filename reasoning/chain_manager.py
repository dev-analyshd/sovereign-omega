import asyncio
import time
from typing import List, Dict
from reasoning.llm_interface import LLMInterface
from reasoning.embedding_engine import EmbeddingEngine


class ChainManager:
    """
    Runs N independent reasoning chains in parallel.
    Each chain produces a response + confidence + embedding vector.
    Results feed into InferentialPlane and ConsensusPlane.
    """

    N_CHAINS = 5

    def __init__(self):
        self.llm = LLMInterface()
        self.embedder = EmbeddingEngine()

    async def run_chains(self, query: str, context: dict) -> List[Dict]:
        tasks = [self._run_single_chain(query, context, i) for i in range(self.N_CHAINS)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        chains = [r for r in results if isinstance(r, dict)]
        return chains

    async def _run_single_chain(self, query: str, context: dict, chain_idx: int) -> Dict:
        start = time.time()
        system = (
            f"You are reasoning chain {chain_idx + 1} of {self.N_CHAINS}. "
            "Reason independently. Do not hedge with other chains. "
            "Be specific and direct. End with: CONFIDENCE: 0.XX"
        )

        response, confidence = await self.llm.reason(query, context, system)
        elapsed_ms = (time.time() - start) * 1000

        vector = self.embedder.embed(response)

        return {
            "chain_idx": chain_idx,
            "response": response,
            "confidence": confidence,
            "vector": vector,
            "elapsed_ms": elapsed_ms,
        }
