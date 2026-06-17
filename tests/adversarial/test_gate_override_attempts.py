"""
Adversarial tests: ActionGate override attempts.
Rule 3: Gate has no override. No bypass. No exception. Period.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class TestGateOverrideAttempts:
    def test_psi_below_delta_gate_stays_closed(self):
        """Psi = 0.30, Delta = 0.65 → gate MUST be closed."""
        from core.action_gate import ActionGate
        g = ActionGate()
        delta = g.compute_threshold(0.0, 0.0)
        assert not g.is_open(0.30, delta), \
            f"FAIL: Psi=0.30 < Delta={delta:.4f} but gate opened"
        print(f"  PASS: Psi=0.30 < Delta={delta:.4f} → gate CLOSED")

    def test_psi_exactly_at_delta_gate_opens(self):
        """Psi == Delta exactly → gate must open (≥ not >)."""
        from core.action_gate import ActionGate
        g = ActionGate()
        delta = g.compute_threshold(0.0, 0.0)
        assert g.is_open(delta, delta), \
            f"FAIL: Psi==Delta should open gate (threshold is >=)"
        print(f"  PASS: Psi=Delta={delta:.4f} → gate OPEN (≥ semantics)")

    def test_psi_one_epsilon_below_delta_gate_closed(self):
        """Psi = Delta - epsilon → gate must be closed."""
        from core.action_gate import ActionGate
        g = ActionGate()
        delta = g.compute_threshold(0.0, 0.0)
        epsilon = 1e-10
        psi = delta - epsilon
        assert not g.is_open(psi, delta), \
            f"FAIL: Psi={psi:.12f} < Delta={delta:.12f} but gate opened"
        print(f"  PASS: Psi=Delta-ε → gate CLOSED (no floating point bypass)")

    def test_max_delta_not_exceedable(self):
        """Delta can never exceed 0.897 regardless of inputs."""
        from core.action_gate import ActionGate
        g = ActionGate()
        for v in [0.0, 0.5, 1.0, 10.0, 100.0, 1e9]:
            for n in [0.0, 0.5, 1.0, 10.0, 100.0, 1e9]:
                delta = g.compute_threshold(v, n)
                assert delta <= g.MAX_DELTA, \
                    f"FAIL: Delta={delta:.6f} exceeded MAX_DELTA={g.MAX_DELTA} at v={v}, n={n}"
        print(f"  PASS: Delta never exceeds {g.MAX_DELTA} under any (volatility, novelty) inputs")

    def test_delta_base_unchanged_at_zero_inputs(self):
        """With zero volatility and novelty, Delta equals Δ_base exactly."""
        from core.action_gate import ActionGate
        g = ActionGate()
        delta = g.compute_threshold(0.0, 0.0)
        assert abs(delta - g.DELTA_BASE) < 1e-12, \
            f"FAIL: Delta={delta} != DELTA_BASE={g.DELTA_BASE}"
        print(f"  PASS: Zero inputs → Delta = DELTA_BASE = {g.DELTA_BASE}")

    def test_negative_psi_gate_closed(self):
        """Psi = -0.5 (adversarial invalid input) → gate must stay closed."""
        from core.action_gate import ActionGate
        g = ActionGate()
        delta = g.compute_threshold(0.2, 0.5)
        assert not g.is_open(-0.5, delta), \
            f"FAIL: Negative Psi should never open gate, got open"
        print(f"  PASS: Psi=-0.5 (adversarial) → gate CLOSED")

    def test_psi_greater_than_1_still_works(self):
        """Psi > 1.0 (theoretical max violation) → gate opens if above delta."""
        from core.action_gate import ActionGate
        g = ActionGate()
        delta = g.compute_threshold(0.0, 0.0)
        assert g.is_open(1.5, delta), \
            f"FAIL: Psi=1.5 > Delta={delta} should open gate"
        print(f"  PASS: Psi=1.5 > Delta={delta} → gate OPEN (numeric edge case)")

    def test_trading_gate_25pct_higher(self):
        """Trading requires 25% higher coherence than general action (Rule 12)."""
        from core.action_gate import ActionGate
        g = ActionGate()
        TRADE_MULTIPLIER = 1.25
        delta_base = g.compute_threshold(0.3, 0.5)
        delta_trade = min(delta_base * TRADE_MULTIPLIER, 0.95)
        # A Psi that passes general gate but fails trading gate
        psi_just_passes_general = delta_base + 0.001
        passes_general = g.is_open(psi_just_passes_general, delta_base)
        passes_trade = g.is_open(psi_just_passes_general, delta_trade)
        assert passes_general, "FAIL: Psi should pass general gate"
        assert not passes_trade, f"FAIL: Same Psi should fail trading gate (Delta_trade={delta_trade:.4f})"
        print(f"  PASS: Psi={psi_just_passes_general:.4f} passes general (Δ={delta_base:.4f}) but fails trade (Δ={delta_trade:.4f})")

    def test_social_gate_70pct_threshold(self):
        """Social gate requires Psi >= 0.70 (Rule 5/13)."""
        DELTA_SOCIAL = 0.70
        from core.action_gate import ActionGate
        g = ActionGate()
        assert not g.is_open(0.699, DELTA_SOCIAL), "FAIL: Psi=0.699 should fail social gate"
        assert g.is_open(0.700, DELTA_SOCIAL), "FAIL: Psi=0.700 should pass social gate"
        assert g.is_open(0.701, DELTA_SOCIAL), "FAIL: Psi=0.701 should pass social gate"
        print(f"  PASS: Social gate Δ=0.70: {g.is_open(0.699, 0.70)}=False, {g.is_open(0.700, 0.70)}=True")

    def test_weights_invariant_under_any_scenario(self):
        """Plane weights must always sum to exactly 1.0 (assert on every call)."""
        from core.coherence_engine import CoherenceEngine
        e = CoherenceEngine()
        total = e.W_P + e.W_I + e.W_C + e.W_S + e.W_W
        assert abs(total - 1.0) < 1e-12, f"FAIL: Weights sum to {total:.15f}"
        print(f"  PASS: Weights always sum to 1.0 (sum={total:.15f})")

    def run_all(self):
        tests = [m for m in dir(self) if m.startswith("test_")]
        passed = 0
        failed = 0
        for t in tests:
            try:
                getattr(self, t)()
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {t}: {e}")
                failed += 1
            except Exception as e:
                import traceback
                print(f"  ✗ {t}: EXCEPTION: {e}")
                traceback.print_exc()
                failed += 1
        return passed, failed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" ADVERSARIAL: ActionGate Override Attempts")
    print("=" * 60)
    suite = TestGateOverrideAttempts()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
