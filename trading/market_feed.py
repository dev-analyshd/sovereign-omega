import asyncio
from typing import Dict, List

try:
    import ccxt.async_support as ccxt
    import pandas as pd
    import pandas_ta as ta
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False


class MarketFeed:
    """
    Ingests real-time price data from exchanges.
    Computes technical indicators (ATR, RSI, MACD).
    Falls back to mock data if ccxt is unavailable.
    """

    SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    TIMEFRAMES = ["1m", "5m", "15m", "1h"]

    def __init__(self):
        if CCXT_AVAILABLE:
            self.exchange = ccxt.binance({"enableRateLimit": True})
        else:
            self.exchange = None
        self.latest_data = {}

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "15m", limit: int = 100):
        if not CCXT_AVAILABLE or self.exchange is None:
            return self._mock_df(limit)

        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            import pandas as pd
            import pandas_ta as ta

            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)
            df["rsi_14"] = ta.rsi(df["close"], length=14)
            macd = ta.macd(df["close"])
            if macd is not None:
                df["macd"] = macd["MACD_12_26_9"]
                df["signal_line"] = macd["MACDs_12_26_9"]
            self.latest_data[f"{symbol}_{timeframe}"] = df
            return df
        except Exception as e:
            print(f"[MARKET] fetch_ohlcv error: {e}")
            return self._mock_df(limit)

    def _mock_df(self, limit: int = 100):
        import random
        try:
            import pandas as pd
            prices = [40000.0 + random.gauss(0, 500) for _ in range(limit)]
            df = pd.DataFrame({"close": prices, "open": prices, "high": [p + 100 for p in prices],
                               "low": [p - 100 for p in prices], "volume": [1000.0] * limit,
                               "atr_14": [200.0] * limit, "rsi_14": [50.0] * limit})
            return df
        except ImportError:
            return None

    async def get_price_channels(self, symbol: str) -> Dict[str, List[float]]:
        channels = {}
        for tf in ["15m", "1h"]:
            df = await self.fetch_ohlcv(symbol, tf, limit=50)
            if df is not None:
                try:
                    channels[f"price_{tf}"] = df["close"].tolist()
                    channels[f"volume_{tf}"] = df["volume"].tolist()
                except Exception:
                    channels[f"price_{tf}"] = [40000.0] * 50
        return channels

    async def get_market_environment(self, symbol: str) -> Dict[str, float]:
        df = await self.fetch_ohlcv(symbol, "1h", limit=100)
        if df is None:
            return {"price_change_1h": 0.0, "volume_ratio": 1.0, "rsi": 0.5, "atr_normalized": 0.005}
        try:
            latest = df.iloc[-1]
            return {
                "price_change_1h": float((df["close"].iloc[-1] - df["close"].iloc[-4]) / (df["close"].iloc[-4] + 1e-9)),
                "volume_ratio": float(df["volume"].iloc[-1] / (df["volume"].mean() + 1e-9)),
                "rsi": float(latest["rsi_14"]) / 100.0 if latest["rsi_14"] == latest["rsi_14"] else 0.5,
                "atr_normalized": float(latest["atr_14"]) / float(latest["close"] + 1e-9)
                if latest["atr_14"] == latest["atr_14"] else 0.005,
            }
        except Exception:
            return {"price_change_1h": 0.0, "volume_ratio": 1.0, "rsi": 0.5, "atr_normalized": 0.005}

    async def close(self):
        if self.exchange:
            await self.exchange.close()
