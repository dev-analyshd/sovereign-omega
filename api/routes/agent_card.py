"""
SOVEREIGN-Ω Agent Discovery Card
Implements the A2A (Agent-to-Agent) discovery protocol.
Exposes /.well-known/agent.json and /.well-known/skills.json for Anvita Flow registry.
"""
import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


def _agent_card() -> dict:
    """Build the agent card. Reads runtime env so it's always current."""
    base_url = os.getenv("REPLIT_DEV_DOMAIN", "")
    if base_url:
        base_url = f"https://{base_url}"
    else:
        port = os.getenv("PORT", "8000")
        base_url = f"http://localhost:{port}"

    return {
        "schema_version": "1.0",
        "name": "SOVEREIGN-Ω",
        "description": (
            "Autonomous intelligence agent governed by TRION mathematics. "
            "Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t). "
            "Truth or silence — the silence is information. "
            "Native Pharos chain agent with compounding moat, silence protocol, "
            "multi-plane cognitive reasoning, and x402 payment-gated premium skills."
        ),
        "version": "2.0.0",
        "url": base_url,
        "capabilities": {
            "skills": True,
            "mcp": True,
            "x402": True,
            "a2a": True,
            "streaming": False,
            "push_notifications": False,
        },
        "skills_url": f"{base_url}/api/v1/skills",
        "invoke_url": f"{base_url}/api/v1/skills/invoke/{{skill_id}}",
        "health_url": f"{base_url}/api/v1/health",
        "chain": {
            "name": "Pharos",
            "network": os.getenv("PHAROS_NETWORK", "testnet"),
            "chain_id_testnet": 688689,
            "chain_id_mainnet": 1672,
            "contracts": {
                "registry": os.getenv("PHAROS_REGISTRY", ""),
                "vault": os.getenv("PHAROS_VAULT", ""),
                "learner": os.getenv("PHAROS_LEARNER", ""),
            },
        },
        "x402": {
            "enabled": True,
            "accepted_tokens": ["PROS", "USDC"],
            "facilitator": "https://x402.pharos.xyz/facilitator",
            "network": os.getenv("PHAROS_NETWORK", "testnet"),
        },
        "security": {
            "certik_scan": True,
            "silence_protocol": True,
            "coherence_gated": True,
            "private_key_env_only": True,
        },
        "cognitive_model": {
            "framework": "TRION",
            "planes": ["Perceptual", "Inferential", "Consensus", "Self-Reflection", "World-Model"],
            "weights": {"P": 0.25, "I": 0.30, "C": 0.20, "S": 0.15, "W": 0.10},
            "formula": "Ψ(t) = 0.25·P + 0.30·I + 0.20·C + 0.15·S + 0.10·W",
        },
        "moat": {
            "formula": "log(Λ(t)) = log(Λ₀) + Σ log(1 + ηᵢ·ρᵢ)",
            "lambda_0": 0.01,
            "monotonic": True,
        },
        "provider": {
            "organization": "SOVEREIGN-Ω",
            "contact": "",
        },
    }


@router.get("/.well-known/agent.json", include_in_schema=False)
async def agent_card():
    """A2A agent discovery card. Used by Anvita Flow and agent registries."""
    return JSONResponse(content=_agent_card())


@router.get("/.well-known/skills.json", include_in_schema=False)
async def skills_manifest():
    """Skills manifest for MCP/Anvita Flow skill registry."""
    from api.routes.skills import SKILLS_MANIFEST
    base_url = os.getenv("REPLIT_DEV_DOMAIN", "")
    if base_url:
        base_url = f"https://{base_url}"
    else:
        base_url = f"http://localhost:{os.getenv('PORT', '8000')}"

    manifest = dict(SKILLS_MANIFEST)
    manifest["base_url"] = base_url
    manifest["agent_card_url"] = f"{base_url}/.well-known/agent.json"
    return JSONResponse(content=manifest)


@router.get("/api/v1/agent/discover")
async def discover_agent():
    """Agent self-discovery endpoint for Anvita Flow registration."""
    card = _agent_card()
    from core.moat_accumulator import MoatAccumulator
    from learning.intelligence_score import IntelligenceScorer
    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    iq = await scorer.compute()
    return {
        **card,
        "runtime": {
            "lambda": moat.get_current_lambda(),
            "n_cycles": moat.n_cycles,
            "iq_score": iq,
            "status": "ONLINE",
        },
    }


@router.get("/api/v1/agent/peers")
async def list_peers():
    """
    Agent-to-Agent (A2A) peer listing.
    Returns known peer agents in the SOVEREIGN-Ω network.
    Extensible — add peer discovery via Pharos chain events.
    """
    return {
        "agent_id": "sovereign-omega",
        "peers": [],
        "peer_discovery": "chain-events",
        "registry": os.getenv("PHAROS_REGISTRY", "not-deployed"),
        "note": "Peer agents discovered via Pharos Registry on-chain events",
    }
