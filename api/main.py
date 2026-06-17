import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import action, trade, intelligence, pharos_routes, silence, moat, health
from api.routes import skills, agent_card, x402


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 50)
    print(" SOVEREIGN-Ω STARTING")
    print(" Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)")
    print(" Truth or silence. The silence is information.")
    print("=" * 50 + "\n")

    from learning.intelligence_score import IntelligenceScorer
    from core.moat_accumulator import MoatAccumulator

    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    iq = await scorer.compute()
    print(f"[STARTUP] Λ={moat.get_current_lambda():.8f} | Cycles={moat.n_cycles} | IQ={iq:.8f}")

    # Background: self-improvement loop
    async def self_improve_loop():
        from learning.domain_mastery import DomainMasteryEngine
        mastery = DomainMasteryEngine()
        while True:
            await asyncio.sleep(3600)
            domains = mastery.get_all()
            weak = [d for d in domains if d["mastery_score"] < 0.3]
            if weak:
                print(f"[SELF-IMPROVE] Weak domains: {[d['domain'] for d in weak]}")

    # Background: daily risk reset
    async def daily_reset():
        from trading.risk_manager import RiskManager
        risk = RiskManager()
        while True:
            await asyncio.sleep(86400)
            risk.daily_reset()

    asyncio.create_task(self_improve_loop())
    asyncio.create_task(daily_reset())

    yield

    print("[SOVEREIGN-Ω] Graceful shutdown. Moat preserved.")


app = FastAPI(
    title="SOVEREIGN-Ω",
    description="Autonomous agent. Powered by TRION mathematics. Pharos Chain native.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(action.router, prefix="/api/v1", tags=["Core"])
app.include_router(trade.router, prefix="/api/v1", tags=["Trading"])
app.include_router(intelligence.router, prefix="/api/v1", tags=["Intelligence"])
app.include_router(pharos_routes.router, prefix="/api/v1", tags=["Pharos Chain"])
app.include_router(silence.router, prefix="/api/v1", tags=["Silence"])
app.include_router(moat.router, prefix="/api/v1", tags=["Moat"])

# ── Pharos Phase 1 Hackathon: Skill-to-Agent Dual Cascade ──────────────────
app.include_router(skills.router, prefix="/api/v1", tags=["Agent Skills (MCP)"])
app.include_router(x402.router, prefix="/api/v1", tags=["x402 Payments"])
app.include_router(agent_card.router, tags=["Agent Discovery (A2A)"])
