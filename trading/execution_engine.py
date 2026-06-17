class ExecutionEngine:
    """Executes trades on-chain via SovereignVault on Pharos."""

    def __init__(self):
        try:
            from pharos.chain_client import PharosClient
            self.client = PharosClient()
        except Exception as e:
            print(f"[EXEC] Pharos client init failed: {e}. Running in simulation mode.")
            self.client = None

    async def execute_trade(
        self,
        trade_id: str,
        symbol: str,
        direction: str,
        size: float,
        entry_price: float,
        stop_loss: float,
        psi: float,
        delta: float,
    ) -> str:
        if self.client is None:
            print(f"[EXEC SIM] Trade {trade_id}: {direction} {symbol} size={size:.4f}")
            return f"sim_{trade_id[:8]}"

        trade_id_bytes = bytes.fromhex(trade_id.replace("-", ""))
        return await self.client.vault_open_trade(
            trade_id=trade_id_bytes,
            symbol=symbol,
            direction=direction,
            size_scaled=int(size * 1e18),
            entry_price_scaled=int(entry_price * 1e18),
            psi_scaled=int(psi * 1e18),
            delta_scaled=int(delta * 1e18),
        )

    async def record_silenced_trade(self, psi: float, delta: float):
        if self.client is None:
            return
        await self.client.vault_record_silence(
            psi_scaled=int(psi * 1e18),
            delta_scaled=int(delta * 1e18),
        )
