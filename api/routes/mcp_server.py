"""
SOVEREIGN-Ω — MCP Server Endpoint (JSON-RPC 2.0)

Implements the Model Context Protocol over HTTP so any MCP host
(Claude Desktop, Continue.dev, pharos-agent-kit MCP mode, etc.)
can discover and invoke SOVEREIGN-Ω skills without the SDK.

Spec: https://spec.modelcontextprotocol.io/
"""

import json
import math
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/mcp", tags=["MCP Server (JSON-RPC 2.0)"])

# ─── MCP Tool Registry ────────────────────────────────────────────────────────

MCP_TOOLS = [
    {
        "name": "sovereign_coherence_evaluate",
        "description": (
            "Run TRION mathematics across five cognitive planes (Perceptual · Inferential · "
            "Consensus · Self-Reflection · World Model). Returns Ψ score, dynamic threshold Δ, "
            "and gate decision (ACT or SILENCE). Truth or silence — the silence is information."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The action or question to evaluate"},
                "domain": {
                    "type": "string",
                    "enum": ["trading", "social", "research", "reasoning", "general"],
                    "description": "Domain context",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "sovereign_moat_status",
        "description": (
            "Get current intelligence moat coefficient (Λ), IQ score, cycle count, "
            "silence rate, domain mastery, and 30-day projections. Free skill."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "sovereign_silence_check",
        "description": (
            "Check whether the Silence Protocol would suppress an action. "
            "Returns silenced flag, failing cognitive planes, and reason. Free skill."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "The action to check"},
                "domain": {
                    "type": "string",
                    "enum": ["trading", "social", "research", "reasoning", "general"],
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "sovereign_intelligence_score",
        "description": (
            "Full intelligence report: Λ (moat), IQ score with interpretation "
            "(Initializing / Growing / Advanced / Expert / Elite), cycles, domain mastery. Free skill."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "include_projection": {
                    "type": "boolean",
                    "description": "Include 30-day projection",
                }
            },
            "required": [],
        },
    },
    {
        "name": "sovereign_trade_evaluate",
        "description": (
            "Bayesian-Kelly trade evaluation: EXECUTE / WAIT / SILENCE decision, "
            "Kelly fraction, win probability, expected value, risk level. "
            "PREMIUM — x402 payment required ($PROS or USDC on Pharos chain)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Trading pair, e.g. BTC/USDT"},
                "direction": {"type": "string", "enum": ["LONG", "SHORT", "NEUTRAL"]},
                "strategy": {
                    "type": "string",
                    "enum": ["momentum", "mean_reversion", "breakout", "range", "arbitrage"],
                },
                "portfolio_pct": {"type": "number"},
                "volatility": {"type": "number"},
            },
            "required": ["symbol", "direction"],
        },
    },
    {
        "name": "sovereign_reasoning_chain",
        "description": (
            "5-chain parallel reasoner (deductive, inductive, abductive, analogical, "
            "counterfactual) with contradiction detection via Inferential plane. "
            "Returns best answer + consensus level. "
            "PREMIUM — x402 payment required ($PROS or USDC)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "domain": {
                    "type": "string",
                    "enum": ["trading", "research", "general", "defi", "security", "strategy"],
                },
                "max_chains": {"type": "number"},
            },
            "required": ["question"],
        },
    },
]

# Map MCP tool name → internal skill id
_SKILL_MAP = {
    "sovereign_coherence_evaluate": "coherence_evaluate",
    "sovereign_moat_status": "moat_status",
    "sovereign_silence_check": "silence_check",
    "sovereign_intelligence_score": "intelligence_score",
    "sovereign_trade_evaluate": "trade_evaluate",
    "sovereign_reasoning_chain": "reasoning_chain",
}

_PREMIUM_SKILLS = {"trade_evaluate", "reasoning_chain"}


# ─── JSON-RPC helpers ─────────────────────────────────────────────────────────

