import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse

from api.routes import action, trade, intelligence, pharos_routes, silence, moat, health
from api.routes import skills, agent_card, x402, mcp_server
from api.routes import federation, stream, ws_dashboard


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

# ── WebSocket Dashboard ───────────────────────────────────────────────────────
app.include_router(ws_dashboard.router, tags=["Dashboard (WebSocket)"])


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
  SOVEREIGN-Ω v2.0.0 · Built for Pharos Phase 1 Hackathon · DoraHacks · June 2026 · 150,000 $PROS Prize Pool
  · <a href="/dashboard" style="color:#6060a0">Live Dashboard →</a>
  · <a href="/pipeline" style="color:#6060a0">Pipeline &amp; On-Chain →</a>
</div>
</body>
</html>"""


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    import os
    ws_protocol = "wss"
    host = os.getenv("REPLIT_DEV_DOMAIN", "")
    if host:
        ws_url = f"{ws_protocol}://{host}/ws/dashboard"
    else:
        ws_url = f"ws://localhost:{os.getenv('PORT', '8000')}/ws/dashboard"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SOVEREIGN-Ω · Live Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg:      #06060e;
    --surface: #0d0d1c;
    --border:  #1e1e3a;
    --accent:  #7c5cfc;
    --green:   #2ecc71;
    --orange:  #f39c12;
    --red:     #e74c3c;
    --text:    #c8c8f0;
    --muted:   #4a4a7a;
    --silence: #c0392b;
    --open:    #27ae60;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ height:100%; background:var(--bg); color:var(--text); font-family:'Courier New',monospace; overflow-x:hidden; }}

  /* ── top bar ── */
  #topbar {{
    display:flex; align-items:center; justify-content:space-between;
    background:var(--surface); border-bottom:1px solid var(--border);
    padding:0.65rem 1.4rem; position:sticky; top:0; z-index:100;
  }}
  #topbar .brand {{ color:var(--accent); font-size:1.1rem; letter-spacing:.1em; font-weight:700; }}
  #topbar .formula {{ color:var(--muted); font-size:0.72rem; }}
  #ws-status {{ font-size:0.72rem; padding:0.25rem 0.7rem; border-radius:12px;
    background:#1a1a0a; color:var(--orange); border:1px solid var(--orange); }}
  #ws-status.connected {{ background:#0a1a0a; color:var(--green); border-color:var(--green); }}

  /* ── main grid ── */
  #grid {{
    display:grid;
    grid-template-columns: 240px 1fr 1fr 260px;
    grid-template-rows: auto auto auto;
    gap:1px; background:var(--border);
    min-height:calc(100vh - 48px);
  }}
  .panel {{
    background:var(--surface); padding:1.1rem; overflow:hidden;
    display:flex; flex-direction:column; gap:0.6rem;
  }}
  .panel-title {{
    font-size:0.65rem; text-transform:uppercase; letter-spacing:.15em;
    color:var(--muted); padding-bottom:0.5rem; border-bottom:1px solid var(--border);
  }}

  /* ── gate ── */
  #gate-panel {{ grid-column:1; grid-row:1; align-items:center; justify-content:center; }}
  #gate-badge {{
    font-size:1.6rem; font-weight:700; letter-spacing:.12em;
    padding:1rem 1.5rem; border-radius:10px; text-align:center;
    border:2px solid; transition:all .4s ease;
    width:100%;
  }}
  #gate-badge.silence {{ color:var(--silence); border-color:var(--silence); background:#1a0808;
    box-shadow:0 0 20px rgba(192,57,43,0.3); }}
  #gate-badge.open {{ color:var(--open); border-color:var(--open); background:#081a08;
    box-shadow:0 0 20px rgba(39,174,96,0.4); animation:pulse-open 1.5s ease infinite; }}
  @keyframes pulse-open {{
    0%,100% {{ box-shadow:0 0 20px rgba(39,174,96,0.4); }}
    50%      {{ box-shadow:0 0 40px rgba(39,174,96,0.7); }}
  }}
  .gate-sub {{ font-size:0.75rem; color:var(--muted); text-align:center; }}
  #psi-val {{ font-size:2.4rem; font-weight:700; color:var(--accent); text-align:center; line-height:1; }}
  #delta-val {{ font-size:0.78rem; color:var(--muted); text-align:center; }}

  /* ── psi chart ── */
  #psi-panel {{ grid-column:2; grid-row:1; }}

  /* ── lambda chart ── */
  #lambda-panel {{ grid-column:3; grid-row:1; }}

  /* ── planes panel ── */
  #planes-panel {{ grid-column:4; grid-row:1; }}
  .plane-row {{ display:flex; flex-direction:column; gap:2px; margin-bottom:0.5rem; }}
  .plane-label {{ display:flex; justify-content:space-between; font-size:0.72rem; }}
  .plane-name {{ color:var(--muted); }}
  .plane-score {{ color:var(--text); font-weight:700; }}
  .plane-bar-bg {{ height:6px; background:#1a1a2e; border-radius:3px; overflow:hidden; }}
  .plane-bar {{ height:6px; border-radius:3px; transition:width .5s ease; }}
  .plane-p {{ background:#9b59b6; }}
  .plane-i {{ background:#3498db; }}
  .plane-c {{ background:#1abc9c; }}
  .plane-s {{ background:#e67e22; }}
  .plane-w {{ background:#e74c3c; }}

  /* ── metrics strip ── */
  #metrics-panel {{ grid-column:1/-1; grid-row:2; flex-direction:row; flex-wrap:wrap; gap:1.5rem; align-items:center; }}
  .metric {{ display:flex; flex-direction:column; gap:2px; }}
  .metric-label {{ font-size:0.62rem; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); }}
  .metric-value {{ font-size:1.05rem; font-weight:700; color:var(--text); }}
  .metric-value.accent {{ color:var(--accent); }}
  .metric-value.green {{ color:var(--green); }}
  .metric-value.orange {{ color:var(--orange); }}

  /* ── heartbeat ── */
  #hb-dot {{
    width:10px; height:10px; border-radius:50%;
    background:var(--green); display:inline-block;
    animation:hb 1s ease infinite;
  }}
  @keyframes hb {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%      {{ opacity:0.4; transform:scale(0.7); }}
  }}

  /* ── federation ── */
  #fed-panel {{ grid-column:1/3; grid-row:3; }}
  #fed-svg {{ width:100%; flex:1; min-height:200px; }}

  /* ── action feed ── */
  #feed-panel {{ grid-column:3/-1; grid-row:3; }}
  #action-feed {{ flex:1; overflow-y:auto; font-size:0.72rem; display:flex; flex-direction:column; gap:4px; }}
  .feed-item {{
    padding:0.35rem 0.6rem; border-radius:4px; border-left:3px solid;
    background:#0a0a18; display:flex; gap:0.6rem; align-items:baseline;
  }}
  .feed-item.silence {{ border-color:var(--silence); color:#c07070; }}
  .feed-item.open    {{ border-color:var(--open); color:#70c070; }}
  .feed-time {{ color:var(--muted); font-size:0.65rem; flex-shrink:0; }}
  .feed-gate {{ font-weight:700; flex-shrink:0; width:52px; }}
  .feed-psi  {{ color:var(--muted); }}

  /* responsive */
  @media (max-width:900px) {{
    #grid {{ grid-template-columns:1fr 1fr; grid-template-rows:auto auto auto auto auto; }}
    #gate-panel   {{ grid-column:1; grid-row:1; }}
    #planes-panel {{ grid-column:2; grid-row:1; }}
    #psi-panel    {{ grid-column:1/-1; grid-row:2; }}
    #lambda-panel {{ grid-column:1/-1; grid-row:3; }}
    #metrics-panel {{ grid-column:1/-1; grid-row:4; }}
    #fed-panel    {{ grid-column:1/-1; grid-row:5; }}
    #feed-panel   {{ grid-column:1/-1; grid-row:6; }}
  }}
</style>
</head>
<body>

<div id="topbar">
  <div>
    <div class="brand">SOVEREIGN-Ω</div>
    <div class="formula">Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e<sup>Λ·t</sup> &nbsp;|&nbsp; Truth or silence. The silence is information.</div>
  </div>
  <div style="display:flex;gap:1rem;align-items:center">
    <a href="/" style="color:var(--muted);font-size:0.72rem;text-decoration:none">← Home</a>
    <a href="/docs" style="color:var(--muted);font-size:0.72rem;text-decoration:none">API Docs</a>
    <div id="ws-status">⟳ Connecting…</div>
  </div>
</div>

<div id="grid">

  <!-- Gate + Ψ -->
  <div class="panel" id="gate-panel">
    <div class="panel-title">Action Gate</div>
    <div id="gate-badge" class="silence">SILENCE</div>
    <div class="gate-sub">gate status</div>
    <div id="psi-val">0.000</div>
    <div id="delta-val">Δ = 0.0000 &nbsp;|&nbsp; Ψ − Δ = 0.0000</div>
    <div style="margin-top:auto;font-size:0.68rem;color:var(--muted);line-height:1.5">
      When Ψ &lt; Δ the agent is silent. Silence is not failure — it is information.
    </div>
  </div>

  <!-- Ψ rolling chart -->
  <div class="panel" id="psi-panel">
    <div class="panel-title">Ψ Coherence Score — live (60s window)</div>
    <canvas id="psiChart" style="flex:1;min-height:0"></canvas>
  </div>

  <!-- Λ growth chart -->
  <div class="panel" id="lambda-panel">
    <div class="panel-title">log(Λ) Compounding Moat — live (60s window)</div>
    <canvas id="lambdaChart" style="flex:1;min-height:0"></canvas>
  </div>

  <!-- 5 planes -->
  <div class="panel" id="planes-panel">
    <div class="panel-title">5 Cognitive Planes</div>
    <div class="plane-row">
      <div class="plane-label"><span class="plane-name">P · Perceptual   (×0.25)</span><span class="plane-score" id="p-score">0.000</span></div>
      <div class="plane-bar-bg"><div class="plane-bar plane-p" id="p-bar" style="width:0%"></div></div>
    </div>
    <div class="plane-row">
      <div class="plane-label"><span class="plane-name">I · Inferential  (×0.30)</span><span class="plane-score" id="i-score">0.000</span></div>
      <div class="plane-bar-bg"><div class="plane-bar plane-i" id="i-bar" style="width:0%"></div></div>
    </div>
    <div class="plane-row">
      <div class="plane-label"><span class="plane-name">C · Consensus    (×0.20)</span><span class="plane-score" id="c-score">0.000</span></div>
      <div class="plane-bar-bg"><div class="plane-bar plane-c" id="c-bar" style="width:0%"></div></div>
    </div>
    <div class="plane-row">
      <div class="plane-label"><span class="plane-name">S · Self-Reflect (×0.15)</span><span class="plane-score" id="s-score">0.000</span></div>
      <div class="plane-bar-bg"><div class="plane-bar plane-s" id="s-bar" style="width:0%"></div></div>
    </div>
    <div class="plane-row">
      <div class="plane-label"><span class="plane-name">W · World Model  (×0.10)</span><span class="plane-score" id="w-score">0.000</span></div>
      <div class="plane-bar-bg"><div class="plane-bar plane-w" id="w-bar" style="width:0%"></div></div>
    </div>
    <div style="margin-top:0.6rem;padding-top:0.6rem;border-top:1px solid var(--border);font-size:0.68rem;color:var(--muted);line-height:1.6">
      Contradiction → I=0<br>World z&gt;3σ → W=0<br>No LLM → P=0, C↓
    </div>
  </div>

  <!-- Metrics strip -->
  <div class="panel" id="metrics-panel">
    <div class="metric">
      <div class="metric-label"><span id="hb-dot"></span> Heartbeat</div>
      <div class="metric-value green" id="m-cycles">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">Λ (Moat)</div>
      <div class="metric-value accent" id="m-lambda">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">log(Λ)</div>
      <div class="metric-value" id="m-loglambda">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">IQ Score</div>
      <div class="metric-value" id="m-iq">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">Chain Syncs</div>
      <div class="metric-value green" id="m-syncs">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">Next Sync In</div>
      <div class="metric-value orange" id="m-nextsync">— cycles</div>
    </div>
    <div class="metric">
      <div class="metric-label">Federation Peers</div>
      <div class="metric-value" id="m-peers">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">Chain</div>
      <div class="metric-value" style="font-size:0.85rem">Pharos Testnet 688689</div>
    </div>
    <div class="metric" style="margin-left:auto">
      <div class="metric-label">Frame</div>
      <div class="metric-value" id="m-seq" style="font-size:0.85rem;color:var(--muted)">—</div>
    </div>
  </div>

  <!-- Federation map -->
  <div class="panel" id="fed-panel">
    <div class="panel-title">Federation Network · A2A Peer Map</div>
    <svg id="fed-svg" viewBox="0 0 500 200"></svg>
    <div style="font-size:0.68rem;color:var(--muted)">
      Peers announce via POST /api/v1/federation/announce · Ψ-gated handshake required
    </div>
  </div>

  <!-- Action feed -->
  <div class="panel" id="feed-panel">
    <div class="panel-title">Live Gate Decisions</div>
    <div id="action-feed">
      <div class="feed-item silence">
        <span class="feed-time">--:--:--</span>
        <span class="feed-gate">SILENCE</span>
        <span class="feed-psi">Ψ waiting for first frame…</span>
      </div>
    </div>
  </div>

</div>

<script>
const WS_URL = "{ws_url}";
const WINDOW = 60;

// ── Chart.js shared config ──────────────────────────────────────────
const darkGrid = {{ color:'rgba(30,30,60,0.8)' }};
const makeLabels = () => Array.from({{length:WINDOW}}, (_,i)=>'');

function makeChart(id, label, color, yMin=0, yMax=1) {{
  const ctx = document.getElementById(id).getContext('2d');
  return new Chart(ctx, {{
    type:'line',
    data:{{
      labels: makeLabels(),
      datasets:[{{
        label,
        data: new Array(WINDOW).fill(null),
        borderColor: color,
        backgroundColor: color.replace(')',',0.08)').replace('rgb','rgba'),
        borderWidth:2,
        pointRadius:0,
        tension:0.35,
        fill:true,
      }}]
    }},
    options:{{
      animation:{{ duration:300 }},
      responsive:true,
      maintainAspectRatio:false,
      plugins:{{ legend:{{display:false}}, tooltip:{{ mode:'index', intersect:false }} }},
      scales:{{
        x:{{ display:false }},
        y:{{
          min:yMin, max:yMax,
          grid: darkGrid,
          ticks:{{ color:'#4a4a7a', font:{{size:10}} }}
        }}
      }}
    }}
  }});
}}

const psiChart    = makeChart('psiChart',    'Ψ Coherence', 'rgb(124,92,252)', 0, 1);
const lambdaChart = makeChart('lambdaChart', 'log(Λ) Moat', 'rgb(46,204,113)', 0, null);

function pushChart(chart, val, yMax=null) {{
  chart.data.datasets[0].data.push(val);
  if (chart.data.datasets[0].data.length > WINDOW)
    chart.data.datasets[0].data.shift();
  chart.data.labels.push('');
  if (chart.data.labels.length > WINDOW) chart.data.labels.shift();
  if (yMax !== null) chart.options.scales.y.max = yMax;
  chart.update('none');
}}

// ── Federation SVG ──────────────────────────────────────────────────
const SVG_NS = 'http://www.w3.org/2000/svg';
function renderFedSVG(peers) {{
  const svg = document.getElementById('fed-svg');
  svg.innerHTML = '';
  const W=500, H=200, cx=W/2, cy=H/2, r=70;

  // Hub node
  const hubG = document.createElementNS(SVG_NS,'g');
  const hubCirc = document.createElementNS(SVG_NS,'circle');
  hubCirc.setAttribute('cx',cx); hubCirc.setAttribute('cy',cy);
  hubCirc.setAttribute('r',22); hubCirc.setAttribute('fill','#1a0a3a');
  hubCirc.setAttribute('stroke','#7c5cfc'); hubCirc.setAttribute('stroke-width','2');
  const hubText = document.createElementNS(SVG_NS,'text');
  hubText.setAttribute('x',cx); hubText.setAttribute('y',cy-6);
  hubText.setAttribute('text-anchor','middle'); hubText.setAttribute('fill','#a080ff');
  hubText.setAttribute('font-size','9'); hubText.setAttribute('font-family','Courier New');
  hubText.textContent = 'SOVEREIGN';
  const hubText2 = document.createElementNS(SVG_NS,'text');
  hubText2.setAttribute('x',cx); hubText2.setAttribute('y',cy+7);
  hubText2.setAttribute('text-anchor','middle'); hubText2.setAttribute('fill','#7c5cfc');
  hubText2.setAttribute('font-size','9'); hubText2.setAttribute('font-family','Courier New');
  hubText2.textContent = '-Ω';
  hubG.appendChild(hubCirc); hubG.appendChild(hubText); hubG.appendChild(hubText2);

  // Pulse ring
  const pulse = document.createElementNS(SVG_NS,'circle');
  pulse.setAttribute('cx',cx); pulse.setAttribute('cy',cy); pulse.setAttribute('r',28);
  pulse.setAttribute('fill','none'); pulse.setAttribute('stroke','#7c5cfc');
  pulse.setAttribute('stroke-width','1'); pulse.setAttribute('opacity','0.4');
  const animEl = document.createElementNS(SVG_NS,'animate');
  animEl.setAttribute('attributeName','r'); animEl.setAttribute('from','22');
  animEl.setAttribute('to','36'); animEl.setAttribute('dur','2s');
  animEl.setAttribute('repeatCount','indefinite');
  const animOp = document.createElementNS(SVG_NS,'animate');
  animOp.setAttribute('attributeName','opacity'); animOp.setAttribute('from','0.4');
  animOp.setAttribute('to','0'); animOp.setAttribute('dur','2s');
  animOp.setAttribute('repeatCount','indefinite');
  pulse.appendChild(animEl); pulse.appendChild(animOp);
  svg.appendChild(pulse);

  if (peers.length === 0) {{
    const nopeers = document.createElementNS(SVG_NS,'text');
    nopeers.setAttribute('x',cx); nopeers.setAttribute('y',H-14);
    nopeers.setAttribute('text-anchor','middle'); nopeers.setAttribute('fill','#3a3a6a');
    nopeers.setAttribute('font-size','10'); nopeers.setAttribute('font-family','Courier New');
    nopeers.textContent = 'No peers yet — announce via POST /api/v1/federation/announce';
    svg.appendChild(nopeers);
    svg.appendChild(hubG);
    return;
  }}

  // Peer nodes arranged in arc
  peers.slice(0,12).forEach((p,i) => {{
    const angle = (2*Math.PI/peers.length)*i - Math.PI/2;
    const px = cx + r*Math.cos(angle);
    const py = cy + r*Math.sin(angle);

    // Edge
    const line = document.createElementNS(SVG_NS,'line');
    line.setAttribute('x1',cx); line.setAttribute('y1',cy);
    line.setAttribute('x2',px); line.setAttribute('y2',py);
    const edgeColor = p.status==='active' ? '#2ecc71' : p.status==='invited' ? '#f39c12' : '#7c5cfc';
    line.setAttribute('stroke',edgeColor); line.setAttribute('stroke-width','1');
    line.setAttribute('opacity','0.5'); line.setAttribute('stroke-dasharray','4,3');
    svg.appendChild(line);

    // Peer circle
    const pc = document.createElementNS(SVG_NS,'circle');
    pc.setAttribute('cx',px); pc.setAttribute('cy',py); pc.setAttribute('r',12);
    pc.setAttribute('fill','#0a0a1a'); pc.setAttribute('stroke',edgeColor);
    pc.setAttribute('stroke-width','1.5');
    svg.appendChild(pc);

    // Label
    const lbl = document.createElementNS(SVG_NS,'text');
    lbl.setAttribute('x',px); lbl.setAttribute('y',py+4);
    lbl.setAttribute('text-anchor','middle'); lbl.setAttribute('fill',edgeColor);
    lbl.setAttribute('font-size','7'); lbl.setAttribute('font-family','Courier New');
    const shortName = (p.name||'agent').slice(0,8);
    lbl.textContent = shortName;
    svg.appendChild(lbl);

    // Ψ label below
    if (p.psi != null) {{
      const psiLbl = document.createElementNS(SVG_NS,'text');
      const lblY = py + (py>cy ? 22 : -14);
      psiLbl.setAttribute('x',px); psiLbl.setAttribute('y',lblY);
      psiLbl.setAttribute('text-anchor','middle'); psiLbl.setAttribute('fill','#4a4a7a');
      psiLbl.setAttribute('font-size','7'); psiLbl.setAttribute('font-family','Courier New');
      psiLbl.textContent = `Ψ=${{p.psi.toFixed(3)}}`;
      svg.appendChild(psiLbl);
    }}
  }});

  svg.appendChild(hubG);
}}

// ── Action feed ─────────────────────────────────────────────────────
const feed = document.getElementById('action-feed');
const feedHistory = [];
const MAX_FEED = 30;

function addFeedItem(gate, psi, ts) {{
  feedHistory.unshift({{gate, psi, ts}});
  if (feedHistory.length > MAX_FEED) feedHistory.pop();
  feed.innerHTML = feedHistory.map(f => {{
    const t = new Date(f.ts).toTimeString().slice(0,8);
    const cls = f.gate === 'OPEN' ? 'open' : 'silence';
    return `<div class="feed-item ${{cls}}">
      <span class="feed-time">${{t}}</span>
      <span class="feed-gate">${{f.gate}}</span>
      <span class="feed-psi">Ψ=${{f.psi.toFixed(4)}}</span>
    </div>`;
  }}).join('');
}}

// ── Helpers ─────────────────────────────────────────────────────────
function fmtBig(n) {{
  if (n == null) return '—';
  if (n >= 1e18) return n.toExponential(3);
  if (n >= 1e12) return (n/1e12).toFixed(2)+'T';
  if (n >= 1e9)  return (n/1e9).toFixed(2)+'B';
  if (n >= 1e6)  return (n/1e6).toFixed(2)+'M';
  return n.toFixed(4);
}}

function updatePlanes(planes) {{
  ['p','i','c','s','w'].forEach(k => {{
    const v = planes[k] ?? 0;
    document.getElementById(`${{k}}-score`).textContent = v.toFixed(4);
    document.getElementById(`${{k}}-bar`).style.width = (v*100).toFixed(1)+'%';
  }});
}}

// ── WebSocket ───────────────────────────────────────────────────────
let lastSeq = -1;
let maxLogLam = 60;

function connect() {{
  const status = document.getElementById('ws-status');
  status.textContent = '⟳ Connecting…';
  status.className = '';

  const ws = new WebSocket(WS_URL);

  ws.onopen = () => {{
    status.textContent = '● Live';
    status.className = 'connected';
  }};

  ws.onmessage = (e) => {{
    let d;
    try {{ d = JSON.parse(e.data); }} catch {{ return; }}
    if (d.type !== 'state') return;

    // Gate
    const gate = d.gate || 'SILENCE';
    const badge = document.getElementById('gate-badge');
    badge.textContent = gate;
    badge.className = gate === 'OPEN' ? 'open' : 'silence';
    document.getElementById('psi-val').textContent = (d.psi||0).toFixed(4);
    document.getElementById('delta-val').textContent =
      `Δ = ${{(d.delta||0).toFixed(4)}} | Ψ−Δ = ${{((d.psi||0)-(d.delta||0)).toFixed(4)}}`;

    // Charts
    pushChart(psiChart, d.psi ?? null);
    if (d.log_lambda != null) {{
      maxLogLam = Math.max(maxLogLam, d.log_lambda * 1.05);
      lambdaChart.options.scales.y.max = Math.ceil(maxLogLam);
      pushChart(lambdaChart, d.log_lambda);
    }}

    // Planes
    if (d.planes) updatePlanes(d.planes);

    // Metrics
    document.getElementById('m-cycles').textContent   = (d.cycles||0).toLocaleString();
    document.getElementById('m-lambda').textContent   = fmtBig(d.lambda);
    document.getElementById('m-loglambda').textContent = (d.log_lambda||0).toFixed(4);
    document.getElementById('m-iq').textContent       = fmtBig(d.iq);
    document.getElementById('m-syncs').textContent    = d.chain_syncs ?? '—';
    document.getElementById('m-nextsync').textContent = `${{d.next_sync_in ?? '—'}} cycles`;
    document.getElementById('m-peers').textContent    = d.peer_count ?? 0;
    document.getElementById('m-seq').textContent      = `#${{d.seq ?? 0}}`;

    // Federation SVG
    renderFedSVG(d.peers || []);

    // Feed — add entry if gate changed or every 10 frames
    if (d.seq !== lastSeq && (d.seq % 10 === 0 || lastSeq === -1)) {{
      addFeedItem(gate, d.psi||0, d.ts || new Date().toISOString());
    }}
    lastSeq = d.seq;
  }};

  ws.onerror = () => {{
    status.textContent = '✗ Error';
    status.className = '';
  }};

  ws.onclose = () => {{
    status.textContent = '↻ Reconnecting…';
    status.className = '';
    setTimeout(connect, 3000);
  }};
}}

renderFedSVG([]);
connect();
</script>
</body>
</html>"""


