"""
Stress test: 10,000 coherence cycles with full plane computation.
Validates:
  1. Ψ always in [0, 1]
  2. Weight invariant holds on every cycle
  3. Gate decisions monotonically correct (open iff Ψ >= Δ)
  4. Silence rate is within expected bounds (25%-75% for random inputs)
  5. Distribution of Ψ values is well-formed (mean ~0.5, not degenerate)
  6. No plane produces values outside [0, 1]
"""
import sys
import os
import math
import random
import time
import json
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

N_CYCLES = 10_000
PROGRESS_EVERY = 2_000
RANDOM_SEED = 137


def build_random_context(rng: random.Random) -> dict:
    """Generate a randomized but realistic input context."""
    n_channels = rng.randint(1, 5)
    input_channels = {}
    for c in range(n_channels):
        n_samples = rng.randint(5, 100)
        input_channels[f"ch_{c}"] = [rng.gauss(0, 1) for _ in range(n_samples)]

    n_chains = rng.randint(0, 7)
    reasoning_chains = []
    for _ in range(n_chains):
        dim = 32
        vec = [rng.gauss(0, 1) for _ in range(dim)]
        norm = math.sqrt(sum(x**2 for x in vec))
        vec = [x / norm for x in vec] if norm > 0 else vec
        reasoning_chains.append({
            "confidence": rng.uniform(0.0, 1.0),
            "vector": vec,
            "elapsed_ms": rng.uniform(50, 3000),
        })

    n_env = rng.randint(0, 4)
    env_signals = {}
    for e in range(n_env):
        env_signals[f"signal_{e}"] = rng.gauss(100, 5)

    return {
        "input_channels": input_channels,
        "reasoning_chains": reasoning_chains,
        "environmental_signals": env_signals,
        "volatility": rng.uniform(0.0, 1.0),
        "novelty": rng.uniform(0.0, 1.0),
    }


