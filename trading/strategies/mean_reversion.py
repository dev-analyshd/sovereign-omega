from typing import Optional


class MeanReversionStrategy:
    """
    Fade extremes. Long when RSI < 30 (oversold). Short when RSI > 70 (overbought).
    Requires ATR confirmation to avoid low-volatility false signals.
    """

    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    MIN_ATR_NORMALIZED = 0.002

    def evaluate(self, df) -> Optional[str]:
        if df is None or len(df) < 20:
            return None

        close = df["close"].iloc[-1]
        atr = df.get("atr_14", None)
        rsi = df.get("rsi_14", None)

        if atr is None or rsi is None:
            return None

        atr_val = float(atr.iloc[-1])
        rsi_val = float(rsi.iloc[-1])
        atr_normalized = atr_val / (float(close) + 1e-9)

        if atr_normalized < self.MIN_ATR_NORMALIZED:
            return None

        if rsi_val < self.RSI_OVERSOLD:
            return "LONG"
        elif rsi_val > self.RSI_OVERBOUGHT:
            return "SHORT"

        return None
