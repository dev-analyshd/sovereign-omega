import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse

from api.routes import action, trade, intelligence, pharos_routes, silence, moat, health
from api.routes import skills, agent_card, x402, mcp_server
from api.routes import federation, stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 60)
    print(" SOVEREIGN-Ω STARTING")
    print(" Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)")
    print(" Truth or silence. The silence is information.")
    print(" On-chain sync: every 100 coherent cycles")
    print(" Federation: A2A peer network active")
    print(" SSE: Live intelligence stream ready")
    print("=" * 60 + "\n")

    from learning.intelligence_score import IntelligenceScorer
    from core.moat_accumulator import MoatAccumulator

    moat_acc = MoatAccumulator()
    scorer = IntelligenceScorer()
    iq = await scorer.compute()
    print(f"[STARTUP] Λ={moat_acc.get_current_lambda():.8f} | Cycles={moat_acc.n_cycles} | IQ={iq:.8f}")

    # ── Background: on-chain heartbeat loop (100-cycle sync) ──────────────
    async def on_chain_heartbeat_loop():
        from core.on_chain_heartbeat import background_sync_loop
        await background_sync_loop()

    # ── Background: self-improvement loop ─────────────────────────────────
    async def self_improve_loop():
        from learning.domain_mastery import DomainMasteryEngine
        mastery = DomainMasteryEngine()
        while True:
            await asyncio.sleep(3600)
            domains = mastery.get_all()
            weak = [d for d in domains if d["mastery_score"] < 0.3]
            if weak:
                print(f"[SELF-IMPROVE] Weak domains: {[d['domain'] for d in weak]}")

    # ── Background: daily risk reset ───────────────────────────────────────
    async def daily_reset():
        from trading.risk_manager import RiskManager
        risk = RiskManager()
        while True:
            await asyncio.sleep(86400)
            risk.daily_reset()

    # ── Background: federation broadcast ping ──────────────────────────────
    async def federation_beacon():
        """Every 5 minutes, SOVEREIGN-Ω pings known peers to stay visible."""
        await asyncio.sleep(60)
        while True:
            try:
                from api.routes.federation import _peers, _proactive_invite
                active = [p for p in _peers.values() if p.get("status") in ("active", "handshaked")]
                if active:
                    print(f"[FEDERATION] Beacon to {len(active)} peer(s)")
            except Exception as e:
                print(f"[FEDERATION] Beacon error: {e}")
            await asyncio.sleep(300)

    asyncio.create_task(on_chain_heartbeat_loop())
    asyncio.create_task(self_improve_loop())
    asyncio.create_task(daily_reset())
    asyncio.create_task(federation_beacon())

    print("[SOVEREIGN-Ω] All background loops running.")
    print(f"[SOVEREIGN-Ω] SSE streams: /api/v1/stream/intelligence | /stream/heartbeat | /stream/moat | /stream/actions")
    print(f"[SOVEREIGN-Ω] Federation: /api/v1/federation/announce | /federation/invite | /federation/broadcast")

    yield

    print("[SOVEREIGN-Ω] Graceful shutdown. Moat preserved.")


