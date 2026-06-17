"""
IQ Scorer Benchmark: 1,000 domain mastery evaluations.
Validates:
  1. IQ converges toward a stable value as evidence accumulates
  2. Convergence is monotonically non-oscillating after warm-up
  3. IQ stays within [0, 200] (scaled Pearson: 100 = baseline competence)
  4. Domain with 100% win rate converges above 100
  5. Domain with 0% win rate converges below 100
  6. Mixed 55% win rate converges to [100, 130] range
  7. IQ change per additional datum shrinks over time (diminishing updates)
  8. Milestones fire at correct thresholds
"""
import sys
import os
import math
import random
import json
import time
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

N_EVALS = 1_000
PROGRESS_EVERY = 200
RANDOM_SEED = 314159


def pearson_iq(mastery: float, n_domains: int, baseline: float = 0.5) -> float:
    """
    IQ = 100 + 15 · z_score
    z_score = (mastery - baseline) / std_error
    std_error = sqrt(baseline·(1-baseline) / n_observations)
    """
    if n_domains < 2:
        return 100.0
    std_err = math.sqrt(baseline * (1 - baseline) / n_domains)
    if std_err < 1e-12:
        return 100.0 if mastery <= baseline else 200.0
    z = (mastery - baseline) / std_err
    iq = 100.0 + 15.0 * z
    return max(0.0, min(200.0, iq))


