"""
Adversarial tests: InferentialPlane contradiction injection.
Rule 10: No averaging. Hard stop at zero when cosine similarity < -0.3.
"""
import sys
import os
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


def orthogonal_vec(dim=16):
    import hashlib
    raw = hashlib.sha256(os.urandom(16)).digest()
    vec = [(b / 255.0) * 2 - 1 for b in raw[:dim]]
    norm = math.sqrt(sum(x**2 for x in vec))
    return [x / norm for x in vec] if norm > 0 else vec


def opposite_vec(vec):
    return [-x for x in vec]


def slightly_rotated(vec, angle_deg=15):
    """Rotate first two dimensions by angle_deg."""
    import math
    a = math.radians(angle_deg)
    v = list(vec)
    x, y = v[0], v[1]
    v[0] = x * math.cos(a) - y * math.sin(a)
    v[1] = x * math.sin(a) + y * math.cos(a)
    norm = math.sqrt(sum(c**2 for c in v))
    return [c / norm for c in v] if norm > 0 else v


class TestInferentialAttacks:
    def setup(self):
        from planes.inferential import InferentialPlane
        self.plane = InferentialPlane()

    def test_direct_opposition_is_hard_zero(self):
        """Two chains with exactly opposite vectors → I(t) = 0.0"""
        self.setup()
        v = orthogonal_vec(32)
        chains = [
            {"confidence": 0.9, "vector": v},
            {"confidence": 0.9, "vector": opposite_vec(v)},
        ]
        score = self.plane.compute(chains)
        assert score == 0.0, f"FAIL: Direct opposition should be hard zero, got {score}"
        print(f"  PASS: Direct opposition → I(t)={score:.4f} (hard zero)")

    def test_three_chains_one_opposing(self):
        """3 chains, 2 agree, 1 opposes → hard zero (worst pair triggers)"""
        self.setup()
        v = orthogonal_vec(32)
        chains = [
            {"confidence": 0.85, "vector": v},
            {"confidence": 0.80, "vector": slightly_rotated(v, 10)},
            {"confidence": 0.75, "vector": opposite_vec(v)},
        ]
        score = self.plane.compute(chains)
        assert score == 0.0, f"FAIL: Any contradiction should zero out, got {score}"
        print(f"  PASS: 3-chain (2 agree + 1 opposes) → I(t)={score:.4f} (hard zero)")

    def test_five_chains_one_adversarial(self):
        """5 consensus chains + 1 injected adversarial → hard zero"""
        self.setup()
        v = orthogonal_vec(32)
        chains = [{"confidence": 0.82 + i * 0.01, "vector": slightly_rotated(v, i * 5)} for i in range(5)]
        chains.append({"confidence": 0.88, "vector": opposite_vec(v)})
        score = self.plane.compute(chains)
        assert score == 0.0, f"FAIL: Injected adversarial chain should force hard zero, got {score}"
        print(f"  PASS: 5-chain + 1 adversarial → I(t)={score:.4f} (hard zero)")

    def test_near_contradiction_threshold(self):
        """Vectors at exactly the threshold boundary (cosine = -0.30)"""
        self.setup()
        # cosine = -0.3 means the angle between vectors is arccos(-0.3) ≈ 107.5°
        import numpy as np
        v1 = np.zeros(32)
        v1[0] = 1.0
        # Construct v2 with cosine exactly -0.3 with v1
        v2 = np.zeros(32)
        v2[0] = -0.3
        v2[1] = math.sqrt(1 - 0.3**2)
        chains = [
            {"confidence": 0.8, "vector": v1.tolist()},
            {"confidence": 0.8, "vector": v2.tolist()},
        ]
        score = self.plane.compute(chains)
        # cosine == -0.3 is exactly at threshold, should trigger zero
        assert score == 0.0, f"FAIL: Cosine=-0.3 should still trigger hard zero, got {score}"
        print(f"  PASS: Boundary cosine=-0.30 → I(t)={score:.4f} (hard zero)")

    def test_just_above_threshold_no_zero(self):
        """cosine = -0.25 (above threshold) → should NOT be zero"""
        self.setup()
        import numpy as np
        v1 = np.zeros(32)
        v1[0] = 1.0
        v2 = np.zeros(32)
        v2[0] = -0.25
        v2[1] = math.sqrt(1 - 0.25**2)
        chains = [
            {"confidence": 0.8, "vector": v1.tolist()},
            {"confidence": 0.8, "vector": v2.tolist()},
        ]
        score = self.plane.compute(chains)
        assert score > 0.0, f"FAIL: cosine=-0.25 should not trigger hard zero, got {score}"
        print(f"  PASS: cosine=-0.25 (above threshold) → I(t)={score:.4f} (not zero)")

    def test_zero_vector_chains(self):
        """Zero vectors shouldn't crash the system"""
        self.setup()
        chains = [
            {"confidence": 0.5, "vector": [0.0] * 32},
            {"confidence": 0.5, "vector": [0.0] * 32},
        ]
        score = self.plane.compute(chains)
        assert 0.0 <= score <= 1.0, f"FAIL: Zero vectors produced out-of-range {score}"
        print(f"  PASS: Zero vectors → I(t)={score:.4f} (handled gracefully)")

    def test_single_chain_no_contradiction(self):
        """Single chain → no pairs to compare → score based on variance only"""
        self.setup()
        chains = [{"confidence": 0.85, "vector": orthogonal_vec(32)}]
        score = self.plane.compute(chains)
        assert 0.0 <= score <= 1.0
        print(f"  PASS: Single chain → I(t)={score:.4f} (no contradiction possible)")

    def test_empty_chains(self):
        """No chains → should return 0.5 default"""
        self.setup()
        score = self.plane.compute([])
        assert score == 0.5, f"FAIL: Empty chains should return 0.5, got {score}"
        print(f"  PASS: Empty chains → I(t)={score:.4f} (default 0.5)")

    def test_all_identical_vectors_low_variance(self):
        """All 5 chains identical → high I(t) (no contradiction, no variance)"""
        self.setup()
        v = orthogonal_vec(32)
        chains = [{"confidence": 0.80, "vector": v} for _ in range(5)]
        score = self.plane.compute(chains)
        assert score > 0.8, f"FAIL: Identical chains should have high I(t), got {score}"
        print(f"  PASS: All identical vectors → I(t)={score:.4f} (high coherence)")

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
                print(f"  ✗ {t}: EXCEPTION: {e}")
                failed += 1
        return passed, failed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" ADVERSARIAL: InferentialPlane Contradiction Injection")
    print("=" * 60)
    suite = TestInferentialAttacks()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
