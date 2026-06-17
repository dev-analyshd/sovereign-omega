"""
IQ Curve Plot: Generates a text-art convergence chart and saves JSON data
for all 7 win-rate scenarios across 1,000 evaluations.
Output: data/iq_convergence_curves.json  (machine-readable)
        data/iq_curve_ascii.txt           (human-readable chart)
"""
import sys
import os
import math
import random
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

N_EVALS = 1_000
SAMPLE_POINTS = [1, 5, 10, 25, 50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
RANDOM_SEED = 271828


def run_scenario(label: str, win_rate: float, rng: random.Random) -> list:
    """Returns IQ sampled at SAMPLE_POINTS."""
    from learning.iq_scorer import IQScorer
    scorer = IQScorer()
    domain = label.replace(" ", "_").lower()[:20]
    iq_at_samples = []
    sample_idx = 0

    for i in range(N_EVALS):
        won = rng.random() < win_rate
        pnl = rng.uniform(0.005, 0.020) if won else -rng.uniform(0.005, 0.015)
        scorer.record_outcome(domain, won, pnl)

        if sample_idx < len(SAMPLE_POINTS) and (i + 1) == SAMPLE_POINTS[sample_idx]:
            iq_at_samples.append(scorer.get_iq(domain))
            sample_idx += 1

    return iq_at_samples


def ascii_chart(curves: dict, width: int = 60, height: int = 20) -> str:
    """Render a simple ASCII convergence chart."""
    all_vals = [v for pts in curves.values() for v in pts if v is not None]
    lo = max(0, min(all_vals) - 5)
    hi = min(200, max(all_vals) + 5)
    y_range = hi - lo

    lines = []
    lines.append(f"  IQ Convergence (N=1 to 1,000 evaluations)")
    lines.append(f"  {'─' * (width + 8)}")

    symbols = {
        "Perfect mastery":   "★",
        "Strong performer":  "▲",
        "Mixed (55%)":       "●",
        "Baseline (50%)":    "─",
        "Below average":     "○",
        "Poor performer":    "▽",
        "Zero wins":         "✕",
    }

    grid = [[" "] * width for _ in range(height)]
    x_positions = list(range(len(SAMPLE_POINTS)))

    for label, pts in curves.items():
        sym = symbols.get(label, "?")
        for xi, val in zip(x_positions, pts):
            if val is None:
                continue
            x = int(xi / (len(SAMPLE_POINTS) - 1) * (width - 1))
            y = int((1 - (val - lo) / y_range) * (height - 1))
            y = max(0, min(height - 1, y))
            x = max(0, min(width - 1, x))
            grid[y][x] = sym

    for row_i, row in enumerate(grid):
        iq_val = hi - (row_i / (height - 1)) * y_range
        lines.append(f"  {iq_val:5.0f} │{''.join(row)}")

    lines.append(f"        └{'─' * width}")
    lines.append(f"         {'1':^{width//4}}{'100':^{width//4}}{'500':^{width//4}}{'1000':^{width//4}}")
    lines.append(f"                               N (evaluations)")
    lines.append(f"")
    lines.append(f"  Legend:")
    for label, sym in symbols.items():
        final_iq = curves[label][-1] if curves[label] else 0
        lines.append(f"    {sym}  {label:<22s}  final IQ = {final_iq:.1f}")
    return "\n".join(lines)


def main():
    rng = random.Random(RANDOM_SEED)

    scenarios = [
        ("Perfect mastery",   1.00),
        ("Strong performer",  0.70),
        ("Mixed (55%)",       0.55),
        ("Baseline (50%)",    0.50),
        ("Below average",     0.40),
        ("Poor performer",    0.25),
        ("Zero wins",         0.00),
    ]

    print(f"\n{'═' * 66}")
    print(f"  IQ CONVERGENCE CURVE GENERATOR — {N_EVALS} evaluations")
    print(f"{'═' * 66}")

    curves = {}
    for label, win_rate in scenarios:
        pts = run_scenario(label, win_rate, rng)
        curves[label] = pts
        print(f"  {label:<22s} (win={win_rate:.0%}): "
              f"IQ @ N=50 = {pts[SAMPLE_POINTS.index(50)]:.1f},  "
              f"N=1000 = {pts[-1]:.1f}")

    # ASCII chart
    chart = ascii_chart(curves)
    print(f"\n{chart}")

    # Save JSON
    data = {
        "sample_points": SAMPLE_POINTS,
        "n_evals": N_EVALS,
        "curves": {label: [round(v, 4) for v in pts] for label, pts in curves.items()},
    }
    with open("data/iq_convergence_curves.json", "w") as f:
        json.dump(data, f, indent=2)

    with open("data/iq_curve_ascii.txt", "w") as f:
        f.write(chart)

    print(f"\n  Saved: data/iq_convergence_curves.json")
    print(f"  Saved: data/iq_curve_ascii.txt")

    # Spot-check assertions
    errors = []
    perfect_final = curves["Perfect mastery"][-1]
    zero_final    = curves["Zero wins"][-1]
    baseline_final = curves["Baseline (50%)"][-1]

    if perfect_final <= zero_final:
        errors.append(f"Perfect ({perfect_final:.1f}) ≤ Zero ({zero_final:.1f})")
    if not (85 <= baseline_final <= 115):
        errors.append(f"Baseline IQ={baseline_final:.1f} not near 100")
    if perfect_final <= 130:
        errors.append(f"Perfect IQ={perfect_final:.1f} should be > 130")
    if zero_final >= 70:
        errors.append(f"Zero IQ={zero_final:.1f} should be < 70")

    if errors:
        print(f"\n  CURVE ASSERTIONS FAILED: {errors}")
        return 1
    else:
        print(f"\n  PASS: Convergence curves match expected ordering and bounds")
        return 0


if __name__ == "__main__":
    sys.exit(main())
