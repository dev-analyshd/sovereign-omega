"""
Adversarial tests: PerceptualPlane entropy attacks.
Rule: P(t) = 0.0 (hard floor) when H/H_max < 0.35.
Tests: uniform noise, constant signal, single spike, tiny channel.
"""
import sys
import os
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class TestPerceptualAttacks:
    def setup(self):
        from planes.perceptual import PerceptualPlane
        self.plane = PerceptualPlane()

    def test_constant_signal_zero(self):
        """All identical values → zero entropy → P(t) = 0.0"""
        self.setup()
        score = self.plane.compute({"ch": [1.0] * 50})
        assert score == 0.0, f"FAIL: Constant signal should be 0.0, got {score}"
        print(f"  PASS: Constant signal [1.0 × 50] → P(t)={score:.4f}")

    def test_high_entropy_signal_nonzero(self):
        """Uniformly distributed values → high entropy → P(t) > 0.35"""
        self.setup()
        random.seed(42)
        vals = [random.uniform(0.01, 1.0) for _ in range(100)]
        score = self.plane.compute({"ch": vals})
        assert score > 0.35, f"FAIL: High-entropy signal should be > 0.35, got {score}"
        print(f"  PASS: Uniform distribution → P(t)={score:.4f}")

    def test_single_spike_low_entropy(self):
        """One large value among many zeros → very low entropy → P(t) = 0.0"""
        self.setup()
        vals = [0.0] * 99 + [1000.0]
        score = self.plane.compute({"ch": vals})
        assert score == 0.0, f"FAIL: Single spike should be low entropy → 0.0, got {score}"
        print(f"  PASS: Single spike [0×99, 1000] → P(t)={score:.4f}")

    def test_two_value_binary_signal(self):
        """Only two distinct values → low entropy → likely floored"""
        self.setup()
        vals = [0.0, 1.0] * 50
        score = self.plane.compute({"ch": vals})
        # Binary signal: H = 1 bit, H_max = log2(100) ≈ 6.6 bits → ratio ≈ 0.15 < 0.35
        assert score == 0.0, f"FAIL: Binary signal should floor to 0.0, got {score}"
        print(f"  PASS: Binary signal [0,1]×50 → P(t)={score:.4f}")

    def test_empty_channels_zero(self):
        """Empty input → P(t) = 0.0"""
        self.setup()
        score = self.plane.compute({})
        assert score == 0.0, f"FAIL: Empty channels should be 0.0, got {score}"
        print(f"  PASS: Empty channels → P(t)={score:.4f}")

    def test_multi_channel_fusion(self):
        """Multiple channels merged → should have higher entropy than single"""
        self.setup()
        random.seed(123)
        channels = {f"ch{i}": [random.uniform(0, 1) for _ in range(25)] for i in range(4)}
        score = self.plane.compute(channels)
        assert score >= 0.0 and score <= 1.0, f"FAIL: Score out of range: {score}"
        print(f"  PASS: 4 channels (25 samples each) → P(t)={score:.4f}")

    def test_all_negative_values(self):
        """Negative values — magnitude-based entropy should still work."""
        self.setup()
        random.seed(99)
        vals = [-random.uniform(0.01, 1.0) for _ in range(50)]
        score = self.plane.compute({"ch": vals})
        assert 0.0 <= score <= 1.0, f"FAIL: Negative values produced out-of-range {score}"
        print(f"  PASS: All-negative uniform → P(t)={score:.4f}")

    def test_single_value_is_zero(self):
        """Single value in channel → H_max = 0 → P(t) = 0.0"""
        self.setup()
        score = self.plane.compute({"ch": [42.0]})
        assert score == 0.0, f"FAIL: Single value should be 0.0, got {score}"
        print(f"  PASS: Single value → P(t)={score:.4f}")

    def test_score_bounded_zero_to_one(self):
        """P(t) must always be in [0, 1]."""
        self.setup()
        for trial in range(20):
            random.seed(trial)
            vals = [random.gauss(0, 1) for _ in range(random.randint(2, 200))]
            score = self.plane.compute({"ch": vals})
            assert 0.0 <= score <= 1.0, f"FAIL: P(t)={score} out of [0,1] on trial {trial}"
        print(f"  PASS: P(t) bounded in [0,1] across 20 random trials")

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
    print(" ADVERSARIAL: PerceptualPlane Entropy Attacks")
    print("=" * 60)
    suite = TestPerceptualAttacks()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
