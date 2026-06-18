"""Unit tests for the coherence engine and plane weights."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def test_plane_weights_sum_to_one():
    from core.coherence_engine import CoherenceEngine
    e = CoherenceEngine()
    total = e.W_P + e.W_I + e.W_C + e.W_S + e.W_W
    assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, not 1.0"


def test_moat_never_decreases():
    from core.moat_accumulator import MoatAccumulator
    m = MoatAccumulator()
    before = m.get_current_lambda()
    m.accumulate(eta_i=0.5, rho_i=0.7)
    after = m.get_current_lambda()
    assert after >= before, "Moat decreased — this must never happen"


def test_action_gate_thresholds():
    from core.action_gate import ActionGate
    g = ActionGate()
    # Base delta (no volatility, no novelty)
    delta = g.compute_threshold(0.0, 0.0)
    assert delta == g.DELTA_BASE
    # Max delta capped at 0.897
    delta_max = g.compute_threshold(1.0, 1.0)
    assert delta_max <= g.MAX_DELTA


def test_perceptual_zero_below_threshold():
    from planes.perceptual import PerceptualPlane
    p = PerceptualPlane()
    # Single spike among zeros → concentrated mass → entropy/H_max < 0.35 → floor to 0.0
    score = p.compute({"channel": [0.0] * 99 + [1000.0]})
    assert score == 0.0


def test_world_model_zscore_hard_zero():
    from planes.world_model import WorldModelPlane
    w = WorldModelPlane()
    # Seed history
    for i in range(50):
        w.compute({"price": float(100 + i % 3)})
    # Massive anomaly → should return 0.0
    score = w.compute({"price": 100000.0})
    assert score == 0.0


def test_inferential_contradiction():
    from planes.inferential import InferentialPlane
    inf = InferentialPlane()
    # Opposite vectors → cosine < -0.3 → hard zero
    chains = [
        {"confidence": 0.8, "vector": [1.0, 0.0, 0.0]},
        {"confidence": 0.8, "vector": [-1.0, 0.0, 0.0]},
    ]
    score = inf.compute(chains)
    assert score == 0.0, f"Expected 0.0 contradiction, got {score}"


if __name__ == "__main__":
    test_plane_weights_sum_to_one()
    test_moat_never_decreases()
    test_action_gate_thresholds()
    test_perceptual_zero_below_threshold()
    test_world_model_zscore_hard_zero()
    test_inferential_contradiction()
    print("All unit tests passed.")
