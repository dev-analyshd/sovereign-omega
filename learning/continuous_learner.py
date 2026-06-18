import math
import os
from datetime import datetime, timezone

from learning.domain_mastery import DomainMasteryEngine
from learning.intelligence_score import IntelligenceScorer
from memory.dual_strand import DualStrandMemory
from memory.faiss_store import FAISSStore
from reasoning.embedding_engine import EmbeddingEngine
from core.moat_accumulator import MoatAccumulator


def _make_store():
    if os.getenv("TIMESCALE_URL"):
        try:
            from memory.timescale_store import TimescaleStore
            print("[LEARN] Using TimescaleDB vector store")
            return TimescaleStore()
        except Exception as e:
            print(f"[LEARN] TimescaleStore unavailable: {e} — falling back to FAISS")
    return FAISSStore()


class ContinuousLearner:
    """
    L_rate(t) = L₀ · e^(-λ_decay · t) · (1 + boost · SILENCE_density(t))
    More silence → learn faster. Gets smarter every cycle. Forever.
    """

    L_ZERO = 0.01
    LAMBDA_DECAY = 0.001
    SILENCE_BOOST = 2.0
    BOOST_MULTIPLIER = 0.5

    def __init__(self):
        self.mastery_engine = DomainMasteryEngine()
        self.intelligence_scorer = IntelligenceScorer()
        self.dual_strand = DualStrandMemory()
        self.store = _make_store()
        self.embedder = EmbeddingEngine()
        self.moat = MoatAccumulator()
        self.recent_silences = []
        self.t_start = datetime.now(timezone.utc).timestamp()

    def compute_learning_rate(self) -> float:
        elapsed = datetime.now(timezone.utc).timestamp() - self.t_start
        t_norm = elapsed / (30 * 24 * 3600)
        decay = self.L_ZERO * math.exp(-self.LAMBDA_DECAY * t_norm)
        slen = len(self.recent_silences[-100:])
        silence_density = sum(self.recent_silences[-100:]) / max(slen, 1)
        boost = 1.0 + self.BOOST_MULTIPLIER * self.SILENCE_BOOST * silence_density
        return decay * boost

    async def learn_from_cycle(
        self,
        cycle_id: str,
        query: str,
        action_output: str,
        gate_open: bool,
        domain: str,
        plane_scores: dict,
        outcome: dict = None,
    ):
        self.recent_silences.append(0 if gate_open else 1)
        learning_rate = self.compute_learning_rate()

        query_embedding = self.embedder.embed(query)
        meta = {
            "cycle_id": cycle_id,
            "domain": domain,
            "gate_open": gate_open,
            "psi": plane_scores.get("psi_total", 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        from memory.timescale_store import TimescaleStore
        if isinstance(self.store, TimescaleStore):
            await self.store.add(query_embedding, meta)
            store_total = await self.store.total()
        else:
            self.store.add(query_embedding, meta)
            store_total = self.store.total()

        if gate_open and action_output and outcome:
            await self._learn_from_action_outcome(query, action_output, outcome, domain, learning_rate)

        if not gate_open:
            await self._learn_from_silence(query, plane_scores, domain, learning_rate)

        await self.mastery_engine.update(domain)

        iq = await self.intelligence_scorer.compute()

        if len(self.recent_silences) % 100 == 0:
            await self._sync_to_pharos(iq)

        return {"learning_rate": learning_rate, "iq": iq, "memory_total": store_total}

    async def _learn_from_action_outcome(self, query, output, outcome, domain, learning_rate):
        if outcome.get("correct", True):
            text = f"Query: {query[:200]}. Approach: {output[:200]}. Result: successful."
            strand = self.dual_strand.encode(text, domain=domain)
            self._log_strand(strand)
        else:
            text = f"Query: {query[:200]}. This led to: {outcome.get('error', 'failure')}. Avoid this pattern."
            strand = self.dual_strand.encode(text, domain=f"{domain}_failures")
            self._log_strand(strand)

    async def _learn_from_silence(self, query, plane_scores, domain, learning_rate):
        planes = {k: plane_scores.get(k, 0) for k in ["p", "i", "c", "s", "w"]}
        weakest = min(planes, key=planes.get)
        lesson = f"In domain {domain}, {weakest} plane failed at {planes[weakest]:.4f}. Query: {query[:100]}"
        strand = self.dual_strand.encode(lesson, domain=f"{domain}_gaps")
        self._log_strand(strand)

    async def _sync_to_pharos(self, iq: float):
        try:
            from pharos.chain_client import PharosClient
            client = PharosClient()
            lambda_val = self.moat.get_current_lambda()
            await client.update_registry_moat(lambda_val, self.moat.n_cycles, iq)
            top = self.mastery_engine.get_top_domain()
            if top:
                await client.update_domain_mastery_on_chain(top["domain"], top["score"], top["count"])
        except Exception as e:
            print(f"[LEARNING] Pharos sync error: {e}")

    def _log_strand(self, strand: dict):
        print(f"[LEARN] Encoded strand: {strand['kf_hash'][:12]}... domain={strand['domain']}")
