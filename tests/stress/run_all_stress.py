#!/usr/bin/env python3
"""
Master stress test runner.
Validates SOVEREIGN-Ω's mathematical integrity under sustained load.

Tests:
  1. Moat Growth Curve (10,000 cycles, random η/ρ) — exponential confirmed
  2. Exponential Shape Validation (constant η/ρ, compare to theory)
  3. Coherence Cycle Stress (10,000 full plane computations)
  4. Numerical Stability (extreme values, edge cases, overflow prevention)
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


def run_test(label: str, module_path: str, class_name: str) -> tuple:
    import importlib
    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        instance = cls()
        results = instance.run()
        passed, failed = instance.assert_results(results)
        return passed, failed, results
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 0, 1, {"error": str(e)}


SUITES = [
    ("Moat Growth Curve (10k cycles, random η/ρ)",
     "tests.stress.test_moat_growth_curve", "MoatGrowthStressTest"),
    ("Exponential Shape (η=0.50, ρ=0.70, vs theory)",
     "tests.stress.test_exponential_shape", "ExponentialShapeTest"),
    ("Coherence Cycle Stress (10k full planes)",
     "tests.stress.test_coherence_cycle_stress", "CoherenceCycleStressTest"),
    ("Numerical Stability (extremes, overflows, NaN)",
     "tests.stress.test_numerical_stability", "NumericalStabilityTest"),
]


def main():
    print()
    print("╔" + "═" * 62 + "╗")
    print("║     SOVEREIGN-Ω STRESS TEST SUITE                           ║")
    print("║     10,000 cycles. Mathematical proof. Truth or silence.    ║")
    print("╚" + "═" * 62 + "╝")

    total_passed = 0
    total_failed = 0
    results_log = []
    wall_start = time.time()

    for label, module, cls in SUITES:
        p, f, raw = run_test(label, module, cls)
        total_passed += p
        total_failed += f
        results_log.append({"label": label, "passed": p, "failed": f})

    wall_elapsed = time.time() - wall_start

    print()
    print("╔" + "═" * 62 + "╗")
    print(f"║  STRESS TEST RESULTS                                         ║")
    print(f"╠" + "═" * 62 + "╣")
    for r in results_log:
        status = "✓" if r["failed"] == 0 else "✗"
        short = r["label"][:50].ljust(50)
        print(f"║  {status} {short}  {r['passed']:2d}P/{r['failed']:2d}F  ║")
    print(f"╠" + "═" * 62 + "╣")
    print(f"║  TOTAL: {total_passed} passed, {total_failed} failed  "
          f"(wall time: {wall_elapsed:.1f}s)".ljust(63) + "║")
    print(f"╚" + "═" * 62 + "╝")
    print()

    # Save aggregated results
    with open("data/stress_suite_summary.json", "w") as f:
        json.dump({
            "total_passed": total_passed,
            "total_failed": total_failed,
            "wall_elapsed_s": wall_elapsed,
            "suites": results_log,
        }, f, indent=2)
    print(f"  Summary saved to data/stress_suite_summary.json")

    if total_failed > 0:
        print(f"\n  STRESS TEST FAILURES: {total_failed} test(s) failed.")
        print(f"  Mathematical properties not guaranteed. Review before deployment.")
        sys.exit(1)
    else:
        print(f"\n  ALL STRESS TESTS PASSED.")
        print(f"  Exponential moat growth confirmed over 10,000 cycles.")
        print(f"  TRION mathematics validated numerically.")
        print(f"  SOVEREIGN-Ω is mathematically coherent.")


if __name__ == "__main__":
    main()