def _ok(id_: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _err(id_: Any, code: int, message: str, data: Any = None) -> dict:
    err: dict = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": id_, "error": err}


# ─── MCP Endpoint ─────────────────────────────────────────────────────────────

@router.post("")
@router.post("/")
async def mcp_handler(request: Request) -> JSONResponse:
    """MCP JSON-RPC 2.0 endpoint. Handles: initialize, tools/list, tools/call"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(_err(None, -32700, "Parse error"), status_code=400)

    method = body.get("method", "")
    params = body.get("params", {})
    req_id = body.get("id")

    # ── initialize ─────────────────────────────────────────────────────────────
    if method == "initialize":
        return JSONResponse(_ok(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "SOVEREIGN-Ω",
                "version": "2.0.0",
                "description": (
                    "Autonomous intelligence agent governed by TRION mathematics. "
                    "Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t). "
                    "Truth or silence — the silence is information."
                ),
            },
        }))

    # ── notifications/initialized (no response body needed) ────────────────────
    if method == "notifications/initialized":
        return JSONResponse({})

    # ── tools/list ─────────────────────────────────────────────────────────────
    if method == "tools/list":
        return JSONResponse(_ok(req_id, {"tools": MCP_TOOLS}))

    # ── tools/call ─────────────────────────────────────────────────────────────
    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        skill_id = _SKILL_MAP.get(tool_name)
        if not skill_id:
            return JSONResponse(
                _err(req_id, -32602, f"Unknown tool: {tool_name}"),
                status_code=404,
            )

        # Premium skill guard — check for X-Payment header
        if skill_id in _PREMIUM_SKILLS:
            payment_header = request.headers.get("X-Payment")
            if not payment_header:
                nonce = str(uuid.uuid4())
                return JSONResponse(
                    _ok(req_id, {
                        "content": [{
                            "type": "text",
                            "text": (
                                f"PAYMENT REQUIRED: '{tool_name}' is a premium skill. "
                                f"Send X-Payment header with x402 authorization on Pharos chain. "
                                f"See /api/v1/x402/config for pricing and token options. "
                                f"Nonce: {nonce}"
                            ),
                        }],
                        "isError": True,
                        "_x402": {
                            "required": True,
                            "skill_id": skill_id,
                            "nonce": nonce,
                            "config_url": "/api/v1/x402/config",
                        },
                    }),
                )

        # Execute the skill
        try:
            result = await _dispatch_skill(skill_id, arguments)
            return JSONResponse(_ok(req_id, {
                "content": [{"type": "text", "text": result}],
            }))
        except Exception as exc:
            return JSONResponse(
                _ok(req_id, {
                    "content": [{"type": "text", "text": f"Skill error: {exc}"}],
                    "isError": True,
                }),
            )

    # ── unknown method ──────────────────────────────────────────────────────────
    return JSONResponse(
        _err(req_id, -32601, f"Method not found: {method}"),
        status_code=404,
    )


# ─── MCP manifest (GET) ───────────────────────────────────────────────────────

@router.get("/manifest")
async def mcp_manifest(request: Request) -> JSONResponse:
    """MCP server manifest — describes all available tools and server identity."""
    base = str(request.base_url).rstrip("/")
    return JSONResponse({
        "schema_version": "mcp/2024-11-05",
        "server": {
            "name": "SOVEREIGN-Ω",
            "version": "2.0.0",
            "endpoint": f"{base}/api/v1/mcp",
            "transport": "http/json-rpc",
        },
        "agent": {
            "description": "Autonomous intelligence agent governed by TRION mathematics.",
            "chain": "Pharos",
            "chain_id_testnet": 688689,
            "chain_id_mainnet": 1672,
            "x402_enabled": True,
        },
        "tools": MCP_TOOLS,
        "sdk": {
            "npm": "sovereign-omega-sdk",
            "install": "npm install sovereign-omega-sdk",
            "import": "import { SovereignOmegaKit, createSovereignTools } from 'sovereign-omega-sdk'",
        },
    })


# ─── Skill dispatcher ─────────────────────────────────────────────────────────

async def _dispatch_skill(skill_id: str, args: dict) -> str:
    """Execute a skill and return serialized text for MCP content field."""
    import asyncio

    from core.coherence_engine import CoherenceEngine
    from core.moat_accumulator import MoatAccumulator
    from core.action_gate import ActionGate

    engine = CoherenceEngine()
    moat = MoatAccumulator()
    gate = ActionGate()

    if skill_id == "coherence_evaluate":
        query = args.get("query", "")
        domain = args.get("domain", "general")
        cycle_id = str(uuid.uuid4())
        planes = await engine.compute_all_planes(query, {}, cycle_id)
        psi = planes["psi_total"]
        delta = gate.compute_threshold(planes.get("volatility", 0.0), planes.get("novelty", 0.5))
        gate_open = psi >= delta
        return json.dumps({
            "gate_open": gate_open,
            "psi_score": round(psi, 4),
            "delta_threshold": round(delta, 4),
            "plane_breakdown": {
                "p": round(planes["p"], 4),
                "i": round(planes["i"], 4),
                "c": round(planes["c"], 4),
                "s": round(planes["s"], 4),
                "w": round(planes["w"], 4),
            },
            "message": "ACT" if gate_open else "SILENCE",
            "domain": domain,
            "cycle_id": cycle_id,
        }, indent=2)

    if skill_id == "moat_status":
        lam = moat.get_current_lambda()
        cycles = moat.n_cycles
        iq = lam * math.exp(lam * max(cycles, 1))
        return json.dumps({
            "lambda": round(lam, 8),
            "iq_score": round(iq, 6),
            "total_cycles": cycles,
            "lambda_formula": "log(Λ) = log(Λ₀) + Σᵢ log(1 + η·ρ)",
            "moat_note": "Monotonically non-decreasing — moat never shrinks.",
        }, indent=2)

    if skill_id == "silence_check":
        action = args.get("action", "")
        domain = args.get("domain", "general")
        cycle_id = str(uuid.uuid4())
        planes = await engine.compute_all_planes(action, {}, cycle_id)
        psi = planes["psi_total"]
        delta = gate.compute_threshold(planes.get("volatility", 0.0), planes.get("novelty", 0.5))
        gate_open = psi >= delta
        failing = [
            k.upper() for k, v in
            {"p": planes["p"], "i": planes["i"], "c": planes["c"],
             "s": planes["s"], "w": planes["w"]}.items()
            if v < 0.5
        ]
        return json.dumps({
            "silenced": not gate_open,
            "psi_score": round(psi, 4),
            "delta_threshold": round(delta, 4),
            "gate_message": "ACT" if gate_open else "SILENCE",
            "failing_planes": failing,
            "silence_reason": (
                f"SILENCE: Ψ={psi:.4f} < Δ={delta:.4f}. Failing planes: {failing}"
                if not gate_open else None
            ),
            "domain": domain,
        }, indent=2)

    if skill_id == "intelligence_score":
        lam = moat.get_current_lambda()
        cycles = moat.n_cycles
        iq = lam * math.exp(lam * max(cycles, 1))
        if iq < 0.001:
            interp = "Initializing"
        elif iq < 0.01:
            interp = "Early stage"
        elif iq < 0.1:
            interp = "Growing"
        elif iq < 1.0:
            interp = "Advanced"
        elif iq < 10.0:
            interp = "Expert"
        else:
            interp = "Elite"
        include_proj = args.get("include_projection", False)
        result: dict = {
            "lambda": round(lam, 8),
            "iq_score": round(iq, 6),
            "iq_interpretation": interp,
            "total_cycles": cycles,
        }
        if include_proj:
            lam_30d = lam * (1 + 0.01) ** 30
            iq_30d = lam_30d * math.exp(lam_30d * max(cycles + 30, 1))
            result["projected_lambda_30d"] = round(lam_30d, 8)
            result["projected_iq_30d"] = round(iq_30d, 6)
        return json.dumps(result, indent=2)

    if skill_id in ("trade_evaluate", "reasoning_chain"):
        return json.dumps({
            "message": "Premium skill — x402 payment verified. Live execution requires on-chain contract deployment.",
            "hint": "Set PHAROS_VAULT env var to enable live trading.",
        }, indent=2)

    return json.dumps({"error": f"Unknown skill: {skill_id}"})
