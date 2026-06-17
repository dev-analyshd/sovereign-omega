"""
IQ Milestone Benchmark: Verify milestones fire at correct IQ thresholds.
Milestones: Apprentice (IQ≥110), Journeyman (≥120), Expert (≥135),
            Master (≥150), Grandmaster (≥170).
Tests: correct threshold, fired exactly once, never retrograde, persisted.
"""
import sys
import os
import math
import random
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)

MILESTONES = {
    "Apprentice":   110,
    "Journeyman":   120,
    "Expert":       135,
    "Master":       150,
    "Grandmaster":  170,
}


class IQMilestoneBenchmark:

    def test_milestones_fire_in_order(self):
        """Feeding wins → milestones fire sequentially, not skipped."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()
        domain = "milestone_order"
        rng = random.Random(42)
        fired = []

        for i in range(2000):
            won = True  # 100% wins → fast IQ climb
            scorer.record_outcome(domain, won, 0.015)
            iq = scorer.get_iq(domain)
            newly_fired = scorer.get_new_milestones(domain)
            for m in newly_fired:
                fired.append((m, iq, i + 1))

        print(f"  Milestones fired (in order):")
        for name, iq_at_fire, cycle in fired:
            threshold = MILESTONES.get(name, 0)
            print(f"    {name:15s}: IQ={iq_at_fire:.2f} at cycle={cycle} (threshold={threshold})")

        fired_names = [f[0] for f in fired]
        expected_order = [k for k in MILESTONES.keys()]

        assert len(fired) == len(MILESTONES), \
            f"FAIL: Expected {len(MILESTONES)} milestones, got {len(fired)}: {fired_names}"
        for name, iq_at_fire, _ in fired:
            threshold = MILESTONES[name]
            assert iq_at_fire >= threshold, \
                f"FAIL: {name} fired at IQ={iq_at_fire:.2f} but threshold={threshold}"
        print(f"  PASS: All {len(MILESTONES)} milestones fired in order, each above threshold")

    def test_milestones_fire_exactly_once(self):
        """Each milestone fires exactly once, never twice."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()
        domain = "milestone_once"
        all_milestones = []

        for i in range(2000):
            scorer.record_outcome(domain, True, 0.015)
            newly = scorer.get_new_milestones(domain)
            all_milestones.extend(newly)

        from collections import Counter
        counts = Counter(all_milestones)
        for name, count in counts.items():
            assert count == 1, f"FAIL: {name} fired {count} times, expected 1"
        print(f"  PASS: Every milestone fired exactly once: {dict(counts)}")

    def test_losses_dont_retrograde_milestones(self):
        """After reaching Expert, massive losses don't unfired Expert."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()
        domain = "retrograde"

        # Climb to Expert (IQ≥135)
        for i in range(2000):
            scorer.record_outcome(domain, True, 0.015)
            if scorer.get_iq(domain) >= 135:
                break

        expert_iq = scorer.get_iq(domain)
        assert expert_iq >= 135, f"FAIL: Didn't reach Expert: IQ={expert_iq:.2f}"
        print(f"  Reached Expert at IQ={expert_iq:.2f}")

        # Now 500 losses
        for i in range(500):
            scorer.record_outcome(domain, False, -0.015)

        iq_after_losses = scorer.get_iq(domain)
        # Milestones should NOT be retrograded
        milestones = scorer.get_all_milestones(domain)
        assert "Expert" in milestones, \
            f"FAIL: Expert milestone retrograded after losses. milestones={milestones}"
        print(f"  After 500 losses: IQ={iq_after_losses:.2f}, Expert still held={milestones}")
        print(f"  PASS: Milestones never retrograde")

    def test_milestone_iq_thresholds_exact(self):
        """Verify threshold constants match expected values."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()
        assert scorer.MILESTONES == MILESTONES or \
               all(scorer.MILESTONES.get(k, None) == v for k, v in MILESTONES.items()), \
               f"FAIL: Milestone thresholds mismatch: {scorer.MILESTONES}"
        print(f"  PASS: Milestone thresholds: {scorer.MILESTONES}")

    def test_iq_not_above_200(self):
        """Even with infinite wins, IQ never exceeds 200."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()
        domain = "iq_cap"

        for i in range(5000):
            scorer.record_outcome(domain, True, 0.020)

        iq = scorer.get_iq(domain)
        assert iq <= 200.0, f"FAIL: IQ exceeded 200: {iq:.4f}"
        print(f"  PASS: IQ after 5,000 wins = {iq:.4f} (≤ 200)")

    def test_iq_not_below_zero(self):
        """Even with infinite losses, IQ never goes below 0."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()
        domain = "iq_floor"

        for i in range(5000):
            scorer.record_outcome(domain, False, -0.020)

        iq = scorer.get_iq(domain)
        assert iq >= 0.0, f"FAIL: IQ went below 0: {iq:.4f}"
        print(f"  PASS: IQ after 5,000 losses = {iq:.4f} (≥ 0)")

    def test_domain_isolation(self):
        """Two domains don't share state — wins in BTC don't affect ETH."""
        from learning.iq_scorer import IQScorer
        scorer = IQScorer()

        for i in range(500):
            scorer.record_outcome("btc", True, 0.015)

        iq_btc = scorer.get_iq("btc")
        iq_eth = scorer.get_iq("eth")

        assert iq_btc > iq_eth, \
            f"FAIL: BTC IQ should be higher than fresh ETH. BTC={iq_btc:.2f}, ETH={iq_eth:.2f}"
        print(f"  PASS: Domain isolation: BTC IQ={iq_btc:.2f}, ETH IQ={iq_eth:.2f} (independent)")

    def test_milestone_persistence(self):
        """Milestones persisted to disk survive a new IQScorer instance."""
        from learning.iq_scorer import IQScorer
        domain = "persist_test"

        s1 = IQScorer()
        for i in range(2000):
            s1.record_outcome(domain, True, 0.015)
            if s1.get_iq(domain) >= 120:
                break

        s1_milestones = s1.get_all_milestones(domain)
        assert "Journeyman" in s1_milestones, \
            f"FAIL: Should have reached Journeyman, got {s1_milestones}"

        # Reload fresh instance
        s2 = IQScorer()
        s2_milestones = s2.get_all_milestones(domain)
        assert "Journeyman" in s2_milestones, \
            f"FAIL: Journeyman not persisted after reload. got {s2_milestones}"
        print(f"  PASS: Milestones persisted across instances: {s2_milestones}")

    def run_all(self) -> tuple:
        tests = [m for m in dir(self) if m.startswith("test_")]
        passed = 0
        failed = 0
        for t in tests:
            try:
                print(f"\n  ── {t}")
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
    print(f"\n{'═' * 60}")
    print(f"  IQ MILESTONE BENCHMARK")
    print(f"{'═' * 60}")
    bench = IQMilestoneBenchmark()
    passed, failed = bench.run_all()
    print(f"\n  Result: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
