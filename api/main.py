import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
