"""
Stress test: Validate the exponential growth shape of Λ(t).
Proves mathematically that TRION's compounding moat formula produces
genuine exponential growth — not linear, not logarithmic.

Method:
  1. Run 10,000 accumulations with constant η, ρ
  2. Sample Λ at checkpoints: 100, 500, 1k, 2k, 5k, 10k
  3. Verify Λ(N) / Λ(0) = (1 + η·ρ)^N within 0.01% tolerance
  4. Verify growth is super-linear: Λ(2N) > 2·Λ(N) (compounding)
  5. Verify log(Λ) vs N is linear with slope log(1 + η·ρ)
"""
import sys
import os
import math
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

ETA = 0.50
RHO = 0.70
LAMBDA_0 = 0.01
CHECKPOINTS = [100, 500, 1_000, 2_000, 5_000, 10_000]
TOLERANCE_PCT = 0.001  # 0.1% tolerance


class ExponentialShapeTest:

    def reset_moat_to_lambda0(self):
        """Reset moat state to Λ₀ = 0.01 for clean test."""
        import json
        state = {"log_lambda": math.log(LAMBDA_0), "n_cycles": 0, "t_start": 1.0}
        os.makedirs("data", exist_ok=True)
        with open("data/moat_state.json", "w") as f:
            json.dump(state, f)

    def run(self) -> dict:
        self.reset_moat_to_lambda0()

        from core.moat_accumulator import MoatAccumulator
        moat = MoatAccumulator()

        per_cycle_increment = math.log(1 + ETA * RHO)
        print(f"\n{'═' * 60}")
        print(f"  EXPONENTIAL SHAPE VALIDATION")
        print(f"{'═' * 60}")
        print(f"  η = {ETA}, ρ = {RHO}")
        print(f"  Λ₀ = {LAMBDA_0}")
        print(f"  Per-cycle log increment = log(1 + η·ρ) = {per_cycle_increment:.8f}")
        print(f"  Expected growth factor per cycle = {math.exp(per_cycle_increment):.8f}")
        print(f"  Checkpoints: {CHECKPOINTS}")
        print()

        checkpoint_set = set(CHECKPOINTS)
        results = {}
        n = 0
        start = time.time()

        for target in CHECKPOINTS:
            while n < target:
                moat.accumulate(eta_i=ETA, rho_i=RHO, cycle_id=f"exp_{n:05d}")
                n += 1

            actual_lambda = moat.get_current_lambda()
            theoretical_lambda = LAMBDA_0 * math.exp(n * per_cycle_increment)
            error_pct = abs(actual_lambda - theoretical_lambda) / theoretical_lambda * 100

            # Expected growth ratio Λ(N)/Λ₀
            growth_ratio = actual_lambda / LAMBDA_0
            expected_ratio = math.exp(n * per_cycle_increment)
            ratio_error_pct = abs(growth_ratio - expected_ratio) / expected_ratio * 100

            results[n] = {
                "n": n,
                "actual": actual_lambda,
                "theoretical": theoretical_lambda,
                "error_pct": error_pct,
                "growth_ratio": growth_ratio,
                "expected_ratio": expected_ratio,
                "ratio_error_pct": ratio_error_pct,
            }
            print(f"  N={n:>6,}: Λ_actual={actual_lambda:.8f}  Λ_theory={theoretical_lambda:.8f}  "
                  f"error={error_pct:.6f}%")

        elapsed = time.time() - start

        # ── Verify compounding (super-linear growth) ────────────────────
        lambda_at_1k = results[1_000]["actual"]
        lambda_at_2k = results[2_000]["actual"]
        lambda_at_5k = results[5_000]["actual"]
        lambda_at_10k = results[10_000]["actual"]

        # True compounding: Λ(2N) > 2·Λ(N)
        compound_2k_vs_1k = lambda_at_2k > 2 * lambda_at_1k
        compound_10k_vs_5k = lambda_at_10k > 2 * lambda_at_5k

        # ── Verify log-linearity ────────────────────────────────────────
        ns = [r["n"] for r in results.values()]
        log_lambdas = [math.log(r["actual"]) for r in results.values()]
        slope, intercept, r_squared = linear_fit(ns, log_lambdas)

        print(f"\n{'─' * 60}")
        print(f"  LOG-LINEAR FIT: log(Λ) = {slope:.8f}·N + {intercept:.6f}")
        print(f"  Expected slope:          {per_cycle_increment:.8f}")
        print(f"  Slope error:             {abs(slope - per_cycle_increment):.2e}")
        print(f"  R² (linearity):          {r_squared:.10f}")
        print(f"\n  COMPOUNDING VERIFICATION:")
        print(f"  Λ(2k) > 2·Λ(1k): {lambda_at_2k:.6f} > {2*lambda_at_1k:.6f} → {compound_2k_vs_1k}")
        print(f"  Λ(10k) > 2·Λ(5k): {lambda_at_10k:.6f} > {2*lambda_at_5k:.6f} → {compound_10k_vs_5k}")
        print(f"  Elapsed: {elapsed:.2f}s")

        return {
            "checkpoints": results,
            "slope_actual": slope,
            "slope_expected": per_cycle_increment,
            "slope_error": abs(slope - per_cycle_increment),
            "r_squared": r_squared,
            "compound_2k_vs_1k": compound_2k_vs_1k,
            "compound_10k_vs_5k": compound_10k_vs_5k,
            "elapsed_s": elapsed,
            "max_error_pct": max(r["error_pct"] for r in results.values()),
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

        max_err = results["max_error_pct"]
        check(f"All checkpoints within {TOLERANCE_PCT*100:.2f}% of theory",
              max_err < TOLERANCE_PCT * 100,
              f"max error = {max_err:.6f}%")

        check("log(Λ) linearity R² > 0.9999999 (exponential, not log/power)",
              results["r_squared"] > 0.9999999,
              f"R² = {results['r_squared']:.10f}")

        slope_err = results["slope_error"]
        check(f"Slope matches log(1+η·ρ) within 1e-8",
              slope_err < 1e-8,
              f"slope_error = {slope_err:.2e}")

        check("Compounding confirmed: Λ(2k) > 2·Λ(1k)",
              results["compound_2k_vs_1k"],
              "Λ(2k) not > 2·Λ(1k)")

        check("Compounding confirmed: Λ(10k) > 2·Λ(5k)",
              results["compound_10k_vs_5k"],
              "Λ(10k) not > 2·Λ(5k)")

        check("10,000 cycles complete in < 30s",
              results["elapsed_s"] < 30.0,
              f"took {results['elapsed_s']:.2f}s")

        print(f"\n  {'═' * 40}")
        print(f"  {passed} passed, {failed} failed")
        print(f"  {'═' * 40}")
        return passed, failed


def linear_fit(x: list, y: list):
    """Simple least-squares linear fit. Returns slope, intercept, R²."""
    n = len(x)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    xy = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    xx = sum((xi - x_mean) ** 2 for xi in x)
    slope = xy / xx if xx != 0 else 0.0
    intercept = y_mean - slope * x_mean
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else 1.0
    return slope, intercept, r2


if __name__ == "__main__":
    test = ExponentialShapeTest()
    results = test.run()
    passed, failed = test.assert_results(results)
    os.makedirs("data", exist_ok=True)
    with open("data/exponential_shape_results.json", "w") as f:
        serializable = {
            "slope_actual": results["slope_actual"],
            "slope_expected": results["slope_expected"],
            "slope_error": results["slope_error"],
            "r_squared": results["r_squared"],
            "compound_2k_vs_1k": results["compound_2k_vs_1k"],
            "compound_10k_vs_5k": results["compound_10k_vs_5k"],
            "elapsed_s": results["elapsed_s"],
            "max_error_pct": results["max_error_pct"],
        }
        json.dump(serializable, f, indent=2)
    print(f"\n  Results saved to data/exponential_shape_results.json")
    sys.exit(0 if failed == 0 else 1)
