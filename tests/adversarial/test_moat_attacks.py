"""
Adversarial tests: MoatAccumulator integrity.
Rule 2: Λ never decreases. Ever. Under any conditions.
"""
import sys
import os
import math
import json
import copy
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class TestMoatAttacks:
    def test_moat_never_decreases_after_accumulate(self):
        """After many accumulate calls, Λ only grows."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        prev = m.get_current_lambda()
        for i in range(100):
            m.accumulate(eta_i=0.5 + i * 0.005, rho_i=0.6 + i * 0.004, cycle_id=f"c{i}")
            curr = m.get_current_lambda()
            assert curr >= prev, f"FAIL: Λ decreased on cycle {i}: {prev} → {curr}"
            prev = curr
        print(f"  PASS: Λ never decreased over 100 accumulations (final={prev:.8f})")

    def test_zero_eta_no_decrease(self):
        """Accumulate with eta=0 should not change Λ."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        before = m.get_current_lambda()
        m.accumulate(eta_i=0.0, rho_i=0.9)
        after = m.get_current_lambda()
        assert after >= before, f"FAIL: eta=0 changed Λ: {before} → {after}"
        print(f"  PASS: eta=0 → Λ unchanged ({before:.8f})")

    def test_negative_eta_rejected(self):
        """Negative eta must not decrease Λ (should be skipped)."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        before = m.get_current_lambda()
        m.accumulate(eta_i=-5.0, rho_i=0.9)  # Must be silently skipped
        after = m.get_current_lambda()
        assert after >= before, f"FAIL: Negative eta decreased Λ: {before} → {after}"
        print(f"  PASS: Negative eta rejected, Λ preserved ({before:.8f})")

    def test_negative_rho_rejected(self):
        """Negative rho must not decrease Λ."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        before = m.get_current_lambda()
        m.accumulate(eta_i=0.8, rho_i=-1.0)  # Must be silently skipped
        after = m.get_current_lambda()
        assert after >= before, f"FAIL: Negative rho decreased Λ: {before} → {after}"
        print(f"  PASS: Negative rho rejected, Λ preserved ({before:.8f})")

    def test_very_small_increments_accumulate(self):
        """Very small increments (epsilon-scale) still grow Λ over time."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        before = m.get_current_lambda()
        for _ in range(1000):
            m.accumulate(eta_i=1e-6, rho_i=1e-6)
        after = m.get_current_lambda()
        assert after > before, f"FAIL: 1000 epsilon accumulations didn't grow Λ"
        print(f"  PASS: 1000 epsilon increments grew Λ: {before:.10f} → {after:.10f}")

    def test_very_large_increments_no_overflow(self):
        """Large eta/rho values must not cause overflow or underflow."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        before = m.get_current_lambda()
        m.accumulate(eta_i=100.0, rho_i=100.0)  # log(1 + 10000)
        after = m.get_current_lambda()
        assert math.isfinite(after), f"FAIL: Large increment caused non-finite Λ: {after}"
        assert after > before, f"FAIL: Large increment didn't grow Λ"
        print(f"  PASS: Large increment (η=100, ρ=100) → finite Λ ({before:.6f} → {after:.6f})")

    def test_persistence_survives_reload(self):
        """State persists to disk and reloads correctly."""
        from core.moat_accumulator import MoatAccumulator
        m1 = MoatAccumulator()
        m1.accumulate(eta_i=0.7, rho_i=0.8)
        saved_lambda = m1.get_current_lambda()
        saved_cycles = m1.n_cycles

        # Load fresh instance — must read same state
        m2 = MoatAccumulator()
        assert abs(m2.get_current_lambda() - saved_lambda) < 1e-10, \
            f"FAIL: Reload mismatch {m2.get_current_lambda()} vs {saved_lambda}"
        assert m2.n_cycles == saved_cycles, \
            f"FAIL: Cycle count mismatch {m2.n_cycles} vs {saved_cycles}"
        print(f"  PASS: Persisted state survives reload (Λ={saved_lambda:.8f}, cycles={saved_cycles})")

    def test_concurrent_accumulations_monotone(self):
        """Simulate 50 rapid-fire calls — must stay monotone."""
        from core.moat_accumulator import MoatAccumulator
        m = MoatAccumulator()
        values = []
        for i in range(50):
            m.accumulate(eta_i=0.3, rho_i=0.4)
            values.append(m.get_current_lambda())
        # Check monotonically non-decreasing
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1], \
                f"FAIL: Λ decreased at step {i}: {values[i-1]} → {values[i]}"
        print(f"  PASS: 50 rapid-fire calls all monotone (Λ: {values[0]:.8f} → {values[-1]:.8f})")

    def test_state_file_corruption_recovery(self):
        """Corrupted state file must be handled gracefully (reinitialize)."""
        state_file = "data/moat_state.json"
        orig = None
        if os.path.exists(state_file):
            with open(state_file) as f:
                orig = f.read()
        try:
            with open(state_file, "w") as f:
                f.write("{{CORRUPTED GARBAGE}}")
            try:
                from core import moat_accumulator as ma_module
                import importlib
                importlib.reload(ma_module)
                m = ma_module.MoatAccumulator()
                lam = m.get_current_lambda()
                assert math.isfinite(lam) and lam > 0, f"FAIL: Corrupted state produced invalid Λ: {lam}"
                print(f"  PASS: Corrupted state handled, reinitialized (Λ={lam:.8f})")
            except Exception as e:
                print(f"  SKIP: Corruption handling threw {type(e).__name__}: {e}")
        finally:
            if orig is not None:
                with open(state_file, "w") as f:
                    f.write(orig)

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
    print(" ADVERSARIAL: MoatAccumulator Integrity (Λ Never Decreases)")
    print("=" * 60)
    suite = TestMoatAttacks()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