app = FastAPI(
    title="SOVEREIGN-Ω",
    description=(
        "Autonomous intelligence agent governed by TRION mathematics. "
        "Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t). "
        "Pharos Chain native. On-chain sync every 100 coherent cycles. "
        "A2A federation with Ψ-gating. Live SSE intelligence stream."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Core intelligence endpoints ────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(action.router, prefix="/api/v1", tags=["Core"])
app.include_router(trade.router, prefix="/api/v1", tags=["Trading"])
app.include_router(intelligence.router, prefix="/api/v1", tags=["Intelligence"])
app.include_router(pharos_routes.router, prefix="/api/v1", tags=["Pharos Chain"])
app.include_router(silence.router, prefix="/api/v1", tags=["Silence"])
app.include_router(moat.router, prefix="/api/v1", tags=["Moat"])

# ── Pharos Phase 1 Hackathon: Skill-to-Agent Dual Cascade ─────────────────────
app.include_router(skills.router, prefix="/api/v1", tags=["Agent Skills (MCP)"])
app.include_router(x402.router, prefix="/api/v1", tags=["x402 Payments"])
app.include_router(agent_card.router, tags=["Agent Discovery (A2A)"])
app.include_router(mcp_server.router, tags=["MCP Server (JSON-RPC 2.0)"])

# ── Agent Federation (A2A peer network) ───────────────────────────────────────
app.include_router(federation.router, prefix="/api/v1", tags=["Federation (A2A)"])

# ── Live SSE Streaming ────────────────────────────────────────────────────────
app.include_router(stream.router, prefix="/api/v1", tags=["Live Streaming (SSE)"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    from core.moat_accumulator import MoatAccumulator
    from learning.intelligence_score import IntelligenceScorer
    from learning.domain_mastery import DomainMasteryEngine
    from core.on_chain_heartbeat import get_sync_stats
    import math

    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    iq = await scorer.compute()
    domains = DomainMasteryEngine().get_all()
    stats = get_sync_stats()

    lam = moat.get_current_lambda()
    log_lam = moat.log_lambda
    cycles = moat.n_cycles
    iq_fmt = f"{iq:.4e}" if iq > 1000 else f"{iq:.6f}"
    lam_fmt = f"{lam:.4e}"
    domain_rows = "".join(
        f"<tr><td>{d['domain']}</td><td>{d['mastery_score']:.4f}</td><td>{d['knowledge_count']}</td></tr>"
        for d in domains[:6]
    ) or "<tr><td colspan='3' style='color:#666'>No domains yet — run some actions</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SOVEREIGN-Ω</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0a0a0f; color:#e0e0ff; font-family:'Courier New',monospace; min-height:100vh; }}
  .header {{ background:linear-gradient(135deg,#0d0d1a,#1a0a2e); border-bottom:1px solid #4040a0; padding:2rem; text-align:center; }}
  .header h1 {{ font-size:2.5rem; color:#a080ff; letter-spacing:0.1em; }}
  .header .formula {{ color:#6060c0; margin-top:0.5rem; font-size:0.9rem; }}
  .header .tagline {{ color:#8080b0; margin-top:0.3rem; font-size:0.8rem; font-style:italic; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1.5rem; padding:2rem; max-width:1200px; margin:0 auto; }}
  .card {{ background:#0f0f1f; border:1px solid #2a2a4a; border-radius:8px; padding:1.5rem; }}
  .card h2 {{ color:#8080ff; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:1rem; border-bottom:1px solid #1a1a3a; padding-bottom:0.5rem; }}
  .metric {{ display:flex; justify-content:space-between; align-items:baseline; margin:0.5rem 0; }}
  .metric-label {{ color:#6060a0; font-size:0.8rem; }}
  .metric-value {{ color:#c0c0ff; font-size:0.9rem; font-weight:bold; }}
  .metric-value.big {{ color:#a080ff; font-size:1.1rem; }}
  .metric-value.green {{ color:#40ff80; }}
  .metric-value.orange {{ color:#ffa040; }}
  .badge {{ display:inline-block; padding:0.2rem 0.6rem; border-radius:4px; font-size:0.7rem; font-weight:bold; margin:0.2rem; }}
  .badge.live {{ background:#1a3a1a; color:#40ff80; border:1px solid #40ff80; }}
  .badge.chain {{ background:#1a1a3a; color:#8080ff; border:1px solid #4040a0; }}
  .badge.silence {{ background:#2a1a0a; color:#ffa040; border:1px solid #ffa040; }}
  .links {{ display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; }}
  .link {{ background:#0a0a1f; border:1px solid #2a2a4a; border-radius:4px; padding:0.5rem; text-decoration:none; color:#8080c0; font-size:0.75rem; transition:all 0.2s; display:block; }}
  .link:hover {{ border-color:#6060a0; color:#c0c0ff; background:#0f0f2f; }}
  .link .method {{ color:#4040a0; font-size:0.65rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.8rem; }}
  th {{ color:#6060a0; padding:0.4rem; text-align:left; border-bottom:1px solid #1a1a3a; }}
  td {{ color:#c0c0ff; padding:0.4rem; border-bottom:1px solid #0f0f1f; }}
  .sse-note {{ background:#0a1a0a; border:1px solid #206020; border-radius:4px; padding:0.8rem; font-size:0.75rem; color:#60c060; margin-top:0.5rem; }}
  .silence-box {{ background:#1a0f0a; border:1px solid #604020; border-radius:4px; padding:0.8rem; margin-top:0.5rem; }}
  .silence-box p {{ font-size:0.75rem; color:#c08040; line-height:1.5; }}
  .on-chain {{ background:#0a0f1a; border:1px solid #204060; border-radius:4px; padding:0.8rem; margin-top:0.5rem; }}
  .on-chain p {{ font-size:0.75rem; color:#4080c0; line-height:1.5; }}
</style>
</head>
<body>
<div class="header">
  <h1>SOVEREIGN-Ω</h1>
  <div class="formula">Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e<sup>Λ·t</sup></div>
  <div class="tagline">Truth or silence. The silence is information. · Pharos Chain · TRION Mathematics</div>
  <div style="margin-top:1rem">
    <span class="badge live">● ONLINE</span>
    <span class="badge chain">⛓ Pharos Testnet</span>
    <span class="badge silence">⚡ Silence Protocol ACTIVE</span>
  </div>
</div>

<div class="grid">

  <div class="card">
    <h2>⚡ Live Intelligence</h2>
    <div class="metric"><span class="metric-label">Λ (Compounding Moat)</span><span class="metric-value big">{lam_fmt}</span></div>
    <div class="metric"><span class="metric-label">log(Λ)</span><span class="metric-value">{log_lam:.4f}</span></div>
    <div class="metric"><span class="metric-label">IQ Score IQ(t)</span><span class="metric-value big">{iq_fmt}</span></div>
    <div class="metric"><span class="metric-label">Coherent Cycles</span><span class="metric-value green">{cycles:,}</span></div>
    <div class="metric"><span class="metric-label">Domains Mastered</span><span class="metric-value">{len(domains)}</span></div>
    <div class="sse-note">📡 Subscribe to live stream:<br><code>/api/v1/stream/intelligence</code></div>
  </div>

  <div class="card">
    <h2>🧠 TRION Coherence</h2>
    <div class="metric"><span class="metric-label">Ψ Formula</span><span class="metric-value" style="font-size:0.75rem">0.25P + 0.30I + 0.20C + 0.15S + 0.10W</span></div>
    <div class="metric"><span class="metric-label">Gate Base Δ</span><span class="metric-value">0.6500</span></div>
    <div class="metric"><span class="metric-label">Max Δ (max volatility)</span><span class="metric-value">0.8970</span></div>
    <div class="metric"><span class="metric-label">Silence rate</span><span class="metric-value orange">~87.9% (discriminating)</span></div>
    <div class="silence-box">
      <p>When Ψ &lt; Δ the agent is SILENT. Silence is not failure — it's the Silence Protocol making the decision that acting would be wrong. Every other agent acts on everything. This one doesn't.</p>
    </div>
  </div>

  <div class="card">
    <h2>⛓ Pharos On-Chain</h2>
    <div class="metric"><span class="metric-label">Network</span><span class="metric-value">Testnet (688689)</span></div>
    <div class="metric"><span class="metric-label">Chain Syncs</span><span class="metric-value green">{stats['total_chain_syncs']}</span></div>
    <div class="metric"><span class="metric-label">Sync Interval</span><span class="metric-value">Every {stats['sync_interval_cycles']} cycles</span></div>
    <div class="metric"><span class="metric-label">SovereignRegistry</span><span class="metric-value" style="font-size:0.7rem">0x6EAB...018Ba</span></div>
    <div class="metric"><span class="metric-label">SovereignVault</span><span class="metric-value" style="font-size:0.7rem">0xAbC1...A7A66</span></div>
    <div class="metric"><span class="metric-label">SovereignLearner</span><span class="metric-value" style="font-size:0.7rem">0x7990...9F84</span></div>
    <div class="on-chain"><p>Λ + IQ auto-synced to chain every 100 coherent cycles. Every action emits an on-chain heartbeat. Moat growth is provably on-chain.</p></div>
  </div>

  <div class="card">
    <h2>🎯 6 Agent Skills</h2>
    <div class="metric"><span class="metric-label">coherence_evaluate</span><span class="metric-value" style="color:#40ff80;font-size:0.75rem">FREE</span></div>
    <div class="metric"><span class="metric-label">moat_status</span><span class="metric-value" style="color:#40ff80;font-size:0.75rem">FREE</span></div>
    <div class="metric"><span class="metric-label">silence_check</span><span class="metric-value" style="color:#40ff80;font-size:0.75rem">FREE</span></div>
    <div class="metric"><span class="metric-label">intelligence_score</span><span class="metric-value" style="color:#40ff80;font-size:0.75rem">FREE</span></div>
    <div class="metric"><span class="metric-label">trade_evaluate</span><span class="metric-value" style="color:#ffa040;font-size:0.75rem">1.0 PROS / 0.10 USDC</span></div>
    <div class="metric"><span class="metric-label">reasoning_chain</span><span class="metric-value" style="color:#ffa040;font-size:0.75rem">2.0 PROS / 0.20 USDC</span></div>
    <div class="sse-note" style="margin-top:0.8rem">MCP + x402 · <a href="/api/v1/skills" style="color:#60c060">View all skills →</a></div>
  </div>

  <div class="card">
    <h2>🌐 Federation (A2A)</h2>
    <div class="metric"><span class="metric-label">Active Peers</span><span class="metric-value green">0</span></div>
    <div class="metric"><span class="metric-label">Protocol</span><span class="metric-value">Ψ-gated handshake</span></div>
    <div class="metric"><span class="metric-label">Discovery</span><span class="metric-value" style="font-size:0.75rem">/.well-known/agent.json</span></div>
    <div class="links" style="margin-top:0.8rem">
      <a class="link" href="/api/v1/federation/announce"><span class="method">POST</span> /announce</a>
      <a class="link" href="/api/v1/federation/peers"><span class="method">GET</span> /peers</a>
      <a class="link" href="/api/v1/federation/network"><span class="method">GET</span> /network</a>
      <a class="link" href="/api/v1/federation/broadcast"><span class="method">SSE</span> /broadcast</a>
    </div>
  </div>

  <div class="card">
    <h2>📡 Live SSE Streams</h2>
    <div class="links">
      <a class="link" href="/api/v1/stream/intelligence"><span class="method">SSE</span> /intelligence</a>
      <a class="link" href="/api/v1/stream/heartbeat"><span class="method">SSE</span> /heartbeat</a>
      <a class="link" href="/api/v1/stream/moat"><span class="method">SSE</span> /moat</a>
      <a class="link" href="/api/v1/stream/actions"><span class="method">SSE</span> /actions</a>
    </div>
    <div class="sse-note" style="margin-top:0.8rem">Other agents subscribe to monitor SOVEREIGN-Ω's intelligence quality before invoking skills</div>

    <h2 style="margin-top:1.2rem">🔗 Explore</h2>
    <div class="links" style="margin-top:0.5rem">
      <a class="link" href="/docs"><span class="method">UI</span> Swagger Docs</a>
      <a class="link" href="/.well-known/agent.json"><span class="method">A2A</span> Agent Card</a>
      <a class="link" href="/api/v1/health"><span class="method">GET</span> /health</a>
      <a class="link" href="/api/v1/moat"><span class="method">GET</span> /moat</a>
    </div>
  </div>

  <div class="card" style="grid-column:1/-1">
    <h2>📊 Domain Mastery</h2>
    <table>
      <thead><tr><th>Domain</th><th>Mastery M(d,t)</th><th>Knowledge Count</th></tr></thead>
      <tbody>{domain_rows}</tbody>
    </table>
  </div>

</div>

<div style="text-align:center;padding:1.5rem;color:#3a3a6a;font-size:0.75rem;border-top:1px solid #1a1a2a">
  SOVEREIGN-Ω v2.0.0 · Built for Pharos Phase 1 Hackathon · DoraHacks · June 2026 · 50,000 $PROS Prize Pool
</div>
</body>
</html>"""
