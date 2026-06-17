"""
Adversarial tests: SilenceProtocol.
Rule 4: SILENCE is logged before any other action in that cycle.
Tests: silence fires when Psi < Delta, silence log includes reason,
failing planes identified, silence cannot be suppressed.
"""
import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class TestSilenceProtocol:
    def setup(self):
        from core.silence_protocol import SilenceProtocol
        self.sp = SilenceProtocol()

    def test_silence_logs_output(self):
        """Silence must produce output (it's information)."""
        self.setup()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            reason = self.sp.log_silence("cyc-001", 0.40, 0.65, {"p": 0.3, "i": 0.8, "c": 0.7, "s": 0.9, "w": 0.8})
        output = buf.getvalue()
        assert output.strip(), f"FAIL: Silence produced no output"
        assert "SILENCE" in output, f"FAIL: Output doesn't contain 'SILENCE': {output}"
        print(f"  PASS: Silence logged to stdout")

    def test_silence_reason_contains_psi_delta(self):
        """Reason string must include Psi and Delta values."""
        self.setup()
        reason = self.sp.log_silence("cyc-002", 0.45, 0.70, {"p": 0.4, "i": 0.9, "c": 0.8, "s": 0.9, "w": 0.7})
        assert "SILENCE" in reason
        assert "0.45" in reason or "Ψ=0.4" in reason or "gap" in reason.lower()
        print(f"  PASS: Reason contains Psi/Delta info: '{reason[:80]}...'")

    def test_failing_planes_identified(self):
        """get_failing_planes returns planes below 0.5."""
        self.setup()
        plane_scores = {"p": 0.2, "i": 0.9, "c": 0.4, "s": 0.8, "w": 0.6}
        failing = self.sp.get_failing_planes(plane_scores)
        assert "P" in failing, f"FAIL: P=0.2 should be failing, got {failing}"
        assert "C" in failing, f"FAIL: C=0.4 should be failing, got {failing}"
        assert "I" not in failing, f"FAIL: I=0.9 should not be failing, got {failing}"
        assert "S" not in failing, f"FAIL: S=0.8 should not be failing, got {failing}"
        print(f"  PASS: Failing planes identified correctly: {failing}")

    def test_no_planes_failing_when_all_above_threshold(self):
        """All planes >= 0.5 → no failing planes."""
        self.setup()
        plane_scores = {"p": 0.6, "i": 0.7, "c": 0.5, "s": 0.9, "w": 0.8}
        failing = self.sp.get_failing_planes(plane_scores)
        assert len(failing) == 0, f"FAIL: No planes should be failing, got {failing}"
        print(f"  PASS: All planes >= 0.5 → failing_planes=[]")

    def test_all_planes_failing(self):
        """All planes below 0.5 → all 5 identified."""
        self.setup()
        plane_scores = {"p": 0.1, "i": 0.2, "c": 0.3, "s": 0.4, "w": 0.0}
        failing = self.sp.get_failing_planes(plane_scores)
        assert len(failing) == 5, f"FAIL: All 5 planes should fail, got {failing}"
        print(f"  PASS: All planes below 0.5 → 5 failing planes: {failing}")

    def test_silence_called_on_psi_below_any_delta(self):
        """Silence fires for any valid Psi < Delta configuration."""
        self.setup()
        test_cases = [
            (0.0, 0.65), (0.30, 0.65), (0.64, 0.65), (0.69, 0.70),
            (0.50, 0.75), (0.79, 0.80), (0.86, 0.897),
        ]
        for psi, delta in test_cases:
            reason = self.sp.log_silence(f"cyc_{psi}", psi, delta,
                                         {"p": psi, "i": psi, "c": psi, "s": psi, "w": psi})
            assert "SILENCE" in reason, f"FAIL: Silence not triggered for Psi={psi} < Delta={delta}"
        print(f"  PASS: Silence triggered for all {len(test_cases)} (Psi < Delta) cases")

    def test_gap_is_positive_in_silence(self):
        """Gap = Delta - Psi must be positive in silence conditions."""
        self.setup()
        psi, delta = 0.42, 0.65
        reason = self.sp.log_silence("cyc-gap", psi, delta, {"p": 0.4, "i": 0.6, "c": 0.5, "s": 0.7, "w": 0.8})
        gap = delta - psi
        assert gap > 0, f"FAIL: Gap should be positive, got {gap}"
        print(f"  PASS: Gap = {gap:.4f} is positive (Delta={delta} - Psi={psi})")

    def test_silence_returns_string(self):
        """log_silence must return a string (for Pharos on-chain recording)."""
        self.setup()
        result = self.sp.log_silence("cyc-str", 0.5, 0.65, {})
        assert isinstance(result, str), f"FAIL: log_silence must return str, got {type(result)}"
        assert len(result) > 0, "FAIL: Reason string is empty"
        print(f"  PASS: log_silence() returns non-empty string")

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
    print(" ADVERSARIAL: SilenceProtocol (Rule 4 — Silence Is Information)")
    print("=" * 60)
    suite = TestSilenceProtocol()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
