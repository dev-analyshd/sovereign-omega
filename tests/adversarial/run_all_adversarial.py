#!/usr/bin/env python3
"""
Master adversarial test runner.
Runs all attack suites in sequence.
Rules under test:
  Rule 1:  FAISS persists every write
  Rule 2:  Moat (Λ) never decreases
  Rule 3:  Action gate has no override
  Rule 4:  Silence logged before any other action
  Rule 5:  Social requires Ψ ≥ 0.70
  Rule 7:  Max 2% of vault per trade
  Rule 8:  6% daily loss = trading paused
  Rule 10: Contradiction → I(t) = 0.0 hard stop
  Rule 11: z-score > 3.0 → W(t) = 0.0 immediately
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

SUITES = [
    ("InferentialPlane — Contradiction Injection (Rule 10)",
     "tests.adversarial.test_inferential_attacks", "TestInferentialAttacks"),
    ("WorldModelPlane — Anomaly Injection (Rule 11)",
     "tests.adversarial.test_world_model_attacks", "TestWorldModelAttacks"),
    ("MoatAccumulator — Λ Never Decreases (Rule 2)",
     "tests.adversarial.test_moat_attacks", "TestMoatAttacks"),
    ("ActionGate — Override Attempts (Rule 3)",
     "tests.adversarial.test_gate_override_attempts", "TestGateOverrideAttempts"),
    ("PerceptualPlane — Entropy Attacks",
     "tests.adversarial.test_perceptual_attacks", "TestPerceptualAttacks"),
    ("FAISS Persistence — Every Write (Rule 1)",
     "tests.adversarial.test_faiss_persistence", "TestFAISSPersistence"),
    ("SilenceProtocol — Always Fires First (Rule 4)",
     "tests.adversarial.test_silence_logging", "TestSilenceLogging"),
    ("RiskManager — Hard Limits (Rules 7 & 8)",
     "tests.adversarial.test_risk_limits", "TestRiskLimits"),
    ("DualStrand Memory — K+/K- Encoding",
     "tests.adversarial.test_dual_strand", "TestDualStrand"),
]

# Map silence module name correctly
SUITE_CLASS_OVERRIDES = {
    "tests.adversarial.test_silence_logging": "TestSilenceProtocol",
}


def run_suite(label, module_path, class_name):
    import importlib
    try:
        mod = importlib.import_module(module_path)
        cls_name = SUITE_CLASS_OVERRIDES.get(module_path, class_name)
        cls = getattr(mod, cls_name)
        suite = cls()
        passed, failed = suite.run_all()
        return passed, failed
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 0, 1


def main():
    print()
    print("╔" + "═" * 62 + "╗")
    print("║     SOVEREIGN-Ω ADVERSARIAL TEST SUITE                      ║")
    print("║     Truth or silence. The rules are enforced.               ║")
    print("╚" + "═" * 62 + "╝")
    print()

    total_passed = 0
    total_failed = 0
    results = []

    start = time.time()
    for label, module, cls in SUITES:
        print(f"\n{'─' * 60}")
        print(f" {label}")
        print(f"{'─' * 60}")
        p, f = run_suite(label, module, cls)
        results.append((label, p, f))
        total_passed += p
        total_failed += f

    elapsed = time.time() - start

    print()
    print("╔" + "═" * 62 + "╗")
    print(f"║  ADVERSARIAL RESULTS                                         ║")
    print(f"╠" + "═" * 62 + "╣")
    for label, p, f in results:
        status = "✓" if f == 0 else "✗"
        short = label[:48].ljust(48)
        print(f"║  {status} {short}  {p:2d}P/{f:2d}F  ║")
    print(f"╠" + "═" * 62 + "╣")
    print(f"║  TOTAL: {total_passed} passed, {total_failed} failed  ({elapsed:.2f}s)".ljust(63) + "║")
    print(f"╚" + "═" * 62 + "╝")
    print()

    if total_failed > 0:
        print(f"ADVERSARIAL FAILURES DETECTED: {total_failed} test(s) failed.")
        print("The rules must hold. Fix violations before deploying.")
        sys.exit(1)
    else:
        print("ALL ADVERSARIAL TESTS PASSED. Rules enforced under attack conditions.")
        print("SOVEREIGN-Ω is coherent.")


if __name__ == "__main__":
    main()
