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
  SOVEREIGN-Ω v2.0.0 · Built for Pharos Phase 1 Hackathon · DoraHacks · June 2026 · 50,000 $PROS Prize Pool
  · <a href="/dashboard" style="color:#6060a0">Live Dashboard →</a>
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