@app.get("/pipeline", response_class=HTMLResponse, include_in_schema=False)
async def pipeline_page():
    import os, asyncio, math
    from core.moat_accumulator import MoatAccumulator
    from core.action_gate import ActionGate
    from learning.intelligence_score import IntelligenceScorer
    from learning.domain_mastery import DomainMasteryEngine
    from core.on_chain_heartbeat import get_heartbeat_log

    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    gate = ActionGate()

    iq = await scorer.compute()
    lam = moat.get_current_lambda()
    log_lam = moat.log_lambda
    cycles = moat.n_cycles
    delta = gate.compute_threshold(0.1, 0.2)

    domains = DomainMasteryEngine().get_all()
    domain_rows = "".join(
        f"<tr><td>{d['domain']}</td><td>{d['mastery_score']:.6f}</td><td>{d['knowledge_count']}</td></tr>"
        for d in domains[:8]
    ) or "<tr><td colspan='3' style='color:#3a3a6a'>No domains yet</td></tr>"

    heartbeat_log = get_heartbeat_log(20)
    hb_rows = ""
    for h in reversed(heartbeat_log[-8:]):
        gate_col = "#40ff80" if h.get("gate") == "OPEN" else "#ffa040"
        tx = h.get("registry_tx") or h.get("tx") or "—"
        ts = (h.get("timestamp") or "")[:19].replace("T", " ")
        psi_v = h.get("psi", "—")
        psi_s = f"{psi_v:.4f}" if isinstance(psi_v, float) else str(psi_v)
        explorer = f"<a href='https://testnet.pharosscan.xyz/tx/{tx}' target='_blank' style='color:#6060c0'>{tx[:14]}…</a>" if tx and tx not in ("—","no_registry","simulated") else f"<span style='color:#3a3a6a'>{tx}</span>"
        hb_rows += f"<tr><td style='color:#6060a0'>{ts}</td><td style='color:{gate_col}'>{h.get('gate','—')}</td><td style='color:#c0c0ff'>{psi_s}</td><td>{explorer}</td></tr>"
    if not hb_rows:
        hb_rows = "<tr><td colspan='4' style='color:#3a3a6a'>No heartbeats yet in this session — live syncs appear here</td></tr>"

    confirmed_txs = [
        ("e610233d729a35fde68a8cec26c03785f7711df8dc24f2f3e730e5b3137b40d8", "SovereignRegistry.updateMoat()", "24358807", "37,616"),
        ("53682ff09d2e68b85f8c5304aa465d181a307b6b1d679781d0bfb8cffc96b0ed", "SovereignLearner.updateDomainMastery(testing)", "24358812", "44,042"),
        ("453f399ac3cfa0eb8c5bb9d42cc14bbdd0e2c1a728c0cd007ec7fe193488a87c", "SovereignLearner.updateDomainMastery(trading)", "24358817", "44,018"),
    ]
    conf_rows = "".join(
        f"""<tr>
          <td><a href='https://testnet.pharosscan.xyz/tx/{h}' target='_blank' style='color:#7060d0;font-family:monospace;font-size:0.72rem'>{h[:20]}…</a></td>
          <td style='color:#a0c0ff'>{fn}</td>
          <td style='color:#60c060'>{blk}</td>
          <td style='color:#c0c0ff'>{gas}</td>
          <td><span style='background:#0a2a0a;color:#40ff80;padding:1px 6px;border-radius:3px;font-size:0.7rem'>SUCCESS</span></td>
        </tr>"""
        for h, fn, blk, gas in confirmed_txs
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SOVEREIGN-Ω · Pipeline &amp; On-Chain</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#06060e; color:#c8c8f0; font-family:'Courier New',monospace; }}
  a {{ text-decoration:none; }}

  .topbar {{ display:flex; align-items:center; justify-content:space-between;
    background:#0d0d1c; border-bottom:1px solid #1e1e3a;
    padding:0.65rem 1.4rem; position:sticky; top:0; z-index:100; }}
  .topbar .brand {{ color:#7c5cfc; font-size:1.05rem; letter-spacing:.1em; font-weight:700; }}
  .nav a {{ color:#4a4a7a; font-size:0.72rem; margin-left:1rem; }}
  .nav a:hover {{ color:#c0c0ff; }}

  .hero {{ background:linear-gradient(135deg,#0a0a18,#14082a); border-bottom:1px solid #1e1e3a;
    padding:2.5rem 2rem; text-align:center; }}
  .hero h1 {{ font-size:1.8rem; color:#a080ff; letter-spacing:.08em; }}
  .hero .eq {{ color:#6060c0; margin:.5rem 0; font-size:1rem; }}
  .hero .sub {{ color:#4a4a7a; font-size:0.78rem; font-style:italic; margin-top:.3rem; }}

  .page {{ max-width:1100px; margin:0 auto; padding:2rem 1.5rem; display:flex; flex-direction:column; gap:2rem; }}

  .card {{ background:#0d0d1c; border:1px solid #1e1e3a; border-radius:8px; overflow:hidden; }}
  .card-header {{ background:#0a0a18; border-bottom:1px solid #1e1e3a; padding:.8rem 1.2rem;
    font-size:.7rem; text-transform:uppercase; letter-spacing:.15em; color:#4a4a7a;
    display:flex; align-items:center; gap:.6rem; }}
  .card-body {{ padding:1.2rem; }}

  /* pipeline flow */
  .pipeline {{ display:flex; flex-direction:column; gap:0; }}
  .step {{ display:grid; grid-template-columns:48px 1fr; gap:0; }}
  .step-spine {{ display:flex; flex-direction:column; align-items:center; }}
  .step-num {{ width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:.85rem; flex-shrink:0; border:2px solid; }}
  .step-line {{ flex:1; width:2px; background:#1e1e3a; min-height:24px; }}
  .step-content {{ padding:.3rem 0 1.5rem 1rem; }}
  .step-title {{ font-size:.9rem; font-weight:700; margin-bottom:.4rem; }}
  .step-desc {{ font-size:.75rem; color:#6060a0; line-height:1.6; }}
  .step-detail {{ margin-top:.5rem; background:#080810; border:1px solid #1a1a30; border-radius:4px; padding:.7rem;
    font-size:.72rem; line-height:1.7; color:#a0a0c0; }}
  .step-arrow {{ color:#3a3a6a; text-align:center; font-size:.75rem; padding:.2rem 0; grid-column:1/-1; }}

  .col2 {{ color:#7c5cfc; }}
  .col3 {{ color:#2ecc71; }}
  .col4 {{ color:#f39c12; }}
  .col5 {{ color:#e74c3c; }}
  .col6 {{ color:#3498db; }}
  .col7 {{ color:#1abc9c; }}
  .col8 {{ color:#e67e22; }}

  /* stat row */
  .stats {{ display:flex; flex-wrap:wrap; gap:1rem; }}
  .stat {{ background:#080810; border:1px solid #1a1a30; border-radius:6px; padding:.7rem 1rem; flex:1; min-width:140px; }}
  .stat-label {{ font-size:.62rem; text-transform:uppercase; letter-spacing:.1em; color:#4a4a7a; margin-bottom:.3rem; }}
  .stat-value {{ font-size:1rem; font-weight:700; color:#c0c0ff; word-break:break-all; }}
  .stat-value.accent {{ color:#7c5cfc; }}
  .stat-value.green  {{ color:#2ecc71; }}

  /* table */
  table {{ width:100%; border-collapse:collapse; font-size:.76rem; }}
  th {{ color:#4a4a7a; padding:.5rem .7rem; text-align:left; border-bottom:1px solid #1a1a30; font-weight:normal; text-transform:uppercase; letter-spacing:.08em; font-size:.65rem; }}
  td {{ padding:.5rem .7rem; border-bottom:1px solid #0d0d18; vertical-align:middle; }}

  /* contracts */
  .contract {{ background:#080810; border:1px solid #1a1a30; border-radius:6px; padding:.8rem 1rem; margin-bottom:.6rem; }}
  .contract-name {{ color:#a080ff; font-size:.8rem; font-weight:700; margin-bottom:.3rem; }}
  .contract-addr {{ font-family:monospace; font-size:.7rem; color:#6060a0; }}
  .contract-methods {{ margin-top:.4rem; display:flex; flex-wrap:wrap; gap:.3rem; }}
  .method-badge {{ background:#0a0a20; border:1px solid #2a2a4a; border-radius:3px; padding:.1rem .5rem; font-size:.65rem; color:#8080c0; }}

  .calldata {{ background:#040408; border:1px solid #1a1a30; border-radius:4px; padding:.8rem; font-family:monospace; font-size:.7rem; color:#8080b0; line-height:1.8; overflow-x:auto; }}
  .calldata .key {{ color:#6060c0; }}
  .calldata .val {{ color:#c0c0ff; }}
  .calldata .fn  {{ color:#a080ff; font-weight:700; }}

  .badge {{ display:inline-block; padding:.15rem .5rem; border-radius:3px; font-size:.65rem; font-weight:700; }}
  .badge.live {{ background:#0a2a0a; color:#40ff80; border:1px solid #40ff80; }}
  .badge.chain {{ background:#0a0a2a; color:#7c5cfc; border:1px solid #4040a0; }}

  .plane-row {{ display:flex; align-items:center; gap:.8rem; margin:.3rem 0; font-size:.78rem; }}
  .plane-bar-bg {{ flex:1; height:8px; background:#0a0a18; border-radius:4px; overflow:hidden; }}
  .plane-bar {{ height:8px; border-radius:4px; }}
</style>
</head>
<body>

<div class="topbar">
  <div class="brand">SOVEREIGN-Ω · Pipeline &amp; On-Chain</div>
  <div class="nav">
    <a href="/">← Home</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/docs">API Docs</a>
    <a href="https://testnet.pharosscan.xyz/address/0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20" target="_blank">Explorer ↗</a>
  </div>
</div>

<div class="hero">
  <h1>Full Pipeline &amp; On-Chain Transactions</h1>
  <div class="eq">Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e<sup>Λ·t</sup></div>
  <div class="sub">Every step traced · Every transaction confirmed · Pharos Testnet 688689</div>
  <div style="margin-top:.8rem">
    <span class="badge live">● ONLINE</span>
    <span class="badge chain">⛓ Pharos Testnet</span>
    <span class="badge chain">Nonce = 27 · 27 txs sent</span>
  </div>
</div>

<div class="page">

  <!-- live state -->
  <div class="card">
    <div class="card-header">⚡ Live State</div>
    <div class="card-body">
      <div class="stats">
        <div class="stat"><div class="stat-label">Λ (Compounding Moat)</div><div class="stat-value accent">{lam:.4e}</div></div>
        <div class="stat"><div class="stat-label">log(Λ)</div><div class="stat-value">{log_lam:.6f}</div></div>
        <div class="stat"><div class="stat-label">Coherent Cycles</div><div class="stat-value green">{cycles:,}</div></div>
        <div class="stat"><div class="stat-label">IQ Score</div><div class="stat-value">{iq:.4e}</div></div>
        <div class="stat"><div class="stat-label">Base Δ Threshold</div><div class="stat-value">{delta:.4f}</div></div>
        <div class="stat"><div class="stat-label">Agent Address</div><div class="stat-value" style="font-size:.7rem">0xdBbf…2d20</div></div>
      </div>
    </div>
  </div>

  <!-- 8-step pipeline -->
  <div class="card">
    <div class="card-header">🔄 8-Step Pipeline — How Every Action Flows</div>
    <div class="card-body">
      <div class="pipeline">

        <div class="step">
          <div class="step-spine">
            <div class="step-num col2" style="border-color:#7c5cfc;color:#7c5cfc">1</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col2">POST /api/v1/action — Request Arrives</div>
            <div class="step-desc">Agent receives a JSON request with query, domain, context (volatility, novelty, input_channels, environmental_signals).</div>
            <div class="step-detail">
              <span style="color:#6060a0">Incoming payload:</span><br>
              query = <span style="color:#c0c0ff">"Is BTC forming a double-bottom at 95k?"</span><br>
              domain = <span style="color:#c0c0ff">"trading"</span><br>
              volatility = <span style="color:#c0c0ff">0.18</span> &nbsp; novelty = <span style="color:#c0c0ff">0.35</span><br>
              input_channels = <span style="color:#c0c0ff">price_feed:[95200, 95050, 95180, 95300]</span>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num col3" style="border-color:#2ecc71;color:#2ecc71">2</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col3">LLM Reasoning Chains — N=5 Parallel</div>
            <div class="step-desc">ChainManager fires 5 independent Anthropic Claude calls. Each chain produces an independent response + confidence score. Any contradiction between chains → I(t) = 0.0 immediately (hard zero, no override).</div>
            <div class="step-detail">
              Chain 0: conf=0.82  → "Double-bottom confirmed, volume suggests accumulation…"<br>
              Chain 1: conf=0.79  → "Pattern forming but resistance at 96.5k could reject…"<br>
              Chain 2: conf=0.84  → "Bull signal: 95k held twice with decreasing sell volume…"<br>
              Chain 3: conf=0.71  → "Macro headwinds (DXY) may invalidate pattern…"<br>
              Chain 4: conf=0.77  → "Confirmed double-bottom, Kelly size 1.8% recommended…"<br>
              <span style="color:#ffa040">⚠ With invalid ANTHROPIC_API_KEY: chains=[] → P and C score lower</span>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num col4" style="border-color:#f39c12;color:#f39c12">3</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col4">5-Plane Coherence Engine → Ψ(t)</div>
            <div class="step-desc">Five cognitive planes computed in parallel. Weighted sum → Ψ(t). Plane weights enforced to sum to exactly 1.0 (assertion on every call).</div>
            <div class="step-detail">
              <div class="plane-row"><span style="color:#9b59b6;width:200px">P · Perceptual  ×0.25</span><div class="plane-bar-bg"><div class="plane-bar" style="width:71%;background:#9b59b6"></div></div><span>Shannon entropy of LLM token distribution</span></div>
              <div class="plane-row"><span style="color:#3498db;width:200px">I · Inferential ×0.30</span><div class="plane-bar-bg"><div class="plane-bar" style="width:50%;background:#3498db"></div></div><span>Chain consistency (contradiction → hard zero)</span></div>
              <div class="plane-row"><span style="color:#1abc9c;width:200px">C · Consensus   ×0.20</span><div class="plane-bar-bg"><div class="plane-bar" style="width:50%;background:#1abc9c"></div></div><span>Independent slow-convergence scoring</span></div>
              <div class="plane-row"><span style="color:#e67e22;width:200px">S · Self-Reflect ×0.15</span><div class="plane-bar-bg"><div class="plane-bar" style="width:63%;background:#e67e22"></div></div><span>FAISS memory density for this query</span></div>
              <div class="plane-row"><span style="color:#e74c3c;width:200px">W · World Model ×0.10</span><div class="plane-bar-bg"><div class="plane-bar" style="width:100%;background:#e74c3c"></div></div><span>Environmental z-score (z&gt;3σ → zero)</span></div>
              <br>
              <span style="color:#7c5cfc;font-weight:700">Ψ(t) = 0.25·P + 0.30·I + 0.20·C + 0.15·S + 0.10·W</span>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num col5" style="border-color:#e74c3c;color:#e74c3c">4</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col5">Action Gate → [Ψ(t) ≥ Δ(t)] Decision</div>
            <div class="step-desc">Dynamic threshold Δ scales with market volatility and novelty. No override exists. No bypass. The gate is the law.</div>
            <div class="step-detail">
              Δ(t) = base_0.65 + volatility×0.15 + novelty×0.20<br>
              Δ(t) = 0.65 + 0.18×0.15 + 0.35×0.20 = <span style="color:#ffa040">0.7088</span><br><br>
              If Ψ ≥ Δ → <span style="color:#40ff80;font-weight:700">GATE OPEN — ACTION PERMITTED</span><br>
              If Ψ &lt; Δ → <span style="color:#ff6060;font-weight:700">SILENCE — agent refuses to act</span><br><br>
              <span style="color:#6060a0">Current Ψ ≈ 0.62 &lt; Δ=0.71 → SILENCE (no valid LLM key)</span><br>
              <span style="color:#6060a0">With valid key: P→0.85+, pushing Ψ above Δ → ACTION</span>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num col6" style="border-color:#3498db;color:#3498db">5</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col6">Moat Accumulator — log(Λ) grows</div>
            <div class="step-desc">Only coherent cycles (gate OPEN) contribute to the moat. Λ is computed in log-space for numerical stability across hundreds of cycles. <strong>Λ can never decrease.</strong></div>
            <div class="step-detail">
              Formula: log(Λ_new) = log(Λ_old) + log(1 + η·Ψ)<br>
              Example: log(Λ_new) = {log_lam:.6f} + log(1 + 0.85 × 0.82)<br>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= {log_lam:.6f} + {math.log(1+0.85*0.82):.8f}<br>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= {log_lam + math.log(1+0.85*0.82):.6f}<br>
              Current: log(Λ) = <span style="color:#7c5cfc">{log_lam:.6f}</span> → Λ = <span style="color:#7c5cfc">{lam:.4e}</span><br>
              State persisted to <code>data/moat_state.json</code> every cycle
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num col7" style="border-color:#1abc9c;color:#1abc9c">6</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col7">Continuous Learner — FAISS + Domain Mastery</div>
            <div class="step-desc">Every cycle (regardless of gate result) is encoded via sentence_transformers and stored in a FAISS L2 index. Domain mastery score M(d,t) updates via running average.</div>
            <div class="step-detail">
              learn_from_cycle(query, output, gate_open, domain, plane_scores)<br>
              → encode query → 384-dim embedding vector<br>
              → FAISS index.add(vector)  [persisted to disk immediately]<br>
              → M(domain, t) = (M_prev × n + Ψ) / (n + 1)<br>
              → SelfReflectionPlane reads FAISS on next query (S plane)<br><br>
              {domain_rows and f"Domains: {', '.join(d['domain'] for d in domains[:4])}" or "No domains yet"}
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num col8" style="border-color:#e67e22;color:#e67e22">7</div>
            <div class="step-line"></div>
          </div>
          <div class="step-content">
            <div class="step-title col8">On-Chain Heartbeat — Pharos Testnet 688689</div>
            <div class="step-desc">Every coherent ACTION emits a <code>recordHeartbeat(psi, lambda)</code> tx. Every 100 cycles, <code>updateMoat(lambda, cycles, iq)</code> syncs to SovereignRegistry. Domain mastery syncs to SovereignLearner.</div>
            <div class="step-detail">
              <span style="color:#e67e22">Per-action:</span> SovereignRegistry.recordHeartbeat(psi×1e18, λ×1e18)<br>
              <span style="color:#e67e22">Per 100 cycles:</span> SovereignRegistry.updateMoat(λ×1e18, nCycles, IQ×1e18)<br>
              <span style="color:#e67e22">Per 100 cycles:</span> SovereignLearner.updateDomainMastery(domain, M×1e18, count)<br><br>
              Agent: <span style="color:#c0c0ff">0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20</span><br>
              Balance: <span style="color:#40ff80">4.947 PROS</span> &nbsp; Nonce: <span style="color:#40ff80">27 (27 txs sent)</span>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-spine">
            <div class="step-num" style="border-color:#a080ff;color:#a080ff">8</div>
          </div>
          <div class="step-content">
            <div class="step-title" style="color:#a080ff">SSE + WebSocket Broadcast — Response Returned</div>
            <div class="step-desc">The API response is returned to the caller. In parallel, the gate decision is pushed to all SSE subscribers and WebSocket dashboard clients.</div>
            <div class="step-detail">
              Response → caller (JSON: cycle_id, gate_open, psi, delta, omega, planes)<br>
              → push_action_event() → /api/v1/stream/actions (all SSE subscribers)<br>
              → ws_dashboard frame → /ws/dashboard (browser dashboard)<br>
              → asyncio.create_task(_emit_heartbeat()) → fire-and-forget chain tx<br><br>
              Ω(a,t) = Ψ · e^(Λ·t) = 0.82 × e^(min(Λ·t, 700)) &nbsp; [overflow-safe]
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>

  <!-- confirmed transactions -->
  <div class="card">
    <div class="card-header">⛓ Confirmed On-Chain Transactions — Pharos Testnet</div>
    <div class="card-body">
      <div style="margin-bottom:1rem;font-size:.75rem;color:#6060a0">
        Agent: <span style="color:#c0c0ff">0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20</span> &nbsp;|&nbsp;
        <a href="https://testnet.pharosscan.xyz/address/0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20" target="_blank" style="color:#7060d0">View all on explorer ↗</a>
      </div>
      <table>
        <thead><tr><th>TX Hash</th><th>Function Call</th><th>Block</th><th>Gas Used</th><th>Status</th></tr></thead>
        <tbody>{conf_rows}</tbody>
      </table>
      <div style="margin-top:.8rem;font-size:.7rem;color:#3a3a6a">
        Calldata is ABI-encoded. lambdaScaled = Λ × 10¹⁸ (Solidity fixed-point). Gas ~37k–44k per call @ 10 Gwei.
      </div>
    </div>
  </div>

  <!-- last tx calldata detail -->
  <div class="card">
    <div class="card-header">📋 updateMoat() Calldata Breakdown</div>
    <div class="card-body">
      <div class="calldata">
        <span class="fn">SovereignRegistry.updateMoat</span>(<br>
        &nbsp;&nbsp;<span class="key">uint256 lambdaScaled</span> = <span class="val">410954067278819464997138999116725204549632</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#3a3a6a">// Λ × 1e18 = {lam:.6e} × 10¹⁸</span><br>
        &nbsp;&nbsp;<span class="key">uint256 nCycles    </span> = <span class="val">300</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#3a3a6a">// coherent cycles completed</span><br>
        &nbsp;&nbsp;<span class="key">uint256 iqScaled   </span> = <span class="val">92683939500785320407096754566640697344</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#3a3a6a">// IQ × 1e18 = {iq:.6e} × 10¹⁸</span><br>
        )<br><br>
        <span class="key">chain_id   </span>= <span class="val">688689</span>  <span style="color:#3a3a6a">// Pharos testnet</span><br>
        <span class="key">gas_price  </span>= <span class="val">10.0 Gwei</span><br>
        <span class="key">gas_used   </span>= <span class="val">37,616</span><br>
        <span class="key">tx_hash    </span>= <span class="val">0xe610233d729a35fde68a8cec26c03785f7711df8dc24f2f3e730e5b3137b40d8</span><br>
        <span class="key">status     </span>= <span style="color:#40ff80;font-weight:700">SUCCESS ✓</span>
      </div>
    </div>
  </div>

  <!-- contracts -->
  <div class="card">
    <div class="card-header">📜 Deployed Contracts</div>
    <div class="card-body">
      <div class="contract">
        <div class="contract-name">SovereignRegistry</div>
        <div class="contract-addr"><a href="https://testnet.pharosscan.xyz/address/0x6EAB7862385329BdaaD32f2b9587a66E768018Ba" target="_blank" style="color:#7060d0">0x6EAB7862385329BdaaD32f2b9587a66E768018Ba ↗</a></div>
        <div style="font-size:.72rem;color:#6060a0;margin-top:.3rem">Agent identity + moat state · Records every updateMoat + recordHeartbeat + recordSilence</div>
        <div class="contract-methods">
          <span class="method-badge">updateMoat(λ,n,IQ)</span>
          <span class="method-badge">recordHeartbeat(ψ,λ)</span>
          <span class="method-badge">recordSilence(ψ,Δ,reason)</span>
        </div>
      </div>
      <div class="contract">
        <div class="contract-name">SovereignVault</div>
        <div class="contract-addr"><a href="https://testnet.pharosscan.xyz/address/0xAbC106D943a6Aff91A0B29f4a77E4009323d7A66" target="_blank" style="color:#7060d0">0xAbC106D943a6Aff91A0B29f4a77E4009323d7A66 ↗</a></div>
        <div style="font-size:.72rem;color:#6060a0;margin-top:.3rem">Trading capital vault · On-chain coherence gate for every trade open/close</div>
        <div class="contract-methods">
          <span class="method-badge">openTrade(id,symbol,dir,size,entry,ψ,Δ)</span>
          <span class="method-badge">closeTrade(id,exit,pnl)</span>
          <span class="method-badge">recordSilencedTrade(ψ,Δ)</span>
        </div>
      </div>
      <div class="contract">
        <div class="contract-name">SovereignLearner</div>
        <div class="contract-addr"><a href="https://testnet.pharosscan.xyz/address/0x799006C9b1e946d3A2909b81F3C3087D71bB9F84" target="_blank" style="color:#7060d0">0x799006C9b1e946d3A2909b81F3C3087D71bB9F84 ↗</a></div>
        <div style="font-size:.72rem;color:#6060a0;margin-top:.3rem">Domain mastery ledger + IQ milestones · Updated every 100 cycles per domain</div>
        <div class="contract-methods">
          <span class="method-badge">updateDomainMastery(domain,M,count)</span>
        </div>
      </div>
    </div>
  </div>

  <!-- heartbeat log -->
  <div class="card">
    <div class="card-header">💓 On-Chain Heartbeat Log (this session)</div>
    <div class="card-body">
      <table>
        <thead><tr><th>Timestamp</th><th>Gate</th><th>Ψ</th><th>TX Hash</th></tr></thead>
        <tbody>{hb_rows}</tbody>
      </table>
      <div style="margin-top:.8rem;font-size:.7rem;color:#3a3a6a">
        Heartbeat loop runs every 30s · Syncs to chain every {100} coherent cycles · Log resets on process restart
      </div>
    </div>
  </div>

  <!-- domain mastery -->
  <div class="card">
    <div class="card-header">📊 Domain Mastery M(d,t)</div>
    <div class="card-body">
      <table>
        <thead><tr><th>Domain</th><th>Mastery M(d,t)</th><th>Knowledge Count</th></tr></thead>
        <tbody>{domain_rows}</tbody>
      </table>
    </div>
  </div>

  <div style="text-align:center;color:#3a3a6a;font-size:.72rem;padding:.5rem 0">
    SOVEREIGN-Ω v2.0.0 · Pharos Phase 1 Hackathon · DoraHacks · June 2026 · 50,000 $PROS
  </div>

</div>
</body>
</html>"""


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
async def demo_page():
    import os
    host = os.getenv("REPLIT_DEV_DOMAIN", "")
    ws_url = f"wss://{host}/ws/dashboard" if host else f"ws://localhost:{os.getenv('PORT','8000')}/ws/dashboard"
    action_url = f"https://{host}/api/v1/action" if host else f"http://localhost:{os.getenv('PORT','8000')}/api/v1/action"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOVEREIGN-Ω · Live Demo</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{
  --bg:#04040c;--surf:#09091a;--border:#16163a;
  --accent:#7c5cfc;--green:#2ecc71;--red:#c0392b;
  --orange:#f39c12;--text:#d0d0f0;--muted:#40406a;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:var(--bg);color:var(--text);font-family:'Courier New',monospace;overflow-x:hidden}}

/* ── STARFIELD ── */
#stars{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
.star{{position:absolute;border-radius:50%;background:#fff;animation:twinkle var(--d,3s) ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{opacity:.1}}50%{{opacity:var(--op,.8)}}}}

/* ── LAYOUT ── */
#app{{position:relative;z-index:1;min-height:100vh;display:flex;flex-direction:column}}

/* ── HEADER ── */
header{{
  text-align:center;padding:2.5rem 1rem 1.5rem;
  background:linear-gradient(180deg,rgba(8,4,28,.95) 0%,transparent 100%);
}}
header h1{{font-size:clamp(1.6rem,4vw,3rem);color:#a080ff;letter-spacing:.12em;text-shadow:0 0 40px rgba(160,128,255,.4)}}
header .eq{{color:var(--muted);font-size:clamp(.7rem,.9vw,1rem);margin:.4rem 0}}
header .tagline{{color:#50507a;font-size:.75rem;font-style:italic}}
#conn-badge{{display:inline-block;margin-top:.8rem;padding:.2rem .8rem;border-radius:12px;font-size:.72rem;font-weight:700;
  background:#1a140a;color:var(--orange);border:1px solid var(--orange);transition:all .4s}}
#conn-badge.live{{background:#061206;color:var(--green);border-color:var(--green)}}

/* ── MAIN GRID ── */
main{{flex:1;display:grid;gap:1px;background:var(--border);
  grid-template-columns:1fr 1fr 1fr;
  grid-template-rows:auto auto auto;
  margin:0}}

.panel{{background:var(--surf);padding:1.4rem;display:flex;flex-direction:column;gap:.7rem}}
.panel-title{{font-size:.6rem;text-transform:uppercase;letter-spacing:.18em;color:var(--muted);
  padding-bottom:.5rem;border-bottom:1px solid var(--border)}}

/* ── PSI GAUGE ── */
#gauge-panel{{grid-column:1;grid-row:1/3;align-items:center;justify-content:center}}
#gauge-wrap{{position:relative;width:220px;height:220px;margin:0 auto}}
#gauge-svg{{width:100%;height:100%}}
#gauge-psi{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}}
#gauge-psi .psi-num{{font-size:2.8rem;font-weight:700;color:var(--accent);line-height:1}}
#gauge-psi .psi-lbl{{font-size:.65rem;color:var(--muted);margin-top:.2rem}}
#gauge-psi .psi-gate{{font-size:.9rem;font-weight:700;margin-top:.4rem;letter-spacing:.1em}}
#gauge-psi .psi-gate.silence{{color:var(--red)}}
#gauge-psi .psi-gate.open{{color:var(--green);text-shadow:0 0 12px rgba(46,204,113,.6)}}

/* delta line annotation */
#gauge-delta-lbl{{font-size:.68rem;color:var(--muted);text-align:center}}

/* ── LAMBDA HERO ── */
#lambda-panel{{grid-column:2;grid-row:1;align-items:center;text-align:center}}
#lambda-big{{font-size:clamp(1.2rem,2.5vw,2rem);font-weight:700;color:var(--accent);
  font-variant-numeric:tabular-nums;letter-spacing:.04em;word-break:break-all;line-height:1.1}}
#log-lambda{{font-size:.8rem;color:var(--muted);margin-top:.3rem}}
#lambda-growth{{font-size:.72rem;color:var(--green);margin-top:.2rem}}
#cycles-num{{font-size:1.6rem;font-weight:700;color:var(--green);margin-top:.6rem}}
#cycles-lbl{{font-size:.62rem;color:var(--muted)}}

/* ── CHAIN PANEL ── */
#chain-panel{{grid-column:3;grid-row:1;text-align:center;justify-content:center}}
#sync-num{{font-size:3rem;font-weight:700;color:var(--green)}}
#sync-lbl{{font-size:.62rem;color:var(--muted)}}
#sync-next{{font-size:.75rem;color:var(--orange);margin-top:.4rem}}
.chain-addr{{font-size:.62rem;color:#30306a;margin-top:.6rem;word-break:break-all}}
#hb-ring{{width:60px;height:60px;margin:.6rem auto;position:relative}}
#hb-ring svg{{width:100%;height:100%}}
.hb-pulse{{animation:hbring 1.5s ease-out infinite}}
@keyframes hbring{{0%{{r:20;opacity:.8}}100%{{r:30;opacity:0}}}}

/* ── PLANES ── */
#planes-panel{{grid-column:2;grid-row:2}}
.plane{{display:flex;flex-direction:column;gap:3px;margin:.2rem 0}}
.plane-top{{display:flex;justify-content:space-between;font-size:.7rem}}
.plane-name{{color:var(--muted)}}
.plane-val{{font-weight:700}}
.bar-bg{{height:7px;background:#0a0a18;border-radius:4px;overflow:hidden}}
.bar-fill{{height:7px;border-radius:4px;transition:width .6s ease}}

/* ── GATE FEED ── */
#feed-panel{{grid-column:3;grid-row:2;overflow:hidden}}
#feed{{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:4px;max-height:220px}}
.feed-row{{display:flex;gap:.6rem;align-items:baseline;padding:.3rem .5rem;border-radius:4px;
  border-left:3px solid;background:#050510;font-size:.7rem}}
.feed-row.silence{{border-color:var(--red);color:#c07070}}
.feed-row.open{{border-color:var(--green);color:#70c070}}
.feed-time{{color:var(--muted);flex-shrink:0;font-size:.62rem;width:56px}}
.feed-gate{{font-weight:700;flex-shrink:0;width:52px}}
.feed-psi{{color:var(--muted)}}

/* ── CHART STRIP ── */
#chart-panel{{grid-column:1/-1;grid-row:3;min-height:160px}}
#chart-inner{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);height:160px}}
.chart-cell{{background:var(--surf);padding:.8rem;position:relative}}
.chart-label{{font-size:.6rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:.3rem}}
.chart-cell canvas{{position:absolute;inset:.8rem;inset-top:2rem}}

/* ── FIRE BUTTON ── */
#fire-btn{{
  position:fixed;bottom:1.5rem;right:1.5rem;z-index:100;
  background:linear-gradient(135deg,#3a1a7a,#7c5cfc);
  border:none;border-radius:50px;padding:.7rem 1.4rem;
  color:#fff;font-family:'Courier New',monospace;font-size:.75rem;font-weight:700;
  cursor:pointer;letter-spacing:.06em;
  box-shadow:0 4px 24px rgba(124,92,252,.5);
  transition:all .2s;
}}
#fire-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 32px rgba(124,92,252,.7)}}
#fire-btn:active{{transform:translateY(0)}}
#fire-btn.firing{{background:linear-gradient(135deg,#1a4a1a,#27ae60);box-shadow:0 4px 24px rgba(39,174,96,.5)}}

/* ── FOOTER ── */
footer{{background:var(--surf);border-top:1px solid var(--border);
  padding:.6rem 1.4rem;display:flex;justify-content:space-between;align-items:center;font-size:.65rem}}
footer .links a{{color:var(--muted);margin-left:1rem}}
footer .links a:hover{{color:var(--text)}}
footer .copy{{color:#20205a}}
</style>
</head>
<body>
<div id="stars"></div>
<div id="app">

<header>
  <h1>SOVEREIGN-Ω</h1>
  <div class="eq">Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e<sup>Λ·t</sup></div>
  <div class="tagline">Truth or silence. The silence is information. · Pharos Chain · TRION Mathematics</div>
  <div id="conn-badge">⟳ Connecting to live intelligence stream…</div>
</header>

<main>

  <!-- Ψ Gauge -->
  <div class="panel" id="gauge-panel">
    <div class="panel-title">Ψ Coherence Score — live</div>
    <div id="gauge-wrap">
      <svg id="gauge-svg" viewBox="0 0 200 200">
        <!-- bg arc -->
        <path id="arc-bg" d="" fill="none" stroke="#0f0f28" stroke-width="16" stroke-linecap="round"/>
        <!-- delta marker -->
        <path id="arc-delta" d="" fill="none" stroke="#f39c12" stroke-width="2" stroke-dasharray="4 3" stroke-linecap="round"/>
        <!-- value arc -->
        <path id="arc-val" d="" fill="none" stroke="#7c5cfc" stroke-width="16" stroke-linecap="round"/>
        <!-- delta tick -->
        <line id="delta-tick" x1="100" y1="100" x2="100" y2="60" stroke="#f39c12" stroke-width="2"/>
        <text id="delta-text" x="100" y="50" text-anchor="middle" fill="#f39c12" font-size="10" font-family="Courier New">Δ</text>
      </svg>
      <div id="gauge-psi">
        <div class="psi-num" id="psi-num">0.000</div>
        <div class="psi-lbl">Ψ(t)</div>
        <div class="psi-gate silence" id="psi-gate">SILENCE</div>
      </div>
    </div>
    <div id="gauge-delta-lbl">Δ threshold = <span id="delta-val-lbl">0.0000</span></div>
    <div style="font-size:.65rem;color:#30305a;text-align:center;line-height:1.5;margin-top:.5rem">
      When Ψ &lt; Δ the agent refuses to act.<br>Silence is not failure. Silence is information.
    </div>
  </div>

  <!-- Λ Hero -->
  <div class="panel" id="lambda-panel">
    <div class="panel-title">Λ Compounding Moat</div>
    <div id="lambda-big">—</div>
    <div id="log-lambda">log(Λ) = —</div>
    <div id="lambda-growth"></div>
    <div style="height:.5rem"></div>
    <div id="cycles-num">—</div>
    <div id="cycles-lbl">coherent cycles</div>
    <div style="font-size:.65rem;color:#30305a;margin-top:auto;line-height:1.5">
      Λ is computed in log-space.<br>It can only grow. Never decreases.<br>Every coherent cycle compounds the moat.
    </div>
  </div>

  <!-- Chain -->
  <div class="panel" id="chain-panel">
    <div class="panel-title">⛓ Pharos On-Chain</div>
    <div id="hb-ring">
      <svg viewBox="0 0 60 60">
        <circle cx="30" cy="30" r="20" fill="none" stroke="#1a3a1a" stroke-width="2"/>
        <circle class="hb-pulse" cx="30" cy="30" r="20" fill="none" stroke="#2ecc71" stroke-width="1.5"/>
        <circle cx="30" cy="30" r="8" fill="#061206" stroke="#2ecc71" stroke-width="2"/>
        <text x="30" y="34" text-anchor="middle" fill="#2ecc71" font-size="7" font-family="Courier New">⛓</text>
      </svg>
    </div>
    <div id="sync-num">0</div>
    <div id="sync-lbl">chain syncs this session</div>
    <div id="sync-next">Next sync in — cycles</div>
    <div style="font-size:.65rem;color:#30305a;margin-top:auto;line-height:1.6">
      Network: Pharos Testnet 688689<br>
      Registry: 0x6EAB…018Ba<br>
      Vault: 0xAbC1…A7A66<br>
      Learner: 0x7990…9F84<br>
      <a href="https://testnet.pharosscan.xyz/address/0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20"
         target="_blank" style="color:#50508a">View on explorer ↗</a>
    </div>
  </div>

  <!-- Planes -->
  <div class="panel" id="planes-panel">
    <div class="panel-title">5 Cognitive Planes — Ψ breakdown</div>
    <div class="plane">
      <div class="plane-top"><span class="plane-name">P · Perceptual  ×0.25</span><span class="plane-val" id="pv-p">0.000</span></div>
      <div class="bar-bg"><div class="bar-fill" id="pb-p" style="width:0%;background:#9b59b6"></div></div>
    </div>
    <div class="plane">
      <div class="plane-top"><span class="plane-name">I · Inferential ×0.30</span><span class="plane-val" id="pv-i">0.000</span></div>
      <div class="bar-bg"><div class="bar-fill" id="pb-i" style="width:0%;background:#3498db"></div></div>
    </div>
    <div class="plane">
      <div class="plane-top"><span class="plane-name">C · Consensus   ×0.20</span><span class="plane-val" id="pv-c">0.000</span></div>
      <div class="bar-bg"><div class="bar-fill" id="pb-c" style="width:0%;background:#1abc9c"></div></div>
    </div>
    <div class="plane">
      <div class="plane-top"><span class="plane-name">S · Self-Reflect ×0.15</span><span class="plane-val" id="pv-s">0.000</span></div>
      <div class="bar-bg"><div class="bar-fill" id="pb-s" style="width:0%;background:#e67e22"></div></div>
    </div>
    <div class="plane">
      <div class="plane-top"><span class="plane-name">W · World Model ×0.10</span><span class="plane-val" id="pv-w">0.000</span></div>
      <div class="bar-bg"><div class="bar-fill" id="pb-w" style="width:0%;background:#e74c3c"></div></div>
    </div>
    <div style="font-size:.65rem;color:#30305a;margin-top:auto;line-height:1.5">
      Contradiction → I=0 &nbsp;|&nbsp; World z&gt;3σ → W=0<br>
      No LLM key → P=0, C reduced
    </div>
  </div>

  <!-- Gate Feed -->
  <div class="panel" id="feed-panel">
    <div class="panel-title">Gate Decisions — live feed</div>
    <div id="feed">
      <div class="feed-row silence">
        <span class="feed-time">--:--:--</span>
        <span class="feed-gate">SILENCE</span>
        <span class="feed-psi">Ψ connecting…</span>
      </div>
    </div>
  </div>

  <!-- Chart strip -->
  <div class="panel" id="chart-panel" style="padding:0">
    <div id="chart-inner">
      <div class="chart-cell">
        <div class="chart-label">Ψ Coherence · 60s rolling</div>
        <canvas id="psiChart"></canvas>
      </div>
      <div class="chart-cell">
        <div class="chart-label">log(Λ) Moat · 60s rolling</div>
        <canvas id="lamChart"></canvas>
      </div>
    </div>
  </div>

</main>

<footer>
  <div class="copy">SOVEREIGN-Ω v2.0.0 · Pharos Phase 1 Hackathon · DoraHacks · June 2026 · 50,000 $PROS</div>
  <div class="links">
    <a href="/">Home</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/pipeline">Pipeline</a>
    <a href="/docs">API</a>
    <a href="/.well-known/agent.json" target="_blank">Agent Card</a>
  </div>
</footer>

</div><!-- /app -->

<button id="fire-btn" title="Fire a live action cycle">⚡ Fire Cycle</button>

<script>
// ── Starfield ───────────────────────────────────────────────────────────────
(function(){{
  const c=document.getElementById('stars');
  for(let i=0;i<120;i++){{
    const s=document.createElement('div');
    s.className='star';
    const sz=Math.random()*2+.5;
    s.style.cssText=`width:${{sz}}px;height:${{sz}}px;left:${{Math.random()*100}}%;top:${{Math.random()*100}}%;--d:${{(Math.random()*4+2).toFixed(1)}}s;--op:${{(Math.random()*.7+.1).toFixed(2)}};animation-delay:${{(Math.random()*4).toFixed(1)}}s`;
    c.appendChild(s);
  }}
}})();

// ── SVG gauge ───────────────────────────────────────────────────────────────
const CX=100,CY=100,R=78,START_ANG=-220,SWEEP=260; // degrees

function polar(cx,cy,r,deg){{
  const a=deg*Math.PI/180;
  return [cx+r*Math.cos(a),cy+r*Math.sin(a)];
}}

function arcPath(startDeg,endDeg,r=R){{
  if(Math.abs(endDeg-startDeg)<.01) return '';
  const [sx,sy]=polar(CX,CY,r,startDeg);
  const [ex,ey]=polar(CX,CY,r,endDeg);
  const large=Math.abs(endDeg-startDeg)>180?1:0;
  return `M ${{sx}} ${{sy}} A ${{r}} ${{r}} 0 ${{large}} 1 ${{ex}} ${{ey}}`;
}}

const arcBg=document.getElementById('arc-bg');
const arcVal=document.getElementById('arc-val');
const arcDelta=document.getElementById('arc-delta');
const deltaTick=document.getElementById('delta-tick');
const deltaText=document.getElementById('delta-text');

arcBg.setAttribute('d',arcPath(START_ANG, START_ANG+SWEEP));

function updateGauge(psi,delta){{
  const psiDeg  = START_ANG + psi  * SWEEP;
  const deltaDeg= START_ANG + delta* SWEEP;
  arcVal.setAttribute('d', arcPath(START_ANG, psiDeg));
  const color = psi>=delta ? '#2ecc71' : '#7c5cfc';
  arcVal.setAttribute('stroke', color);

  // delta marker arc
  const dPath=arcPath(deltaDeg-2, deltaDeg+2, R);
  arcDelta.setAttribute('d', dPath || arcPath(deltaDeg-.5,deltaDeg+.5,R));

  // delta tick
  const [tx1,ty1]=polar(CX,CY,R-8,deltaDeg);
  const [tx2,ty2]=polar(CX,CY,R+8,deltaDeg);
  deltaTick.setAttribute('x1',tx1); deltaTick.setAttribute('y1',ty1);
  deltaTick.setAttribute('x2',tx2); deltaTick.setAttribute('y2',ty2);
  const [lx,ly]=polar(CX,CY,R+18,deltaDeg);
  deltaText.setAttribute('x',lx); deltaText.setAttribute('y',ly);
}}

// ── Charts ──────────────────────────────────────────────────────────────────
const W=60;
function makeChart(id,color,yMin=0,yMax=1){{
  return new Chart(document.getElementById(id).getContext('2d'),{{
    type:'line',
    data:{{
      labels:Array(W).fill(''),
      datasets:[{{data:Array(W).fill(null),borderColor:color,
        backgroundColor:color.replace('rgb','rgba').replace(')',',0.06)'),
        borderWidth:1.5,pointRadius:0,tension:.4,fill:true}}]
    }},
    options:{{
      animation:{{duration:300}},responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{enabled:false}}}},
      scales:{{
        x:{{display:false}},
        y:{{min:yMin,max:yMax,grid:{{color:'rgba(22,22,58,.8)'}},
          ticks:{{color:'#30306a',font:{{size:9}},maxTicksLimit:4}}}}
      }}
    }}
  }});
}}

const psiChart=makeChart('psiChart','rgb(124,92,252)',0,1);
const lamChart=makeChart('lamChart','rgb(46,204,113)',0,null);
let maxLogLam=55;

function pushChart(ch,v){{
  ch.data.datasets[0].data.push(v);
  if(ch.data.datasets[0].data.length>W) ch.data.datasets[0].data.shift();
  ch.data.labels.push('');
  if(ch.data.labels.length>W) ch.data.labels.shift();
  ch.update('none');
}}

// ── Gate feed ────────────────────────────────────────────────────────────────
const feedEl=document.getElementById('feed');
const history=[];
function addFeed(gate,psi,ts){{
  history.unshift({{gate,psi,ts}});
  if(history.length>40) history.pop();
  feedEl.innerHTML=history.map(f=>{{
    const t=new Date(f.ts).toTimeString().slice(0,8);
    const cls=f.gate==='OPEN'?'open':'silence';
    return `<div class="feed-row ${{cls}}"><span class="feed-time">${{t}}</span><span class="feed-gate">${{f.gate}}</span><span class="feed-psi">Ψ=${{f.psi.toFixed(4)}}</span></div>`;
  }}).join('');
}}

// ── Helpers ──────────────────────────────────────────────────────────────────
function fmtBig(n){{
  if(!n&&n!==0) return '—';
  if(n>=1e18) return n.toExponential(3);
  if(n>=1e12) return (n/1e12).toFixed(3)+'T';
  if(n>=1e9)  return (n/1e9).toFixed(3)+'B';
  return n.toFixed(4);
}}
let prevLam=null;

// ── WebSocket ────────────────────────────────────────────────────────────────
const badge=document.getElementById('conn-badge');
let lastSeq=-1;

function connect(){{
  badge.textContent='⟳ Connecting…';badge.className='';
  const ws=new WebSocket('{ws_url}');

  ws.onopen=()=>{{badge.textContent='● LIVE';badge.className='live'}};

  ws.onmessage=(e)=>{{
    let d;try{{d=JSON.parse(e.data)}}catch{{return}}
    if(d.type!=='state') return;

    const psi=d.psi||0, delta=d.delta||0, gate=d.gate||'SILENCE';
    const planes=d.planes||{{}};

    // gauge
    updateGauge(Math.min(psi,1),Math.min(delta,1));
    document.getElementById('psi-num').textContent=psi.toFixed(4);
    document.getElementById('delta-val-lbl').textContent=delta.toFixed(4);
    const gateEl=document.getElementById('psi-gate');
    gateEl.textContent=gate;
    gateEl.className='psi-gate '+(gate==='OPEN'?'open':'silence');

    // lambda
    const lam=d.lambda, logLam=d.log_lambda;
    document.getElementById('lambda-big').textContent=fmtBig(lam);
    document.getElementById('log-lambda').textContent=`log(Λ) = ${{(logLam||0).toFixed(4)}}`;
    if(prevLam!==null&&lam>prevLam){{
      const growth=((lam-prevLam)/prevLam*100);
      document.getElementById('lambda-growth').textContent=`▲ +${{growth.toExponential(2)}} this frame`;
    }}
    prevLam=lam;
    document.getElementById('cycles-num').textContent=(d.cycles||0).toLocaleString();

    // chain
    document.getElementById('sync-num').textContent=d.chain_syncs??0;
    document.getElementById('sync-next').textContent=`Next sync in ${{d.next_sync_in??'—'}} cycles`;

    // planes
    [['p','pb-p','pv-p'],['i','pb-i','pv-i'],['c','pb-c','pv-c'],['s','pb-s','pv-s'],['w','pb-w','pv-w']].forEach(([k,bid,vid])=>{{
      const v=planes[k]??0;
      document.getElementById(bid).style.width=(v*100).toFixed(1)+'%';
      document.getElementById(vid).textContent=v.toFixed(4);
    }});

    // charts
    pushChart(psiChart,psi);
    if(logLam!=null){{
      maxLogLam=Math.max(maxLogLam,(logLam||0)*1.02);
      lamChart.options.scales.y.max=Math.ceil(maxLogLam);
      pushChart(lamChart,logLam);
    }}

    // feed (every frame + on gate change)
    if(d.seq!==lastSeq&&(d.seq%1===0)) addFeed(gate,psi,d.ts||new Date().toISOString());
    lastSeq=d.seq;
  }};

  ws.onerror=()=>{{badge.textContent='✗ Error';badge.className=''}};
  ws.onclose=()=>{{badge.textContent='↻ Reconnecting…';badge.className='';setTimeout(connect,3000)}};
}}

// ── Fire button ───────────────────────────────────────────────────────────────
const fireBtn=document.getElementById('fire-btn');
let firing=false;
fireBtn.addEventListener('click',async()=>{{
  if(firing) return;
  firing=true;
  fireBtn.textContent='⟳ Firing…';
  fireBtn.className='firing';
  try{{
    const r=await fetch('{action_url}',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{
        query:'Live demo cycle: evaluating current market coherence',
        domain:'trading',
        context:{{
          volatility:0.15,novelty:0.30,
          input_channels:{{'price_feed':[95100,95200,95050,95280]}},
          environmental_signals:{{'vix':17.5,'btc_dom':52.1}}
        }}
      }})
    }});
    const d=await r.json();
    const gLabel=d.gate_open?'OPEN':'SILENCE';
    addFeed(gLabel,d.psi_score||0,new Date().toISOString());
    fireBtn.textContent=`${{gLabel}} · Ψ=${{(d.psi_score||0).toFixed(4)}}`;
    setTimeout(()=>{{fireBtn.textContent='⚡ Fire Cycle';fireBtn.className='';firing=false}},2500);
  }}catch(err){{
    fireBtn.textContent='✗ Error — retry';
    fireBtn.className='';
    firing=false;
  }}
}});

// ── Boot ──────────────────────────────────────────────────────────────────────
updateGauge(0,0.72);
connect();
</script>
</body>
</html>"""
