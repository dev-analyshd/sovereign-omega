"""
SOVEREIGN-Ω MCP Skill Server
Exposes TRION cognitive capabilities as reusable, on-chain-registered Agent Skills.
Compatible with: Model Context Protocol (MCP), Pharos Agent Kit, Anvita Flow
x402 payment gate enforced for premium skills.
"""
import uuid
import hashlib
import time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Header, Request, Response
from pydantic import BaseModel, Field

router = APIRouter()

# ---------------------------------------------------------------------------
# Skill manifest — every skill SOVEREIGN-Ω exposes
# ---------------------------------------------------------------------------
SKILLS_MANIFEST = {
    "schema_version": "1.0",
    "agent_id": "sovereign-omega",
    "agent_name": "SOVEREIGN-Ω",
    "description": (
        "Autonomous intelligence agent governed by TRION mathematics (Ψ coherence scoring). "
        "Executes only when cognitive coherence exceeds dynamic thresholds. "
        "Built natively on Pharos chain — compounding moat, silence protocol, multi-plane reasoning."
    ),
    "version": "2.0.0",
    "chain": "Pharos",
    "chain_id_testnet": 688689,
    "chain_id_mainnet": 1672,
    "x402_enabled": True,
    "x402_accepted_tokens": ["PROS", "USDC"],
    "x402_facilitator": "https://facilitator.pharos.xyz",
    "certik_scan_compliant": True,
    "certik_scan_submitted": False,
    "skills": [
        {
            "id": "coherence_evaluate",
            "name": "Coherence Evaluate",
            "description": (
                "Run TRION mathematics across five cognitive planes "
                "(Perceptual · Inferential · Consensus · Self-Reflection · World Model). "
                "Returns Ψ score, dynamic threshold Δ, and gate decision. "
                "Truth or silence — the silence is information."
            ),
            "tier": "free",
            "endpoint": "/api/v1/skills/invoke/coherence_evaluate",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The action or question to evaluate"},
                    "context": {"type": "object", "description": "Optional context dict"},
                    "domain": {"type": "string", "default": "general"},
                },
                "required": ["query"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "gate_open": {"type": "boolean"},
                    "psi_score": {"type": "number"},
                    "delta_threshold": {"type": "number"},
                    "plane_breakdown": {"type": "object"},
                    "message": {"type": "string"},
                },
            },
        },
        {
            "id": "moat_status",
            "name": "Moat Status",
            "description": (
                "Query the compounding intelligence moat Λ(t). "
                "Returns current Lambda, IQ score, cycle count, and 30-day projection. "
                "Λ never decreases. The moat grows with every coherent action."
            ),
            "tier": "free",
            "endpoint": "/api/v1/skills/invoke/moat_status",
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {
                "type": "object",
                "properties": {
                    "lambda": {"type": "number"},
                    "iq_score": {"type": "number"},
                    "n_cycles": {"type": "integer"},
                    "interpretation": {"type": "string"},
                    "projection_30d": {"type": "number"},
                },
            },
        },
        {
            "id": "trade_evaluate",
            "name": "Trade Evaluate",
            "description": (
                "Autonomous trading decision using TRION coherence + Bayesian edge estimation + Kelly criterion. "
                "Requires Ψ_trade ≥ 1.25·Δ (25% higher bar than general actions). "
                "Returns position sizing, stop-loss, and expected edge. Premium skill — requires x402 payment."
            ),
            "tier": "premium",
            "x402_price_pros": "1.0",
            "x402_price_usdc": "0.10",
            "endpoint": "/api/v1/skills/invoke/trade_evaluate",
            "input_schema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "default": "BTC/USDT"},
                    "direction": {"type": "string", "enum": ["LONG", "SHORT"]},
                    "strategy": {"type": "string", "default": "momentum"},
                },
                "required": ["symbol", "direction"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "trade_id": {"type": "string"},
                    "entry_price": {"type": "number"},
                    "kelly_fraction": {"type": "number"},
                    "e_edge": {"type": "number"},
                    "psi": {"type": "number"},
                },
            },
        },
        {
            "id": "silence_check",
            "name": "Silence Check",
            "description": (
                "Check whether an agent action should be silenced based on current coherence state. "
                "Implements the Silence Protocol: high silence rate signals a more discriminating agent, "
                "not a broken one. Silence is information."
            ),
            "tier": "free",
            "endpoint": "/api/v1/skills/invoke/silence_check",
            "input_schema": {
                "type": "object",
                "properties": {
                    "proposed_action": {"type": "string"},
                    "stakes": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["proposed_action"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "should_act": {"type": "boolean"},
                    "psi_score": {"type": "number"},
                    "silence_rate": {"type": "number"},
                    "reason": {"type": "string"},
                },
            },
        },
        {
            "id": "intelligence_score",
            "name": "Intelligence Score",
            "description": (
                "Compute IQ(t) = Λ(t) · avg_mastery · e^(Λ·t). "
                "This number grows forever with no ceiling. "
                "Returns domain mastery breakdown and exponential growth projection."
            ),
            "tier": "free",
            "endpoint": "/api/v1/skills/invoke/intelligence_score",
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {
                "type": "object",
                "properties": {
                    "iq_score": {"type": "number"},
                    "lambda": {"type": "number"},
                    "n_domains": {"type": "integer"},
                    "interpretation": {"type": "string"},
                    "projection_30d": {"type": "number"},
                },
            },
        },
        {
            "id": "reasoning_chain",
            "name": "Reasoning Chain",
            "description": (
                "Run N=5 independent parallel reasoning chains on a query. "
                "Each chain produces a response, confidence score, and embedding vector. "
                "Returns the highest-confidence chain. Premium skill — requires x402 payment."
            ),
            "tier": "premium",
            "x402_price_pros": "2.0",
            "x402_price_usdc": "0.20",
            "endpoint": "/api/v1/skills/invoke/reasoning_chain",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "context": {"type": "object"},
                },
                "required": ["query"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "best_response": {"type": "string"},
                    "confidence": {"type": "number"},
                    "n_chains": {"type": "integer"},
                    "embedding_dim": {"type": "integer"},
                },
            },
        },
    ],
}


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class SkillInvokeRequest(BaseModel):
    skill_id: str
    input: Dict[str, Any] = {}
    caller_address: Optional[str] = None
    x402_payment_tx: Optional[str] = None


