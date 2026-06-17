import math
import uuid
from planes.perceptual import PerceptualPlane
from planes.inferential import InferentialPlane
from planes.consensus import ConsensusPlane
from planes.self_reflection import SelfReflectionPlane
from planes.world_model import WorldModelPlane
from core.action_gate import ActionGate


class CoherenceEngine:
    """
    Ψ(t) = 0.25·P(t) + 0.30·I(t) + 0.20·C(t) + 0.15·S(t) + 0.10·W(t)
    Weights must sum to 1.0. Assert on every call.
    """

    W_P = 0.25
    W_I = 0.30
    W_C = 0.20
    W_S = 0.15
    W_W = 0.10

    def __init__(self):
        assert abs(self.W_P + self.W_I + self.W_C + self.W_S + self.W_W - 1.0) < 1e-9, \
            "Plane weights must sum to 1.0 exactly"
        self.perceptual = PerceptualPlane()
        self.inferential = InferentialPlane()
        self.consensus = ConsensusPlane()
        self.self_ref = SelfReflectionPlane()
        self.world_model = WorldModelPlane()
        self.gate = ActionGate()

    async def compute_all_planes(
        self, query: str, context: dict, cycle_id: str
    ) -> dict:
        input_channels = context.get("input_channels", {"default": [1.0, 2.0, 3.0]})
        reasoning_chains = context.get("reasoning_chains", [])
        env_signals = context.get("environmental_signals", {})

        p = self.perceptual.compute(input_channels)
        i = self.inferential.compute(reasoning_chains)
        c = self.consensus.compute(reasoning_chains)
        s = self.self_ref.compute(query)
        w = self.world_model.compute(env_signals)

        psi = self.W_P * p + self.W_I * i + self.W_C * c + self.W_S * s + self.W_W * w

        volatility = context.get("volatility", 0.0)
        novelty = context.get("novelty", 0.5)

        return {
            "p": p,
            "i": i,
            "c": c,
            "s": s,
            "w": w,
            "psi_total": psi,
            "volatility": volatility,
            "novelty": novelty,
            "cycle_id": cycle_id,
        }
