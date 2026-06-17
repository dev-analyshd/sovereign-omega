"""
Adversarial tests: RiskManager hard limits.
Rule 7: Max 2% of vault per trade.
Rule 8: 6% daily loss = trading paused until reset.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.makedirs("data", exist_ok=True)


class TestRiskLimits:
    def setup(self):
        from trading.risk_manager import RiskManager
        self.risk = RiskManager()

    def test_2pct_position_limit_enforced(self):
        """Position at exactly 2.001% of capital → rejected."""
        self.setup()
        capital = 10000.0
        size = capital * 0.02001  # Just over 2%
        entry = 40000.0
        stop = 39000.0
        passes = self.risk.passes_risk_check(size, capital, stop, entry)
        assert not passes, f"FAIL: 2.001% position should be rejected, got {passes}"
        print(f"  PASS: 2.001% position rejected")

    def test_exactly_2pct_passes(self):
        """Position at exactly 2.0% of capital → allowed."""
        self.setup()
        capital = 10000.0
        size = capital * 0.020  # Exactly 2%
        entry = 40000.0
        stop = 38000.0
        passes = self.risk.passes_risk_check(size, capital, stop, entry)
        assert passes, f"FAIL: 2.0% position should be allowed, got {passes}"
        print(f"  PASS: 2.0% position allowed")

    def test_1pct_position_always_passes(self):
        """Position at 1% → always allowed."""
        self.setup()
        capital = 50000.0
        size = capital * 0.01
        entry = 40000.0
        stop = 39000.0
        passes = self.risk.passes_risk_check(size, capital, stop, entry)
        assert passes, f"FAIL: 1% position should always pass, got {passes}"
        print(f"  PASS: 1% position always allowed")

    def test_daily_loss_6pct_pauses_trading(self):
        """After 6% daily loss, all trades must be blocked."""
        self.setup()
        self.risk.record_trade_loss(0.06)
        assert self.risk.trading_paused, "FAIL: Trading should be paused after 6% loss"
        # Any further trade must be blocked
        passes = self.risk.passes_risk_check(100, 10000, 39000, 40000)
        assert not passes, "FAIL: Trade after 6% daily loss should be blocked"
        print(f"  PASS: 6% daily loss → trading paused, all trades blocked")

    def test_daily_loss_accumulates_across_trades(self):
        """3 losses of 2% each = 6% total → pause."""
        self.setup()
        self.risk.record_trade_loss(0.02)
        self.risk.record_trade_loss(0.02)
        assert not self.risk.trading_paused, "FAIL: Should not be paused at 4%"
        self.risk.record_trade_loss(0.02)
        assert self.risk.trading_paused, "FAIL: Should be paused at 6%"
        print(f"  PASS: 2% + 2% + 2% = 6% → trading paused")

    def test_daily_reset_restores_trading(self):
        """daily_reset() must restore trading ability."""
        self.setup()
        self.risk.record_trade_loss(0.10)  # 10% loss
        assert self.risk.trading_paused
        self.risk.daily_reset()
        assert not self.risk.trading_paused, "FAIL: daily_reset should unpause trading"
        assert self.risk.daily_loss == 0.0, "FAIL: daily_reset should zero daily loss"
        passes = self.risk.passes_risk_check(100, 10000, 39000, 40000)
        assert passes, "FAIL: Trade should be allowed after daily reset"
        print(f"  PASS: daily_reset() restores trading (paused=False, daily_loss=0.0)")

    def test_zero_capital_rejected(self):
        """Zero capital → no trades allowed."""
        self.setup()
        passes = self.risk.passes_risk_check(0, 0, 39000, 40000)
        assert not passes, "FAIL: Zero capital should reject all trades"
        print(f"  PASS: Zero capital → all trades rejected")

    def test_max_open_trades_enforced(self):
        """After MAX_OPEN_TRADES open positions, further trades rejected."""
        self.setup()
        self.risk.open_trades = self.risk.MAX_OPEN_TRADES
        passes = self.risk.passes_risk_check(100, 10000, 39000, 40000)
        assert not passes, f"FAIL: Should block at MAX_OPEN_TRADES={self.risk.MAX_OPEN_TRADES}"
        print(f"  PASS: Max {self.risk.MAX_OPEN_TRADES} open trades limit enforced")

    def test_very_large_position_rejected(self):
        """10x capital position → clearly over 2% → rejected."""
        self.setup()
        capital = 10000.0
        size = capital * 10  # 1000% of capital
        passes = self.risk.passes_risk_check(size, capital, 39000, 40000)
        assert not passes, "FAIL: 10x capital position should be rejected"
        print(f"  PASS: 10x capital position rejected")

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
    print(" ADVERSARIAL: RiskManager Hard Limits (Rules 7 & 8)")
    print("=" * 60)
    suite = TestRiskLimits()
    passed, failed = suite.run_all()
    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