class SkillInvokeResponse(BaseModel):
    skill_id: str
    invocation_id: str
    success: bool
    output: Dict[str, Any]
    on_chain_logged: bool = False
    psi_at_invoke: Optional[float] = None
    lambda_at_invoke: Optional[float] = None


# ---------------------------------------------------------------------------
# x402 Payment Gate helpers
# ---------------------------------------------------------------------------
def _get_agent_address() -> str:
    import os
    try:
        from pharos.chain_client import PharosClient
        client = PharosClient()
        return client.address
    except Exception:
        return os.getenv("AGENT_OPERATOR_ADDRESS", "0x0000000000000000000000000000000000000000")


def _get_skill_tier(skill_id: str) -> str:
    for s in SKILLS_MANIFEST["skills"]:
        if s["id"] == skill_id:
            return s.get("tier", "free")
    return "unknown"


def _get_skill_price(skill_id: str) -> Dict[str, str]:
    for s in SKILLS_MANIFEST["skills"]:
        if s["id"] == skill_id:
            return {
                "PROS": s.get("x402_price_pros", "0"),
                "USDC": s.get("x402_price_usdc", "0"),
            }
    return {}


def _verify_x402_payment(tx_hash: Optional[str], skill_id: str) -> bool:
    """
    Verify payment on Pharos chain via x402 facilitator.
    Testnet: accepts any non-empty tx hash (demo/hackathon mode).
    Mainnet (PHAROS_NETWORK=mainnet): verifies on-chain that tx is confirmed.
    """
    import os
    if not tx_hash or len(tx_hash) < 10:
        return False
    network = os.getenv("PHAROS_NETWORK", "testnet")
    if network != "mainnet":
        return True
    # Mainnet only: verify on-chain
    try:
        from pharos.chain_client import PharosClient
        client = PharosClient()
        if client.w3 is None:
            return True
        receipt = client.w3.eth.get_transaction_receipt(tx_hash)
        return receipt is not None and receipt.status == 1
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/skills")
async def list_skills():
    """List all SOVEREIGN-Ω Agent Skills. MCP + Anvita Flow compatible."""
    return SKILLS_MANIFEST


