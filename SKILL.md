---
name: sovereign-omega
description: Autonomous on-chain intelligence agent for Pharos blockchain — TRION cognitive coherence scoring, x402 machine-to-machine payments, compounding moat (Λ), and MCP-compatible skills.
---

# SOVEREIGN-Ω Agent Skill

SOVEREIGN-Ω is an autonomous intelligence agent built natively on Pharos chain. It exposes 6 reusable MCP-compatible skills, gated by a 5-plane cognitive coherence framework (TRION). Premium skills require an x402 micro-payment in $PROS or USDC before invocation.

## When to Use This Skill

- You need an autonomous on-chain agent that evaluates its own cognitive coherence before acting
- You want to invoke reusable AI skills that are metered and paid via x402 ($PROS / USDC) on Pharos Atlantic testnet
- You want an agent that discovers and federates with other agents via A2A (`/.well-known/agent.json`)
- You need trading analysis with Kelly criterion + Bayesian edge calculations
- You need multi-step parallel reasoning chains with contradiction detection

## Available Skills

| Skill ID | Tier | What it does |
|---|---|---|
| `coherence_evaluate` | Free | TRION Ψ score across 5 cognitive planes — returns gate decision (act or silence) |
| `moat_status` | Free | Live Λ (moat), IQ score, cycle count, and compounding projection |
| `intelligence_score` | Free | Full IQ breakdown with domain mastery per topic |
| `silence_check` | Free | Should this specific action be silenced? Returns boolean + reason |
| `trade_evaluate` | **Premium** (1.0 PROS / 0.10 USDC) | Autonomous trading analysis: Kelly sizing, Bayesian edge, risk management |
| `reasoning_chain` | **Premium** (2.0 PROS / 0.20 USDC) | 5 parallel reasoning chains — contradiction detection, best answer returned |

## How to Invoke (Free Skills)

```bash
# 1. Discover the agent and its live state
curl https://<agent-host>/.well-known/agent.json

# 2. List all available skills
curl https://<agent-host>/api/v1/skills

# 3. Invoke a free skill
curl -X POST https://<agent-host>/api/v1/skills/invoke/coherence_evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "coherence_evaluate",
    "input": {
      "query": "Should I execute this trade?",
      "domain": "trading",
      "context": {
        "volatility": 0.18,
        "novelty": 0.30
      }
    }
  }'
```

## How to Invoke (Premium Skills via x402)

```bash
# Step 1 — Get payment config (amount, token, recipient address)
curl https://<agent-host>/api/v1/x402/config

# Step 2 — Send $PROS or USDC payment on Pharos Atlantic testnet (chain ID 688689)
#   USDC testnet address: 0xE0BE08c77f415F577A1B3A9aD7a1Df1479564ec8
#   Facilitator: https://facilitator.pharos.xyz

# Step 3 — Verify payment and receive a nonce
curl -X POST https://<agent-host>/api/v1/x402/verify \
  -H "Content-Type: application/json" \
  -d '{"tx_hash": "0x<your-tx>", "skill_id": "trade_evaluate", "token": "PROS"}'

# Step 4 — Invoke premium skill with payment proof
curl -X POST https://<agent-host>/api/v1/skills/invoke/trade_evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "trade_evaluate",
    "x402_payment_tx": "0x<your-tx>",
    "input": {
      "symbol": "BTC/USDT",
      "direction": "LONG",
      "market_data": {"price": 95000, "volume_24h": 28000000000}
    }
  }'
```

## MCP Integration

SOVEREIGN-Ω exposes a full MCP JSON-RPC 2.0 endpoint at `/mcp`:

```json
{
  "mcpServers": {
    "sovereign-omega": {
      "url": "https://<agent-host>/api/v1/mcp",
      "transport": "http"
    }
  }
}
```

MCP tools exposed: `coherence_evaluate`, `moat_status`, `intelligence_score`, `silence_check`, `trade_evaluate`, `reasoning_chain`

## Chain Details

- **Network**: Pharos Atlantic Testnet
- **Chain ID**: 688689
- **Contracts**: SovereignRegistry, SovereignVault, SovereignLearner
- **x402 Facilitator**: https://facilitator.pharos.xyz
- **Testnet USDC**: `0xE0BE08c77f415F577A1B3A9aD7a1Df1479564ec8`

## TRION Cognitive Framework

Every action is evaluated through 5 planes before execution:

```
Ψ(t) = 0.25·P(t) + 0.30·I(t) + 0.20·C(t) + 0.15·S(t) + 0.10·W(t)
```

| Plane | Signal | Hard-stop condition |
|---|---|---|
| **P** Perceptual | Shannon entropy of input | — |
| **I** Inferential | Multi-chain reasoning consistency | Contradiction → I = 0.0 |
| **C** Consensus | Slow convergence score | — |
| **S** Self-Reflection | Memory familiarity weighting | — |
| **W** World Model | Environmental anomaly detection | z > 3σ → W = 0.0 |

If Ψ(t) < Δ(t) (dynamic threshold), the agent invokes the **Silence Protocol** — it returns no output. The silence is information.

## Security

- Private keys loaded from environment variables only (never hardcoded)
- Action gate has no override, no bypass — code-enforced
- x402 payment nonces expire in 5 minutes (replay protection)
- Silence Protocol enforced before every social/trading action
- World Model anomaly detection kills W(t) on z > 3σ signals

## Live Demo

- Homepage: `https://<agent-host>/`
- Dashboard: `https://<agent-host>/dashboard`
- Pipeline: `https://<agent-host>/pipeline`
- Swagger: `https://<agent-host>/docs`
- Agent Card: `https://<agent-host>/.well-known/agent.json`
