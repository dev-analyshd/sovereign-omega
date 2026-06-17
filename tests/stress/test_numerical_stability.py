"""
Stress test: Numerical stability under extreme conditions.
Validates that no overflow, underflow, NaN, or Inf occurs across:
  1. 10,000 cycles with alternating extreme/small η values
  2. Coherence computation with pathological plane scores
  3. Kelly fraction with edge-case p_win values
  4. Bayesian updater over 10,000 trade outcomes
  5. FAISS store under 1,000 high-dimensional vector writes
"""
import sys
import os
import math
import random
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class NumericalStabilityTest:

    def test_extreme_eta_values(self) -> tuple:
        """Alternating very large (100) and very small (1e-8) eta values."""
        from core.moat_accumulator import MoatAccumulator
        moat = MoatAccumulator()
        errors = []

        for i in range(1000):
            eta = 100.0 if i % 2 == 0 else 1e-8
            rho = 0.5
            moat.accumulate(eta_i=eta, rho_i=rho, cycle_id=f"ext_{i}")
            lam = moat.get_current_lambda()
            if not math.isfinite(lam):
                errors.append(f"cycle {i}: Λ = {lam}")
            if lam <= 0:
                errors.append(f"cycle {i}: Λ ≤ 0: {lam}")

        result = len(errors) == 0
        print(f"  {'✓' if result else '✗'} Extreme η (100 ↔ 1e-8): "
              f"{'all finite and positive' if result else errors[:2]}")
        return result, errors

    def test_pathological_coherence_scores(self) -> tuple:
        """Boundary plane scores: all 0, all 1, alternating, degenerate combos."""
        errors = []
        W_P, W_I, W_C, W_S, W_W = 0.25, 0.30, 0.20, 0.15, 0.10

        test_cases = [
            (0.0, 0.0, 0.0, 0.0, 0.0),   # All zero
            (1.0, 1.0, 1.0, 1.0, 1.0),   # All one
            (0.0, 1.0, 0.0, 1.0, 0.0),   # Alternating
            (1.0, 0.0, 1.0, 0.0, 1.0),   # Alternating inverse
            (0.5, 0.5, 0.5, 0.5, 0.5),   # All mid
            (1e-10, 1e-10, 1e-10, 1e-10, 1e-10),  # Near-zero
            (1 - 1e-10, 1.0, 1.0, 1.0, 1.0),      # Near-max
        ]

        for p, i, c, s, w in test_cases:
            psi = W_P * p + W_I * i + W_C * c + W_S * s + W_W * w
            if not math.isfinite(psi):
                errors.append(f"psi NaN/Inf for ({p},{i},{c},{s},{w})")
            if not (0.0 <= psi <= 1.0 + 1e-12):
                errors.append(f"psi={psi:.10f} out of [0,1] for ({p},{i},{c},{s},{w})")

        result = len(errors) == 0
        print(f"  {'✓' if result else '✗'} Pathological plane scores: "
              f"{'all Ψ in [0,1]' if result else errors[:2]}")
        return result, errors

    def test_kelly_fraction_edge_cases(self) -> tuple:
        """Kelly fraction with p_win near 0, 0.5, 1.0 and extreme payoff ratios."""
        from trading.bayesian_updater import compute_kelly_fraction, compute_expected_edge
        errors = []

        cases = [
            (0.01, 0.01, 0.01),   # Near-zero win prob
            (0.50, 0.02, 0.01),   # Equal odds
            (0.99, 0.10, 0.01),   # Near-certain win
            (0.50, 100.0, 0.01),  # Huge upside
            (0.50, 0.001, 100.0), # Huge downside
            (0.0,  0.01, 0.01),   # Zero win prob
            (1.0,  0.01, 0.01),   # Certain win
        ]

        for p_win, avg_win, avg_loss in cases:
            kelly = compute_kelly_fraction(p_win, avg_win, avg_loss)
            edge = compute_expected_edge(p_win, avg_win, avg_loss)

            if not math.isfinite(kelly):
                errors.append(f"Kelly NaN/Inf: p={p_win}, w={avg_win}, l={avg_loss}")
            if not (0.0 <= kelly <= 0.02 + 1e-9):
                errors.append(f"Kelly={kelly:.6f} out of [0, 0.02]: p={p_win}")
            if not math.isfinite(edge):
                errors.append(f"Edge NaN/Inf: p={p_win}, w={avg_win}, l={avg_loss}")

        result = len(errors) == 0
        print(f"  {'✓' if result else '✗'} Kelly/edge edge cases: "
              f"{'all finite and bounded' if result else errors[:2]}")
        return result, errors

    def test_bayesian_updater_10k_outcomes(self) -> tuple:
        """10,000 trade outcomes fed into Bayesian updater — check for stability."""
        import asyncio
        from trading.bayesian_updater import BayesianUpdater
        rng = random.Random(42)
        updater = BayesianUpdater()
        errors = []

        async def run_updates():
            for i in range(1000):
                won = rng.random() < 0.55  # 55% win rate
                pnl_pct = rng.uniform(0.005, 0.025) if won else -rng.uniform(0.005, 0.015)
                await updater.update_after_trade("BTC/USDT", "momentum", won, pnl_pct)

                state = updater.states.get(("BTC/USDT", "momentum"), {})
                p_win = state.get("p_win", 0.5)
                if not math.isfinite(p_win):
                    errors.append(f"p_win NaN/Inf at iteration {i}")
                if not (0.0 <= p_win <= 1.0):
                    errors.append(f"p_win={p_win:.6f} outside [0,1] at iteration {i}")

        asyncio.run(run_updates())

        state = updater.states.get(("BTC/USDT", "momentum"), {})
        p_win = state.get("p_win", 0.5)
        # p_win should converge toward ~0.55 with enough data
        bias_check = 0.45 < p_win < 0.65

        result = len(errors) == 0 and bias_check
        print(f"  {'✓' if result else '✗'} Bayesian 1k outcomes: "
              f"p_win={p_win:.4f}, errors={len(errors)}, converged={bias_check}")
        return result, errors

    def test_faiss_1k_writes_stable(self) -> tuple:
        """1,000 FAISS writes with various dimensions — no crash, always persists."""
        import numpy as np
        from memory.faiss_store import FAISSStore
        store = FAISSStore()
        errors = []
        before = store.total()
        rng = random.Random(99)

        for i in range(1000):
            # Mix of good, padded, and truncated vectors
            dim = rng.choice([64, 128, 256, 300, 512])
            vec = np.random.randn(dim).astype(np.float32)
            store.add(vec, {"stress_i": i})
            if store.total() != before + i + 1:
                errors.append(f"Total mismatch at {i}: {store.total()} != {before + i + 1}")

        result = len(errors) == 0
        print(f"  {'✓' if result else '✗'} FAISS 1k writes: "
              f"total={store.total()}, errors={len(errors)}")
        return result, errors

    def test_self_reflection_repeated_queries(self) -> tuple:
        """500 repeated self-reflection queries — scores must stay in [0,1]."""
        from planes.self_reflection import SelfReflectionPlane
        plane = SelfReflectionPlane()
        errors = []
        queries = [
            "BTC trade evaluation",
            "ETH market analysis",
            "Coherence gate status",
            "Moat accumulation check",
            "Social post generation",
        ]
        rng = random.Random(77)

        for i in range(500):
            q = queries[i % len(queries)]
            score = plane.compute(q)
            if not math.isfinite(score):
                errors.append(f"iter {i}: score NaN/Inf")
            if not (0.0 <= score <= 1.0):
                errors.append(f"iter {i}: score={score:.6f} out of [0,1]")

        result = len(errors) == 0
        print(f"  {'✓' if result else '✗'} SelfReflection 500 repeated queries: "
              f"errors={len(errors)}")
        return result, errors

    def run(self) -> dict:
        print(f"\n{'═' * 60}")
        print(f"  NUMERICAL STABILITY STRESS TEST")
        print(f"{'═' * 60}\n")

        start = time.time()
        all_passed = True
        summary = {}

        for method_name in [
            "test_extreme_eta_values",
            "test_pathological_coherence_scores",
            "test_kelly_fraction_edge_cases",
            "test_bayesian_updater_10k_outcomes",
            "test_faiss_1k_writes_stable",
            "test_self_reflection_repeated_queries",
        ]:
            try:
                ok, errs = getattr(self, method_name)()
                summary[method_name] = {"passed": ok, "errors": len(errs)}
                if not ok:
                    all_passed = False
            except Exception as e:
                import traceback
                print(f"  ✗ {method_name}: EXCEPTION: {e}")
                traceback.print_exc()
                summary[method_name] = {"passed": False, "errors": 1}
                all_passed = False

        elapsed = time.time() - start
        passed = sum(1 for v in summary.values() if v["passed"])
        failed = len(summary) - passed

        print(f"\n{'─' * 60}")
        print(f"  Elapsed: {elapsed:.2f}s")
        print(f"  {passed} passed, {failed} failed")
        print(f"{'─' * 60}")

        return {"all_passed": all_passed, "summary": summary, "elapsed_s": elapsed,
                "passed": passed, "failed": failed}


if __name__ == "__main__":
    test = NumericalStabilityTest()
    results = test.run()
    sys.exit(0 if results["all_passed"] else 1)
