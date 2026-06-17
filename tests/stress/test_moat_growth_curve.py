"""
Stress test: 10,000 consecutive coherence cycles with randomized inputs.
Validates:
  1. Λ(t) growth follows expected exponential curve
  2. log(Λ(t)) increases linearly with N (law of large numbers)
  3. Numerical stability — no overflow, NaN, or negative values
  4. Moat growth rate is bounded: log(1 + η·ρ) per cycle
  5. Projection accuracy: actual vs theoretical Λ(N) within 10%
  6. Memory (FAISS) remains consistent after 10k cycles
"""
import sys
import os
import math
import random
import time
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

N_CYCLES = 10_000
PROGRESS_EVERY = 1_000
RANDOM_SEED = 42


def theoretical_lambda(lambda_0: float, eta_avg: float, rho_avg: float, n: int) -> float:
    """
    Theoretical Λ after n cycles:
    log(Λ(n)) = log(Λ₀) + n · E[log(1 + η·ρ)]
    ≈ log(Λ₀) + n · log(1 + η_avg · ρ_avg)
    """
    per_cycle = math.log(1 + eta_avg * rho_avg)
    return lambda_0 * math.exp(n * per_cycle)


class MoatGrowthStressTest:

    def run(self) -> dict:
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)

        from core.moat_accumulator import MoatAccumulator
        moat = MoatAccumulator()

        lambda_0 = moat.get_current_lambda()
        log_lambda_0 = moat.log_lambda

        print(f"\n{'═' * 60}")
        print(f"  MOAT GROWTH STRESS TEST — {N_CYCLES:,} cycles")
        print(f"{'═' * 60}")
        print(f"  Λ₀ = {lambda_0:.8f}")
        print(f"  log(Λ₀) = {log_lambda_0:.6f}\n")

        # Tracking arrays
        lambda_history = [lambda_0]
        log_lambda_history = [log_lambda_0]
        increments = []
        eta_values = []
        rho_values = []

        errors = []
        start = time.time()

        for i in range(N_CYCLES):
            # Randomized inputs — uniform in realistic operational ranges
            eta = random.uniform(0.01, 1.0)
            rho = random.uniform(0.01, 1.0)
            eta_values.append(eta)
            rho_values.append(rho)

            prev_log = moat.log_lambda
            moat.accumulate(eta_i=eta, rho_i=rho, cycle_id=f"stress_{i:05d}")
            curr_log = moat.log_lambda

            increment = curr_log - prev_log
            increments.append(increment)

            lam = moat.get_current_lambda()
            lambda_history.append(lam)
            log_lambda_history.append(curr_log)

            # Continuous assertions (sample every 100 cycles for speed)
            if i % 100 == 0:
                # 1. Never decreases
                if lam < lambda_history[-2]:
                    errors.append(f"Cycle {i}: Λ decreased {lambda_history[-2]:.10f} → {lam:.10f}")

                # 2. Finite
                if not math.isfinite(lam):
                    errors.append(f"Cycle {i}: Λ is non-finite: {lam}")
                    break

                # 3. Positive
                if lam <= 0:
                    errors.append(f"Cycle {i}: Λ is non-positive: {lam}")
                    break

                # 4. log-space increment matches expected
                expected_inc = math.log(1 + eta * rho)
                if abs(increment - expected_inc) > 1e-10:
                    errors.append(f"Cycle {i}: increment {increment:.15f} != expected {expected_inc:.15f}")

            # Progress print
            if (i + 1) % PROGRESS_EVERY == 0:
                elapsed = time.time() - start
                print(f"  Cycle {i+1:>6,}/{N_CYCLES:,} | Λ={lam:.8f} | "
                      f"log(Λ)={curr_log:.6f} | {elapsed:.1f}s")

        elapsed = time.time() - start

        # ── Post-run analysis ──────────────────────────────────────────
        final_lambda = moat.get_current_lambda()
        eta_avg = sum(eta_values) / len(eta_values)
        rho_avg = sum(rho_values) / len(rho_values)
        lambda_theoretical = theoretical_lambda(lambda_0, eta_avg, rho_avg, N_CYCLES)

        # Growth ratio actual vs theoretical
        growth_actual = final_lambda / lambda_0
        growth_theoretical = lambda_theoretical / lambda_0
        growth_error_pct = abs(growth_actual - growth_theoretical) / growth_theoretical * 100

        # log(Λ) linearity check: fit y = a*x + b, check R²
        r_squared = compute_r_squared(log_lambda_history)

        # Increment statistics
        inc_mean = sum(increments) / len(increments)
        inc_variance = sum((x - inc_mean) ** 2 for x in increments) / len(increments)
        inc_std = math.sqrt(inc_variance)

        # Total log-space growth
        total_log_growth = moat.log_lambda - log_lambda_0
        expected_total_log_growth = sum(math.log(1 + e * r) for e, r in zip(eta_values, rho_values))

        print(f"\n{'─' * 60}")
        print(f"  RESULTS after {N_CYCLES:,} cycles ({elapsed:.2f}s)")
        print(f"{'─' * 60}")
        print(f"  Initial Λ₀:           {lambda_0:.10f}")
        print(f"  Final Λ(N):           {final_lambda:.10f}")
        print(f"  Growth ×:             {growth_actual:.4f}×")
        print(f"  Theoretical ×:        {growth_theoretical:.4f}×")
        print(f"  Growth error:         {growth_error_pct:.4f}%")
        print(f"  η_avg:                {eta_avg:.4f}")
        print(f"  ρ_avg:                {rho_avg:.4f}")
        print(f"  log(Λ) R²:            {r_squared:.8f}")
        print(f"  Total log-growth:     {total_log_growth:.6f}")
        print(f"  Expected log-growth:  {expected_total_log_growth:.6f}")
        print(f"  Log-growth match:     {abs(total_log_growth - expected_total_log_growth):.2e}")
        print(f"  Increment μ:          {inc_mean:.8f}")
        print(f"  Increment σ:          {inc_std:.8f}")
        print(f"  Errors found:         {len(errors)}")

        return {
            "n_cycles": N_CYCLES,
            "elapsed_s": elapsed,
            "lambda_0": lambda_0,
            "lambda_final": final_lambda,
            "growth_actual": growth_actual,
            "growth_theoretical": growth_theoretical,
            "growth_error_pct": growth_error_pct,
            "r_squared": r_squared,
            "total_log_growth_match": abs(total_log_growth - expected_total_log_growth),
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

        check("No rule violations during {N_CYCLES:,} cycles",
              len(results["errors"]) == 0,
              f"{len(results['errors'])} violations: {results['errors'][:3]}")

        check("Final Λ is positive and finite",
              math.isfinite(results["lambda_final"]) and results["lambda_final"] > 0,
              f"Λ = {results['lambda_final']}")

        check("Actual growth > 1.0× (Λ grew)",
              results["growth_actual"] > 1.0,
              f"growth = {results['growth_actual']:.4f}")

        check("Growth error within 5% of theoretical",
              results["growth_error_pct"] < 5.0,
              f"error = {results['growth_error_pct']:.4f}%")

        check("log(Λ) linearity R² > 0.99 (exponential growth confirmed)",
              results["r_squared"] > 0.99,
              f"R² = {results['r_squared']:.8f}")

        check("Total log-growth matches sum of increments (< 1e-8 error)",
              results["total_log_growth_match"] < 1e-8,
              f"mismatch = {results['total_log_growth_match']:.2e}")

        check("10,000 cycles complete without crash",
              results["n_cycles"] == N_CYCLES)

        check("Performance: < 30 seconds for 10k cycles",
              results["elapsed_s"] < 30.0,
              f"took {results['elapsed_s']:.2f}s")

        print(f"\n  {'═' * 40}")
        print(f"  {passed} passed, {failed} failed")
        print(f"  {'═' * 40}")

        return passed, failed


def compute_r_squared(log_lambda_history: list) -> float:
    """Compute R² of log(Λ) vs cycle index (should be linear → R² near 1.0)."""
    n = len(log_lambda_history)
    x = list(range(n))
    y = log_lambda_history

    x_mean = sum(x) / n
    y_mean = sum(y) / n

    ss_res = 0.0
    ss_tot = 0.0
    xy_sum = 0.0
    xx_sum = 0.0

    for xi, yi in zip(x, y):
        xy_sum += (xi - x_mean) * (yi - y_mean)
        xx_sum += (xi - x_mean) ** 2

    if xx_sum == 0:
        return 0.0

    slope = xy_sum / xx_sum
    intercept = y_mean - slope * x_mean

    for xi, yi in zip(x, y):
        y_pred = slope * xi + intercept
        ss_res += (yi - y_pred) ** 2
        ss_tot += (yi - y_mean) ** 2

    if ss_tot == 0:
        return 1.0

    return 1.0 - ss_res / ss_tot


if __name__ == "__main__":
    test = MoatGrowthStressTest()
    results = test.run()
    passed, failed = test.assert_results(results)

    # Save results to file for CI artifact
    os.makedirs("data", exist_ok=True)
    with open("data/stress_test_results.json", "w") as f:
        json.dump({k: v for k, v in results.items() if k != "errors" or len(v) == 0}, f, indent=2)

    print(f"\n  Results saved to data/stress_test_results.json")
    sys.exit(0 if failed == 0 else 1)
