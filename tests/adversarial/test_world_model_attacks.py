"""
Adversarial tests: WorldModelPlane anomaly injection.
Rule 11: Any z-score > 3.0 → W(t) = 0.0 immediately. No softening.
"""
import sys
import os
import math
import random
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class TestWorldModelAttacks:
    def setup(self):
        from planes.world_model import WorldModelPlane
        self.plane = WorldModelPlane()

    def _seed_history(self, plane, key, n=60, base=100.0, noise=2.0):
        """Seed the plane history with stable values."""
        for i in range(n):
            val = base + random.gauss(0, noise)
            plane.compute({key: val})

    def test_massive_spike_is_hard_zero(self):
        """Price 100x normal → z >> 3.0 → W(t) = 0.0"""
        self.setup()
        self._seed_history(self.plane, "price", n=80, base=100.0, noise=1.0)
        score = self.plane.compute({"price": 10000.0})
        assert score == 0.0, f"FAIL: Massive spike should be hard zero, got {score}"
        print(f"  PASS: Massive spike (100x) → W(t)={score:.4f} (hard zero)")

    def test_gradual_drift_no_zero(self):
        """Slow price drift — no single point exceeds z=3.0"""
        self.setup()
        for i in range(100):
            self.plane.compute({"price": 100.0 + i * 0.5})
        score = self.plane.compute({"price": 151.0})
        assert score > 0.0, f"FAIL: Gradual drift should not trigger hard zero, got {score}"
        print(f"  PASS: Gradual drift → W(t)={score:.4f} (no hard zero)")

    def test_exactly_3sigma_spike(self):
        """A value exactly at 3σ boundary → should trigger zero (boundary condition)"""
        self.setup()
        vals = [100.0 + random.gauss(0, 1.0) for _ in range(80)]
        for v in vals:
            self.plane.compute({"price": v})
        mu = statistics.mean(vals)
        sigma = statistics.stdev(vals)
        spike_val = mu + 3.001 * sigma
        score = self.plane.compute({"price": spike_val})
        assert score == 0.0, f"FAIL: z > 3.0 should be hard zero, got {score}"
        print(f"  PASS: z=3.001 spike → W(t)={score:.4f} (hard zero)")

    def test_just_below_3sigma_no_zero(self):
        """A value at 2.9σ → should NOT trigger hard zero"""
        self.setup()
        vals = [100.0 + random.gauss(0, 1.0) for _ in range(80)]
        for v in vals:
            self.plane.compute({"price": v})
        mu = statistics.mean(vals)
        sigma = statistics.stdev(vals)
        val_2_9 = mu + 2.9 * sigma
        score = self.plane.compute({"price": val_2_9})
        assert score > 0.0, f"FAIL: z=2.9 should not be hard zero, got {score}"
        print(f"  PASS: z=2.9 → W(t)={score:.4f} (above zero)")

    def test_one_anomalous_channel_among_many_normal(self):
        """5 channels normal, 1 anomalous → the anomaly alone triggers hard zero"""
        self.setup()
        for i in range(60):
            self.plane.compute({
                "ch1": 100.0 + random.gauss(0, 1),
                "ch2": 200.0 + random.gauss(0, 2),
                "ch3": 50.0 + random.gauss(0, 0.5),
                "ch4": 300.0 + random.gauss(0, 3),
                "ch5": 75.0 + random.gauss(0, 1),
                "anomaly": 10.0 + random.gauss(0, 0.1),
            })
        # Now inject anomaly in ch_anomaly
        score = self.plane.compute({
            "ch1": 100.0,
            "ch2": 200.0,
            "ch3": 50.0,
            "ch4": 300.0,
            "ch5": 75.0,
            "anomaly": 10000.0,  # massive spike on one channel
        })
        assert score == 0.0, f"FAIL: Single anomalous channel should force hard zero, got {score}"
        print(f"  PASS: 1-of-6 anomalous channels → W(t)={score:.4f} (hard zero)")

    def test_negative_spike(self):
        """Sudden massive drop (z < -3) → hard zero"""
        self.setup()
        self._seed_history(self.plane, "price", n=80, base=100.0, noise=1.0)
        score = self.plane.compute({"price": -9000.0})
        assert score == 0.0, f"FAIL: Negative spike z << -3 should be hard zero, got {score}"
        print(f"  PASS: Negative spike (z << -3) → W(t)={score:.4f} (hard zero)")

    def test_flash_crash_sequence(self):
        """Simulate a flash crash: rapid descent beyond 3σ at the bottom"""
        self.setup()
        self._seed_history(self.plane, "price", n=80, base=40000.0, noise=200.0)
        # Rapid decline steps
        for v in [39000, 37000, 35000, 32000]:
            s = self.plane.compute({"price": float(v)})
        # The final crash step is clearly anomalous
        s = self.plane.compute({"price": 1000.0})
        assert s == 0.0, f"FAIL: Flash crash bottom should be hard zero, got {s}"
        print(f"  PASS: Flash crash sequence → W(t)={s:.4f} (hard zero at bottom)")

    def test_no_history_returns_nonzero(self):
        """No history → default 0.7, don't panic without data"""
        self.setup()
        score = self.plane.compute({"price": 40000.0})
        assert score > 0.0, f"FAIL: No history should return default, got {score}"
        print(f"  PASS: No history → W(t)={score:.4f} (default, not zero)")

    def test_constant_signal_no_anomaly(self):
        """Perfectly constant signal → zero variance → should not crash → return nonzero"""
        self.setup()
        for i in range(60):
            self.plane.compute({"price": 100.0})
        score = self.plane.compute({"price": 100.0})
        assert score > 0.0, f"FAIL: Constant signal should not be zero, got {score}"
        print(f"  PASS: Constant signal (σ=0) → W(t)={score:.4f} (handled, nonzero)")

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
    print(" ADVERSARIAL: WorldModelPlane Anomaly Injection")
    print("=" * 60)
    random.seed(42)
    suite = TestWorldModelAttacks()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
