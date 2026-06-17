from typing import Optional


class MomentumStrategy:
    """
    Trend-following. Long when price > EMA20 and RSI in 40-70 range.
    Short when price < EMA20 and RSI in 30-60 range.
    """

    def evaluate(self, df) -> Optional[str]:
        if df is None or len(df) < 20:
            return None

        close = df["close"].iloc[-1]
        ema20 = df["close"].ewm(span=20, adjust=False).mean().iloc[-1]

        rsi = df.get("rsi_14", None)
        if rsi is None:
            return None
        rsi_val = float(rsi.iloc[-1]) if hasattr(rsi, "iloc") else 50.0

        if close > ema20 and 40 <= rsi_val <= 70:
            return "LONG"
        elif close < ema20 and 30 <= rsi_val <= 60:
            return "SHORT"
        return None
