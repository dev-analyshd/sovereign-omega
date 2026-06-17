try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

if PROMETHEUS_AVAILABLE:
    CYCLES_TOTAL = Counter("sovereign_cycles_total", "Total coherence cycles", ["gate_result"])
    SILENCES_TOTAL = Counter("sovereign_silences_total", "Total silence episodes")
    PSI_SCORE = Gauge("sovereign_psi_score", "Current Psi coherence score")
    LAMBDA_VALUE = Gauge("sovereign_lambda_value", "Current Moat coefficient Λ")
    IQ_SCORE = Gauge("sovereign_iq_score", "Current intelligence score IQ(t)")
    TRADES_TOTAL = Counter("sovereign_trades_total", "Total trades", ["direction", "outcome"])
    TRADE_PNL = Histogram("sovereign_trade_pnl", "Trade PnL distribution",
                           buckets=[-0.1, -0.05, -0.02, 0, 0.01, 0.02, 0.05, 0.1, 0.2])
    SOCIAL_POSTS = Counter("sovereign_social_posts_total", "Social posts", ["platform", "silenced"])
else:
    class _NullMetric:
        def inc(self, *a, **kw): pass
        def set(self, *a, **kw): pass
        def observe(self, *a, **kw): pass
        def labels(self, *a, **kw): return self

    CYCLES_TOTAL = _NullMetric()
    SILENCES_TOTAL = _NullMetric()
    PSI_SCORE = _NullMetric()
    LAMBDA_VALUE = _NullMetric()
    IQ_SCORE = _NullMetric()
    TRADES_TOTAL = _NullMetric()
    TRADE_PNL = _NullMetric()
    SOCIAL_POSTS = _NullMetric()


def start_metrics_server(port: int = 9090):
    if PROMETHEUS_AVAILABLE:
        start_http_server(port)
        print(f"[METRICS] Prometheus metrics at :{port}/metrics")