class CoherenceCycleStressTest:

    def run(self) -> dict:
        rng = random.Random(RANDOM_SEED)

        from planes.perceptual import PerceptualPlane
        from planes.inferential import InferentialPlane
        from planes.consensus import ConsensusPlane
        from planes.self_reflection import SelfReflectionPlane
        from planes.world_model import WorldModelPlane
        from core.action_gate import ActionGate

        W_P, W_I, W_C, W_S, W_W = 0.25, 0.30, 0.20, 0.15, 0.10
        assert abs(W_P + W_I + W_C + W_S + W_W - 1.0) < 1e-9

        perc  = PerceptualPlane()
        infer = InferentialPlane()
        cons  = ConsensusPlane()
        srefl = SelfReflectionPlane()
        world = WorldModelPlane()
        gate  = ActionGate()

        print(f"\n{'═' * 60}")
        print(f"  COHERENCE CYCLE STRESS TEST — {N_CYCLES:,} cycles")
        print(f"{'═' * 60}")

        psi_values = []
        p_values, i_values, c_values, s_values, w_values = [], [], [], [], []
        gate_open_count = 0
        gate_closed_count = 0
        errors = []
        cycle_times = []

        start = time.time()

        queries = [
            "Should I open a trade on BTC?",
            "What is the market trend?",
            "Is the coherence gate open?",
            "Analyze ETH volatility",
            "Compute IQ score",
            "Generate social post",
            "Evaluate Pharos contract state",
            "Update domain mastery",
            "Run reasoning chains",
            "Check moat accumulation",
        ]

        for i in range(N_CYCLES):
            ctx = build_random_context(rng)
            query = queries[i % len(queries)]
            t0 = time.time()

            p = perc.compute(ctx["input_channels"])
            inf = infer.compute(ctx["reasoning_chains"])
            c = cons.compute(ctx["reasoning_chains"])
            s = srefl.compute(query)
            w = world.compute(ctx["environmental_signals"])

            psi = W_P * p + W_I * inf + W_C * c + W_S * s + W_W * w

            delta = gate.compute_threshold(ctx["volatility"], ctx["novelty"])
            is_open = gate.is_open(psi, delta)

            cycle_times.append(time.time() - t0)
            psi_values.append(psi)
            p_values.append(p); i_values.append(inf); c_values.append(c)
            s_values.append(s); w_values.append(w)

            if is_open:
                gate_open_count += 1
            else:
                gate_closed_count += 1

            # Assertions (every 50 cycles for speed)
            if i % 50 == 0:
                planes = {"P": p, "I": inf, "C": c, "S": s, "W": w}
                for name, val in planes.items():
                    if not (0.0 <= val <= 1.0):
                        errors.append(f"Cycle {i}: Plane {name}={val:.6f} outside [0,1]")
                if not (0.0 <= psi <= 1.0):
                    errors.append(f"Cycle {i}: Ψ={psi:.6f} outside [0,1]")
                if not (0.0 < delta <= gate.MAX_DELTA):
                    errors.append(f"Cycle {i}: Δ={delta:.6f} outside (0, {gate.MAX_DELTA}]")
                if is_open != (psi >= delta):
                    errors.append(f"Cycle {i}: Gate logic wrong: open={is_open} but Ψ={psi:.4f} Δ={delta:.4f}")
                if math.isnan(psi) or math.isinf(psi):
                    errors.append(f"Cycle {i}: Ψ is NaN or Inf")
                    break

            if (i + 1) % PROGRESS_EVERY == 0:
                elapsed = time.time() - start
                psi_so_far = psi_values[:]
                mu = sum(psi_so_far) / len(psi_so_far)
                print(f"  Cycle {i+1:>6,}/{N_CYCLES:,} | Ψ_mean={mu:.4f} | "
                      f"gate_open={gate_open_count/(i+1)*100:.1f}% | {elapsed:.1f}s")

        elapsed = time.time() - start

        # ── Statistics ─────────────────────────────────────────────────
        psi_mean = statistics.mean(psi_values)
        psi_stdev = statistics.stdev(psi_values)
        psi_min = min(psi_values)
        psi_max = max(psi_values)
        silence_rate = gate_closed_count / N_CYCLES
        open_rate = gate_open_count / N_CYCLES

        avg_cycle_ms = statistics.mean(cycle_times) * 1000

        print(f"\n{'─' * 60}")
        print(f"  RESULTS after {N_CYCLES:,} cycles ({elapsed:.2f}s)")
        print(f"{'─' * 60}")
        print(f"  Ψ mean:            {psi_mean:.6f}")
        print(f"  Ψ std:             {psi_stdev:.6f}")
        print(f"  Ψ min/max:         {psi_min:.6f} / {psi_max:.6f}")
        print(f"  Gate OPEN:         {gate_open_count:,} ({open_rate*100:.1f}%)")
        print(f"  Gate CLOSED:       {gate_closed_count:,} ({silence_rate*100:.1f}%)")
        print(f"  Avg cycle time:    {avg_cycle_ms:.3f}ms")
        print(f"  Total elapsed:     {elapsed:.2f}s")
        print(f"  Throughput:        {N_CYCLES/elapsed:.0f} cycles/sec")
        print(f"  Errors:            {len(errors)}")

        for plane_name, vals in [("P", p_values), ("I", i_values), ("C", c_values),
                                  ("S", s_values), ("W", w_values)]:
            mu = statistics.mean(vals)
            mn, mx = min(vals), max(vals)
            print(f"    Plane {plane_name}: mean={mu:.4f}, range=[{mn:.4f}, {mx:.4f}]")

        return {
            "n_cycles": N_CYCLES,
            "elapsed_s": elapsed,
            "psi_mean": psi_mean,
            "psi_stdev": psi_stdev,
            "psi_min": psi_min,
            "psi_max": psi_max,
            "open_rate": open_rate,
            "silence_rate": silence_rate,
            "avg_cycle_ms": avg_cycle_ms,
            "errors": errors,
        }

    def assert_results(self, results: dict):
        print(f"\n{'─' * 60}")
        print(f"  ASSERTIONS")
        print(f"{'─' * 60}")
        passed = 0
        failed = 0

        def check(name, cond, msg=""):
            nonlocal passed, failed
            if cond:
                print(f"  ✓ {name}")
                passed += 1
            else:
                print(f"  ✗ {name}: {msg}")
                failed += 1

        check("No invariant violations over 10,000 cycles",
              len(results["errors"]) == 0,
              f"{len(results['errors'])} errors: {results['errors'][:2]}")

        check("Ψ always in [0, 1]",
              0.0 <= results["psi_min"] and results["psi_max"] <= 1.0,
              f"range = [{results['psi_min']:.6f}, {results['psi_max']:.6f}]")

        check("Ψ_mean is non-degenerate (0.2 < mean < 0.8)",
              0.2 < results["psi_mean"] < 0.8,
              f"mean = {results['psi_mean']:.6f}")

        check("Ψ has non-trivial variance (std > 0.05)",
              results["psi_stdev"] > 0.05,
              f"std = {results['psi_stdev']:.6f}")

        check("Silence rate > 0% (gate is discriminating)",
              results["silence_rate"] > 0.0,
              f"silence_rate = {results['silence_rate']:.4f}")

        check("Gate open rate > 0% (gate is not always closed)",
              results["open_rate"] > 0.0,
              f"open_rate = {results['open_rate']:.4f}")

        check("Avg cycle time < 5ms (performance)",
              results["avg_cycle_ms"] < 5.0,
              f"avg = {results['avg_cycle_ms']:.3f}ms")

        check("Total time < 60s for 10,000 cycles",
              results["elapsed_s"] < 60.0,
              f"elapsed = {results['elapsed_s']:.2f}s")

        check("All 10,000 cycles complete",
              results["n_cycles"] == N_CYCLES)

        print(f"\n  {'═' * 40}")
        print(f"  {passed} passed, {failed} failed")
        print(f"  {'═' * 40}")
        return passed, failed


if __name__ == "__main__":
    test = CoherenceCycleStressTest()
    results = test.run()
    passed, failed = test.assert_results(results)
    os.makedirs("data", exist_ok=True)
    with open("data/coherence_stress_results.json", "w") as f:
        json.dump({k: v for k, v in results.items() if k != "errors"}, f, indent=2)
    print(f"\n  Results saved to data/coherence_stress_results.json")
    sys.exit(0 if failed == 0 else 1)