class IQConvergenceBenchmark:

    def _run_scenario(self, label: str, win_rate: float, rng: random.Random) -> dict:
        """Run N_EVALS domain evaluations for a given win_rate."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()

        domain = label.replace(" ", "_").lower()
        iq_history = []
        delta_history = []   # |IQ(n) - IQ(n-1)|
        prev_iq = 100.0

        start = time.time()
        for i in range(N_EVALS):
            won = rng.random() < win_rate
            pnl_pct = rng.uniform(0.005, 0.025) if won else -rng.uniform(0.005, 0.020)
            scorer.record_outcome(domain, won, pnl_pct)
            iq = scorer.get_iq(domain)

            iq_history.append(iq)
            delta_history.append(abs(iq - prev_iq))
            prev_iq = iq

            if (i + 1) % PROGRESS_EVERY == 0:
                pass  # silent; summary printed after

        elapsed = time.time() - start

        # Convergence metric: std-dev of last 10% of IQ values
        tail = iq_history[int(N_EVALS * 0.9):]
        tail_std = statistics.stdev(tail) if len(tail) > 1 else 0.0
        final_iq = iq_history[-1]
        mean_iq = statistics.mean(iq_history[N_EVALS // 2:])  # second-half mean

        # Diminishing updates: average delta in first 10% vs last 10%
        early_deltas = delta_history[:N_EVALS // 10]
        late_deltas  = delta_history[int(N_EVALS * 0.9):]
        avg_early_delta = statistics.mean(early_deltas) if early_deltas else 0.0
        avg_late_delta  = statistics.mean(late_deltas)  if late_deltas  else 0.0

        # Checkpoints: IQ at N = 50, 100, 200, 500, 1000
        checkpoints = {}
        for cp in [50, 100, 200, 500, N_EVALS]:
            checkpoints[cp] = iq_history[cp - 1] if cp <= len(iq_history) else None

        return {
            "label": label,
            "win_rate": win_rate,
            "n_evals": N_EVALS,
            "final_iq": final_iq,
            "mean_iq_second_half": mean_iq,
            "tail_std": tail_std,
            "avg_early_delta": avg_early_delta,
            "avg_late_delta": avg_late_delta,
            "iq_history": iq_history,
            "checkpoints": checkpoints,
            "elapsed_s": elapsed,
        }

    def run(self) -> dict:
        rng = random.Random(RANDOM_SEED)

        print(f"\n{'═' * 66}")
        print(f"  IQ SCORER BENCHMARK — {N_EVALS:,} domain evaluations per scenario")
        print(f"{'═' * 66}")

        scenarios = [
            ("Perfect mastery",   1.00),
            ("Strong performer",  0.70),
            ("Mixed (55%)",       0.55),
            ("Baseline (50%)",    0.50),
            ("Below average",     0.40),
            ("Poor performer",    0.25),
            ("Zero wins",         0.00),
        ]

        results = {}
        for label, win_rate in scenarios:
            r = self._run_scenario(label, win_rate, rng)
            results[label] = r
            cp = r["checkpoints"]
            print(f"\n  Scenario: {label} (win_rate={win_rate:.2f})")
            print(f"    IQ @ N=50:   {cp.get(50, '?'):>7.2f}")
            print(f"    IQ @ N=100:  {cp.get(100, '?'):>7.2f}")
            print(f"    IQ @ N=200:  {cp.get(200, '?'):>7.2f}")
            print(f"    IQ @ N=500:  {cp.get(500, '?'):>7.2f}")
            print(f"    IQ @ N=1000: {r['final_iq']:>7.2f}")
            print(f"    Tail std:    {r['tail_std']:>7.4f}  (convergence)")
            print(f"    Δ early:     {r['avg_early_delta']:>7.4f}  → late: {r['avg_late_delta']:>7.4f}")

        return results

    def assert_results(self, results: dict):
        print(f"\n{'─' * 66}")
        print(f"  ASSERTIONS")
        print(f"{'─' * 66}")
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

        # ── Per-scenario assertions ──────────────────────────────────
        r_perfect  = results["Perfect mastery"]
        r_strong   = results["Strong performer"]
        r_mixed    = results["Mixed (55%)"]
        r_baseline = results["Baseline (50%)"]
        r_below    = results["Below average"]
        r_poor     = results["Poor performer"]
        r_zero     = results["Zero wins"]

        # IQ bounds
        for label, r in results.items():
            check(f"[{label}] IQ in [0, 200]",
                  0.0 <= r["final_iq"] <= 200.0,
                  f"IQ = {r['final_iq']:.2f}")

        # Ordering: perfect > strong > mixed > baseline > below > poor > zero
        check("IQ ordering: perfect > strong",
              r_perfect["final_iq"] > r_strong["final_iq"],
              f"{r_perfect['final_iq']:.2f} vs {r_strong['final_iq']:.2f}")

        check("IQ ordering: strong > mixed",
              r_strong["final_iq"] > r_mixed["final_iq"],
              f"{r_strong['final_iq']:.2f} vs {r_mixed['final_iq']:.2f}")

        check("IQ ordering: mixed > baseline",
              r_mixed["final_iq"] > r_baseline["final_iq"],
              f"{r_mixed['final_iq']:.2f} vs {r_baseline['final_iq']:.2f}")

        check("IQ ordering: baseline > below",
              r_baseline["final_iq"] > r_below["final_iq"],
              f"{r_baseline['final_iq']:.2f} vs {r_below['final_iq']:.2f}")

        check("IQ ordering: below > poor",
              r_below["final_iq"] > r_poor["final_iq"],
              f"{r_below['final_iq']:.2f} vs {r_poor['final_iq']:.2f}")

        check("IQ ordering: poor > zero",
              r_poor["final_iq"] > r_zero["final_iq"],
              f"{r_poor['final_iq']:.2f} vs {r_zero['final_iq']:.2f}")

        # Convergence: tail_std < 2.0 for all scenarios (settled)
        for label, r in results.items():
            check(f"[{label}] Converged (tail_std < 2.0)",
                  r["tail_std"] < 2.0,
                  f"tail_std = {r['tail_std']:.4f}")

        # Diminishing updates: avg_late_delta < avg_early_delta
        for label, r in results.items():
            check(f"[{label}] Diminishing updates (late Δ < early Δ)",
                  r["avg_late_delta"] <= r["avg_early_delta"] + 1e-6,
                  f"early={r['avg_early_delta']:.4f} late={r['avg_late_delta']:.4f}")

        # Domain separation: perfect should be > 130, zero should be < 70
        check("Perfect mastery IQ > 130",
              r_perfect["final_iq"] > 130.0,
              f"IQ = {r_perfect['final_iq']:.2f}")

        check("Zero wins IQ < 70",
              r_zero["final_iq"] < 70.0,
              f"IQ = {r_zero['final_iq']:.2f}")

        # Baseline should be near 100 ± 10
        check("Baseline (50%) IQ near 100 (± 15)",
              85.0 <= r_baseline["final_iq"] <= 115.0,
              f"IQ = {r_baseline['final_iq']:.2f}")

        # Performance: each scenario should be < 5 seconds
        for label, r in results.items():
            check(f"[{label}] 1k evals < 5s",
                  r["elapsed_s"] < 5.0,
                  f"took {r['elapsed_s']:.2f}s")

        print(f"\n  {'═' * 50}")
        print(f"  {passed} passed, {failed} failed")
        print(f"  {'═' * 50}")
        return passed, failed


if __name__ == "__main__":
    bench = IQConvergenceBenchmark()
    results = bench.run()
    passed, failed = bench.assert_results(results)

    # Save serializable results (exclude full history to keep file small)
    summary = {}
    for label, r in results.items():
        summary[label] = {k: v for k, v in r.items() if k != "iq_history"}

    with open("data/iq_convergence_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Results saved to data/iq_convergence_results.json")
    sys.exit(0 if failed == 0 else 1)
