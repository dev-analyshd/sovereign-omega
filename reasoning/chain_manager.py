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
        # Stagger chain completion times so tau_ij drives meaningful consensus weight.
        # Consensus formula: weight = 1 - e^(-tau_ij / TAU_REF=5).
        # Reduced stagger (200ms × idx) keeps skill latency under 3s while still
        # providing meaningful tau spread (0–800ms) for consensus scoring.
        chain_origin = time.time()  # Record BEFORE sleep — common-origin clock
        await asyncio.sleep(chain_idx * 0.2)
        system = (
            f"You are reasoning chain {chain_idx + 1} of {self.N_CHAINS}. "
            "Reason independently. Do not hedge with other chains. "
            "Be specific and direct. End with: CONFIDENCE: 0.XX"
        )

        response, confidence = await self.llm.reason(query, context, system)
        elapsed_ms = (time.time() - chain_origin) * 1000  # Full time including stagger

        vector = self.embedder.embed(response)

        return {
            "chain_idx": chain_idx,
            "response": response,
            "confidence": confidence,
            "vector": vector,
            "elapsed_ms": elapsed_ms,
        }
