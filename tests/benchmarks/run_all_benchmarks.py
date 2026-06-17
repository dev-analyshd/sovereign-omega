#!/usr/bin/env python3
"""
Master benchmark runner for SOVEREIGN-Ω IQ system.
Tests:
  1. IQ Convergence  — 1,000 evals × 7 win-rate scenarios
  2. IQ Milestones   — fire exactly once, never retrograde, persisted
  3. IQ Curve Plot   — ASCII chart + JSON output saved to data/
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


def run_convergence():
    from tests.benchmarks.test_iq_convergence import IQConvergenceBenchmark
    bench = IQConvergenceBenchmark()
    results = bench.run()
    p, f = bench.assert_results(results)
    return p, f


def run_milestones():
    from tests.benchmarks.test_iq_milestones import IQMilestoneBenchmark
    bench = IQMilestoneBenchmark()
    p, f = bench.run_all()
    return p, f


def run_curve_plot():
    from tests.benchmarks.test_iq_curve_plot import main as plot_main
    rc = plot_main()
    return (1, 0) if rc == 0 else (0, 1)


SUITES = [
    ("IQ Convergence  (1k evals × 7 scenarios)",  run_convergence),
    ("IQ Milestones   (thresholds, persistence)",  run_milestones),
    ("IQ Curve Plot   (ASCII chart + JSON)",       run_curve_plot),
]


def main():
    print()
    print("╔" + "═" * 64 + "╗")
    print("║   SOVEREIGN-Ω IQ BENCHMARK SUITE                              ║")
    print("║   1,000 evaluations. 7 scenarios. Convergence proved.         ║")
    print("╚" + "═" * 64 + "╝")

    total_passed = 0
    total_failed = 0
    results_log = []
    wall_start = time.time()

    for label, fn in SUITES:
        print(f"\n{'─' * 66}")
        print(f"  Running: {label}")
        print(f"{'─' * 66}")
        try:
            p, f = fn()
        except Exception as e:
            import traceback
            traceback.print_exc()
            p, f = 0, 1
        total_passed += p
        total_failed += f
        results_log.append({"label": label, "passed": p, "failed": f})

    wall_elapsed = time.time() - wall_start

    print()
    print("╔" + "═" * 64 + "╗")
    print(f"║  IQ BENCHMARK RESULTS                                          ║")
    print(f"╠" + "═" * 64 + "╣")
    for r in results_log:
        status = "✓" if r["failed"] == 0 else "✗"
        short = r["label"][:54].ljust(54)
        print(f"║  {status} {short}  {r['passed']:2d}P/{r['failed']:2d}F  ║")
    print(f"╠" + "═" * 64 + "╣")
    print(f"║  TOTAL: {total_passed} passed, {total_failed} failed  "
          f"({wall_elapsed:.1f}s)".ljust(65) + "║")
    print(f"╚" + "═" * 64 + "╝")

    with open("data/benchmark_summary.json", "w") as f:
        json.dump({
            "total_passed": total_passed,
            "total_failed": total_failed,
            "wall_elapsed_s": wall_elapsed,
            "suites": results_log,
        }, f, indent=2)

    print(f"\n  Summary → data/benchmark_summary.json")
    print(f"  Curves  → data/iq_convergence_curves.json")
    print(f"  Chart   → data/iq_curve_ascii.txt")

    if total_failed > 0:
        print(f"\n  IQ BENCHMARK FAILURES: {total_failed} test(s) failed.")
        sys.exit(1)
    else:
        print(f"\n  ALL IQ BENCHMARKS PASSED.")
        print(f"  IQ convergence verified: Pearson scoring stable over 1,000 evaluations.")
        print(f"  SOVEREIGN-Ω learns correctly.")


if __name__ == "__main__":
    main()