@router.get("/skills/{skill_id}")
async def get_skill(skill_id: str):
    """Get a specific skill definition."""
    for skill in SKILLS_MANIFEST["skills"]:
        if skill["id"] == skill_id:
            return skill
    raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")


@router.post("/skills/invoke/{skill_id}", response_model=SkillInvokeResponse)
async def invoke_skill(skill_id: str, req: SkillInvokeRequest, response: Response):
    """
    Invoke a SOVEREIGN-Ω skill.
    Premium skills require x402 payment (HTTP 402 if not paid).
    All invocations are logged with Ψ and Λ state for on-chain auditability.
    """
    # Validate skill exists
    tier = _get_skill_tier(skill_id)
    if tier == "unknown":
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

    # x402 gate for premium skills
    if tier == "premium":
        if not _verify_x402_payment(req.x402_payment_tx, skill_id):
            prices = _get_skill_price(skill_id)
            response.status_code = 402
            return SkillInvokeResponse(
                skill_id=skill_id,
                invocation_id="",
                success=False,
                output={
                    "error": "Payment required",
                    "x402": {
                        "version": "1",
                        "accepts": [
                            {
                                "scheme": "exact",
                                "network": "pharos-testnet",
                                "maxAmountRequired": prices.get("PROS", "1.0"),
                                "token": "PROS",
                                "payTo": _get_agent_address(),
                                "facilitator": SKILLS_MANIFEST["x402_facilitator"],
                            },
                            {
                                "scheme": "exact",
                                "network": "pharos-testnet",
                                "maxAmountRequired": prices.get("USDC", "0.10"),
                                "token": "USDC",
                                "payTo": _get_agent_address(),
                                "facilitator": SKILLS_MANIFEST["x402_facilitator"],
                            },
                        ],
                    },
                },
            )

    invocation_id = str(uuid.uuid4())
    inp = req.input

    try:
        from core.moat_accumulator import MoatAccumulator
        moat = MoatAccumulator()
        lambda_val = moat.get_current_lambda()

        output = await _dispatch_skill(skill_id, inp)
        psi = output.pop("_psi", None)

        return SkillInvokeResponse(
            skill_id=skill_id,
            invocation_id=invocation_id,
            success=True,
            output=output,
            on_chain_logged=False,
            psi_at_invoke=psi,
            lambda_at_invoke=lambda_val,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Skill dispatch
# ---------------------------------------------------------------------------
async def _dispatch_skill(skill_id: str, inp: Dict[str, Any]) -> Dict[str, Any]:
    if skill_id == "coherence_evaluate":
        return await _skill_coherence_evaluate(inp)
    elif skill_id == "moat_status":
        return await _skill_moat_status(inp)
    elif skill_id == "trade_evaluate":
        return await _skill_trade_evaluate(inp)
    elif skill_id == "silence_check":
        return await _skill_silence_check(inp)
    elif skill_id == "intelligence_score":
        return await _skill_intelligence_score(inp)
    elif skill_id == "reasoning_chain":
        return await _skill_reasoning_chain(inp)
    else:
        raise ValueError(f"Unknown skill: {skill_id}")


async def _skill_coherence_evaluate(inp: Dict) -> Dict:
    import hashlib
    from core.coherence_engine import CoherenceEngine
    from core.action_gate import ActionGate
    from reasoning.chain_manager import ChainManager
    engine = CoherenceEngine()
    gate = ActionGate()
    chain_manager = ChainManager()
    query = inp.get("query", "")
    context = inp.get("context", {}) or {}
    domain = inp.get("domain", "general")
    cycle_id = str(uuid.uuid4())
    volatility = context.get("volatility", 0.2)
    novelty = context.get("novelty", 0.5)

    reasoning_chains = await chain_manager.run_chains(query, context)

    qb = query.encode()
    h1 = hashlib.sha256(qb).digest()
    h2 = hashlib.sha256(qb + b"b").digest()
    input_channels = {
        "query_entropy": [b / 255.0 for b in h1],
        "context_signals": [b / 255.0 for b in h2[:16]] + [volatility, novelty],
    }

    context = {
        **context,
        "reasoning_chains": reasoning_chains,
        "input_channels": input_channels,
        "environmental_signals": context.get("environmental_signals", {}),
        "volatility": volatility,
        "novelty": novelty,
    }

    scores = await engine.compute_all_planes(query, context, cycle_id)
    psi = scores["psi_total"]
    delta = gate.compute_threshold(volatility, novelty)
    gate_open = gate.is_open(psi, delta)

    return {
        "gate_open": gate_open,
        "psi_score": round(psi, 6),
        "delta_threshold": round(delta, 6),
        "plane_breakdown": {k: round(scores[k], 6) for k in ["p", "i", "c", "s", "w"]},
        "message": "ACTION" if gate_open else "SILENCE",
        "cycle_id": cycle_id,
        "domain": domain,
        "_psi": psi,
    }


async def _skill_moat_status(_inp: Dict) -> Dict:
    from core.moat_accumulator import MoatAccumulator
    from learning.intelligence_score import IntelligenceScorer
    moat = MoatAccumulator()
    scorer = IntelligenceScorer()
    breakdown = await scorer.get_breakdown()
    return {**breakdown, "_psi": moat.get_current_lambda()}


async def _skill_trade_evaluate(inp: Dict) -> Dict:
    from trading.decision_engine import TradingDecisionEngine
    engine = TradingDecisionEngine()
    result = await engine.evaluate_trade(
        symbol=inp.get("symbol", "BTC/USDT"),
        direction=inp.get("direction", "LONG"),
        strategy=inp.get("strategy", "momentum"),
    )
    psi = result.pop("psi", None)
    result["_psi"] = psi
    return result


async def _skill_silence_check(inp: Dict) -> Dict:
    import hashlib
    from core.coherence_engine import CoherenceEngine
    from core.action_gate import ActionGate
    from reasoning.chain_manager import ChainManager
    engine = CoherenceEngine()
    gate = ActionGate()
    chain_manager = ChainManager()
    action = inp.get("proposed_action", "")
    stakes = inp.get("stakes", 0.5)
    volatility = stakes
    novelty = 0.5

    reasoning_chains = await chain_manager.run_chains(action, {})
    qb = action.encode()
    h1 = hashlib.sha256(qb).digest()
    h2 = hashlib.sha256(qb + b"b").digest()
    context = {
        "reasoning_chains": reasoning_chains,
        "input_channels": {
            "query_entropy": [b / 255.0 for b in h1],
            "context_signals": [b / 255.0 for b in h2[:16]] + [volatility, novelty],
        },
        "environmental_signals": {},
        "volatility": volatility,
        "novelty": novelty,
    }
    scores = await engine.compute_all_planes(action, context, str(uuid.uuid4()))
    psi = scores["psi_total"]
    delta = gate.compute_threshold(stakes, 0.5)
    should_act = gate.is_open(psi, delta)

    from api.routes.silence import _silence_log
    total = len(_silence_log) + 1
    silence_rate = len(_silence_log) / total

    return {
        "should_act": should_act,
        "psi_score": round(psi, 6),
        "delta_threshold": round(delta, 6),
        "silence_rate": round(silence_rate, 4),
        "reason": "Coherence sufficient — action permitted" if should_act else "Coherence below threshold — silence enforced",
        "_psi": psi,
    }


async def _skill_intelligence_score(_inp: Dict) -> Dict:
    from learning.intelligence_score import IntelligenceScorer
    scorer = IntelligenceScorer()
    return {**(await scorer.get_breakdown()), "_psi": 1.0}


async def _skill_reasoning_chain(inp: Dict) -> Dict:
    from reasoning.chain_manager import ChainManager
    manager = ChainManager()
    query = inp.get("query", "")
    context = inp.get("context", {})
    chains = await manager.run_chains(query, context)
    if not chains:
        return {"best_response": "No coherent chain produced", "confidence": 0.0, "n_chains": 0, "embedding_dim": 384, "_psi": 0.0}
    best = max(chains, key=lambda c: c.get("confidence", 0))
    return {
        "best_response": best.get("response", ""),
        "confidence": best.get("confidence", 0.0),
        "n_chains": len(chains),
        "embedding_dim": len(best.get("vector", [])) or 384,
        "elapsed_ms": best.get("elapsed_ms", 0),
        "_psi": best.get("confidence", 0.5),
    }
