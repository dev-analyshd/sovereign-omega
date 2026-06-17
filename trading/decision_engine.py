import math
import uuid
from typing import Optional

from core.coherence_engine import CoherenceEngine
from core.action_gate import ActionGate
from core.moat_accumulator import MoatAccumulator
from core.silence_protocol import SilenceProtocol
from trading.bayesian_updater import BayesianUpdater, compute_kelly_fraction, compute_expected_edge
from trading.market_feed import MarketFeed
from trading.risk_manager import RiskManager
from trading.execution_engine import ExecutionEngine


class TradingDecisionEngine:
    """
    T(t) = [Ψ_trade(t) ≥ Δ_trade(t)] · E_edge(t) · size_scalar(t) · e^(Λ·t)
    Trading requires 25% higher coherence than general action. Rule 12.
    """

    TRADE_DELTA_MULTIPLIER = 1.25

    def __init__(self):
        self.coherence = CoherenceEngine()
        self.gate = ActionGate()
        self.moat = MoatAccumulator()
        self.silence = SilenceProtocol()
        self.bayesian = BayesianUpdater()
        self.market = MarketFeed()
        self.risk = RiskManager()
        self.executor = ExecutionEngine()

    async def evaluate_trade(self, symbol: str, direction: str, strategy: str) -> dict:
        price_channels = await self.market.get_price_channels(symbol)
        env_signals = await self.market.get_market_environment(symbol)

        context = {
            "input_channels": price_channels if price_channels else {"default": [1, 2, 3, 4]},
            "environmental_signals": env_signals,
            "task_type": "trading",
            "volatility": env_signals.get("atr_normalized", 0.3),
            "novelty": 0.5,
        }

        query = f"Should I enter a {direction} position on {symbol} using {strategy} strategy?"
        cycle_id = str(uuid.uuid4())
        plane_scores = await self.coherence.compute_all_planes(query, context, cycle_id)
        psi = plane_scores["psi_total"]

        base_delta = self.gate.compute_threshold(
            volatility=plane_scores["volatility"],
            novelty=plane_scores["novelty"],
        )
        delta_trade = min(base_delta * self.TRADE_DELTA_MULTIPLIER, 0.95)

        if psi < delta_trade:
            reason = self.silence.log_silence(cycle_id, psi, delta_trade, plane_scores)
            await self.executor.record_silenced_trade(psi, delta_trade)
            return {"action": "SILENCE", "reason": reason, "psi": psi, "delta": delta_trade}

        p_win, avg_win, avg_loss, kelly_f = self.bayesian.get_edge_params(symbol, strategy)
        e_edge = compute_expected_edge(p_win, avg_win, avg_loss)

        if e_edge <= 0:
            return {"action": "NO_EDGE", "reason": "Expected edge is negative", "e_edge": e_edge}

        lambda_val = self.moat.get_current_lambda()
        t_norm = self.moat.get_t_normalized()
        t_value = e_edge * kelly_f * math.exp(lambda_val * t_norm)

        df = await self.market.fetch_ohlcv(symbol, "15m", limit=20)
        if df is not None:
            current_price = float(df["close"].iloc[-1])
            atr = float(df["atr_14"].iloc[-1]) if df["atr_14"].iloc[-1] == df["atr_14"].iloc[-1] else current_price * 0.005
        else:
            current_price = 40000.0
            atr = 200.0

        if direction == "LONG":
            stop_loss = current_price - atr * 1.5
        else:
            stop_loss = current_price + atr * 1.5

        capital = await self.risk.get_available_capital()
        if capital <= 0:
            capital = 1.0

        position_size = capital * kelly_f

        if not self.risk.passes_risk_check(position_size, capital, stop_loss, current_price):
            return {"action": "RISK_BLOCKED", "reason": "Risk manager blocked trade"}

        trade_id = str(uuid.uuid4())
        tx_hash = await self.executor.execute_trade(
            trade_id=trade_id,
            symbol=symbol,
            direction=direction,
            size=position_size,
            entry_price=current_price,
            stop_loss=stop_loss,
            psi=psi,
            delta=delta_trade,
        )

        self.moat.accumulate(eta_i=0.8, rho_i=psi, cycle_id=trade_id)

        return {
            "action": "TRADE_OPENED",
            "trade_id": trade_id,
            "symbol": symbol,
            "direction": direction,
            "entry_price": current_price,
            "size": position_size,
            "stop_loss": stop_loss,
            "kelly_fraction": kelly_f,
            "e_edge": e_edge,
            "t_value": t_value,
            "psi": psi,
            "delta_trade": delta_trade,
            "p_win": p_win,
            "pharos_tx": tx_hash,
        }

    async def close_trade_on_outcome(self, trade_id: str, exit_price: float, pnl: float, won: bool, symbol: str = "BTC/USDT", strategy: str = "momentum", size: float = 1.0):
        await self.bayesian.update_after_trade(
            symbol=symbol,
            strategy=strategy,
            won=won,
            pnl_pct=pnl / (size + 1e-9),
        )
        if won and pnl > 0:
            self.moat.accumulate(eta_i=0.9, rho_i=0.8, cycle_id=f"{trade_id}_close")
