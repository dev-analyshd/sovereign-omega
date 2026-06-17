class RiskManager:
    """
    Hard limits. Rule 7: Never > 2% per trade. Rule 8: 6% daily loss = pause.
    These are not configurable at runtime. No override. No exception.
    """

    MAX_POSITION_PCT = 0.02
    MAX_DAILY_LOSS_PCT = 0.06
    MAX_OPEN_TRADES = 3
    MIN_RISK_REWARD = 1.5

    def __init__(self):
        self.daily_loss = 0.0
        self.open_trades = 0
        self.trading_paused = False

    async def get_available_capital(self) -> float:
        try:
            from pharos.chain_client import PharosClient
            client = PharosClient()
            return await client.get_vault_balance()
        except Exception:
            return 0.0

    def passes_risk_check(
        self,
        position_size: float,
        capital: float,
        stop_loss: float,
        entry_price: float,
    ) -> bool:
        if self.trading_paused:
            print("[RISK] Trading paused due to daily loss limit.")
            return False

        if self.open_trades >= self.MAX_OPEN_TRADES:
            print(f"[RISK] Max {self.MAX_OPEN_TRADES} open trades reached.")
            return False

        if capital <= 0:
            print("[RISK] No capital available.")
            return False

        position_pct = position_size / capital
        if position_pct > self.MAX_POSITION_PCT:
            print(f"[RISK] Position {position_pct:.2%} exceeds max {self.MAX_POSITION_PCT:.2%}")
            return False

        potential_loss = abs(entry_price - stop_loss)
        if potential_loss <= 0:
            return False

        potential_gain = potential_loss * self.MIN_RISK_REWARD
        if potential_gain / entry_price < 0.005:
            print(f"[RISK] R:R too low. Need at least {self.MIN_RISK_REWARD}:1")
            return False

        return True

    def record_trade_loss(self, loss_pct: float):
        self.daily_loss += loss_pct
        if self.daily_loss >= self.MAX_DAILY_LOSS_PCT:
            self.trading_paused = True
            print(f"[RISK] Daily loss {self.daily_loss:.2%} hit limit. Trading paused.")

    def daily_reset(self):
        self.daily_loss = 0.0
        self.trading_paused = False
        print("[RISK] Daily limits reset.")
