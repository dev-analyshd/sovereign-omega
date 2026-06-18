# SOVEREIGN-Ω · Phase 1 Submission
## Pharos "Skill-to-Agent Dual Cascade Hackathon" — DoraHacks

> *Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)*
> *Truth or silence. The silence is information.*

**Live:** https://sovereignomega.onrender.com · **GitHub:** https://github.com/dev-analyshd/sovereign-omega

---

## The 6 Skills (Phase 1 Core Deliverable)

SOVEREIGN-Ω ships **6 reusable MCP Skills** that any AI agent can invoke via HTTP — no TRION runtime required. The SOVEREIGN-Ω agent is the reference implementation that *composes* all 6 skills into a self-governing on-chain entity.

| # | Skill ID | Tier | What It Does | Latency |
|---|---|---|---|---|
| 1 | `coherence_evaluate` | **Free** | TRION Ψ score across 5 cognitive planes — gate decision (ACT or SILENCE) | ~2–5s with LLM |
| 2 | `silence_check` | **Free** | Should this specific action be silenced? Returns boolean + reason | ~2–5s with LLM |
| 3 | `moat_status` | **Free** | Live Λ, IQ, cycle count + 1d/7d/30d/365d compounding projection | <100ms |
| 4 | `intelligence_score` | **Free** | Full IQ breakdown with per-domain mastery scores | <100ms |
| 5 | `trade_evaluate` | **Premium** (1.0 PROS / 0.10 USDC) | Bayesian Kelly trade sizing + coherence gate (Ψ ≥ 1.25·Δ required) | <100ms |
| 6 | `reasoning_chain` | **Premium** (2.0 PROS / 0.20 USDC) | 5 parallel reasoning chains — contradiction detection, best returned | ~2–5s with LLM |

### Invoke Any Free Skill (one curl)

```bash
curl -X POST https://sovereignomega.onrender.com/api/v1/skills/invoke/coherence_evaluate \
  -H "Content-Type: application/json" \
  -d '{"skill_id":"coherence_evaluate","input":{"query":"Should I execute this trade?","domain":"trading"}}'
```

**Response:**
```json
{
  "skill_id": "coherence_evaluate",
  "invocation_id": "a7f2c3d1-...",
  "success": true,
  "output": {
    "gate_open": false,
    "psi_score": 0.656770,
    "delta_threshold": 0.682900,
    "plane_breakdown": {
      "p": 0.978738,
      "i": 0.500000,
      "c": 0.500000,
      "s": 0.613901,
      "w": 0.700000
    },
    "message": "SILENCE",
    "cycle_id": "a7f2c3d1-...",
    "domain": "trading"
  }
}
```

### MCP JSON-RPC 2.0 (Claude Desktop / any MCP host)

```json
{
  "mcpServers": {
    "sovereign-omega": {
      "url": "https://sovereignomega.onrender.com/api/v1/mcp",
      "transport": "http"
    }
  }
}
```

```bash
# List all 6 MCP tools
curl -X POST https://sovereignomega.onrender.com/api/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Call a tool via MCP
curl -X POST https://sovereignomega.onrender.com/api/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"sovereign_moat_status","arguments":{}}}'
```

### Skill Discovery (Pharos Skill Engine Format)

```bash
# Auto-discover all skills — compatible with Pharos Agent Kit, Anvita Flow, any MCP host
curl https://sovereignomega.onrender.com/.well-known/skills.json   # 6-skill manifest
curl https://sovereignomega.onrender.com/.well-known/agent.json    # A2A agent card
curl https://sovereignomega.onrender.com/api/v1/agent/discover     # Live runtime state
```

**`SKILL.md` at repo root** — Pharos Skill Engine format, discoverable by coding agents (Claude Code, Cursor, Codex, Pharos Kit).

---

## Judging Criteria — How Each One Is Met

### 1. Originality and Creativity

**TRION Mathematics** — a novel 5-plane cognitive coherence framework invented for this project:

```
Ψ(t) = 0.25·P(t) + 0.30·I(t) + 0.20·C(t) + 0.15·S(t) + 0.10·W(t)
```

| Plane | Signal | Hard-stop condition |
|-------|--------|---------------------|
| **P** Perceptual | Shannon entropy via Rust ChaCha20 CSPRNG | — |
| **I** Inferential | 5-chain reasoning consistency | Contradiction → I = 0.0 |
| **C** Consensus | Slow independent convergence score | — |
| **S** Self-Reflection | FAISS memory density / query familiarity | — |
| **W** World Model | Environmental anomaly detection (z-score) | z > 3σ → W = 0.0 |

**The Silence Protocol** — agents that know *when not to act* are more valuable than agents that act on everything. When Ψ < Δ, the agent returns nothing. Silence rate ~87% in production (high discrimination).

**The Compounding Moat** — intelligence that compounds forever:
```
log(Λ(t)) = log(Λ₀) + Σᵢ log(1 + ηᵢ · ρᵢ)
```
Λ is log-additive (numerically stable), monotonically non-decreasing, synced to Pharos chain every 100 cycles. **Λ can never decrease.**

### 2. Technical Quality and Completeness

- 6 MCP Skills with full JSON input/output schemas
- FastAPI backend, async throughout, live on Render
- WebSocket + SSE real-time dashboard (WS-first, SSE fallback)
- FAISS 384-dim IndexFlatL2 vector memory — persists to disk on every write
- Rust entropy module (PyO3 + ChaCha20 CSPRNG) — not Python `random`
- 5 parallel reasoning chains per query — staggered for consensus scoring, 4s timeout guard
- TimescaleDB + pgvector — time-series intelligence storage
- 3 Solidity 0.8.24 contracts deployed on Pharos testnet
- x402 payment gate — HTTP 402 response with `accepts[]` array (PROS + USDC)
- A2A federation — coherence-gated peer mesh
- Background learner loop — FAISS index grows with every cycle regardless of gate result
- MCP JSON-RPC 2.0 endpoint, fully spec-compliant

**Live test right now:**
```bash
curl https://sovereignomega.onrender.com/api/v1/health
curl https://sovereignomega.onrender.com/api/v1/pharos/status   # chain_id: 688689
curl https://sovereignomega.onrender.com/api/v1/moat
curl https://sovereignomega.onrender.com/api/v1/silence/stats
```

### 3. Practical Use Case for AI Agents

Any agent — LangChain, AutoGPT, CrewAI, or raw HTTP — can call these skills to add coherence-gating before acting:

```python
import requests

# Before executing any consequential action
r = requests.post("https://sovereignomega.onrender.com/api/v1/skills/invoke/coherence_evaluate",
    json={"skill_id": "coherence_evaluate",
          "input": {"query": "Execute $50k DOGE buy", "domain": "trading"}})

d = r.json()
if d["output"]["gate_open"]:
    execute_trade()
else:
    print("SILENCE:", d["output"]["psi_score"], "< threshold", d["output"]["delta_threshold"])
```

```python
# Pre-flight silence check before any high-stakes action
r = requests.post(".../invoke/silence_check",
    json={"skill_id": "silence_check",
          "input": {"proposed_action": "Post on X about project alpha", "stakes": 0.7}})

if r.json()["output"]["should_act"]:
    post_to_social()
```

### 4. Reusability and Composability of Skills

Phase 1's primary criterion. Every skill is:

**Independently callable** — no shared state required between calls:
```bash
curl -X POST .../invoke/moat_status        -d '{"skill_id":"moat_status","input":{}}'
curl -X POST .../invoke/silence_check      -d '{"skill_id":"silence_check","input":{"proposed_action":"trade"}}'
curl -X POST .../invoke/coherence_evaluate -d '{"skill_id":"coherence_evaluate","input":{"query":"act?"}}'
```

**Schema-validated** — each skill has JSON input/output schemas:
```bash
curl https://sovereignomega.onrender.com/api/v1/skills/coherence_evaluate
# → {id, name, description, tier, input_schema, output_schema, endpoint}
```

**MCP-compatible** — drop into any MCP host with one config line

**Composable** — the SOVEREIGN-Ω agent demonstrates full composition:
```
silence_check → coherence_evaluate → [gate] → trade_evaluate/reasoning_chain → moat_status update
```

**SKILL.md at repo root** — Pharos Skill Engine format for coding-agent auto-discovery

**Python SDK** (`sdk/` directory):
```python
from sdk.sovereign_sdk import SovereignClient
client = SovereignClient("https://sovereignomega.onrender.com")
result = client.coherence_evaluate("Should I act?", domain="trading")
```

**LangChain integration** (`examples/langchain_orchestrator.py`):
```python
tools = create_sovereign_tools("https://sovereignomega.onrender.com")
# Returns LangChain-compatible Tool[] — plug into any AgentExecutor
```

### 5. Successful Deployment on Pharos

**3 Smart Contracts deployed on Pharos Atlantic Testnet (Chain ID 688689):**

| Contract | Address | Purpose |
|----------|---------|---------|
| `SovereignRegistry` | `0x6EAB7862385329BdaaD32f2b9587a66E768018Ba` | Agent identity, moat state, cycle counter |
| `SovereignVault` | `0xAbC106D943a6Aff91A0B29f4a77E4009323d7A66` | Trading capital + coherence gate per trade |
| `SovereignLearner` | `0x799006C9b1e946d3A2909b81F3C3087D71bB9F84` | Domain mastery + IQ milestones |

**Agent Wallet:** [`0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20`](https://testnet.pharosscan.xyz/address/0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20)

**Vault Funded — confirmed on-chain:**
- Tx: [`0xad8b9a7ee114...ab3363`](https://testnet.pharosscan.xyz/tx/0xad8b9a7ee114a853a8acd39432eec297ddba404185d553570008d8a1a8ab3363) · Block: `24417627` · Amount: **2.0 PROS** ✅

**Confirmed on-chain transactions:**
- [`e610233d...`](https://testnet.pharosscan.xyz/tx/e610233d729a35fde68a8cec26c03785f7711df8dc24f2f3e730e5b3137b40d8) → `SovereignRegistry.updateMoat()` @ Block 24358807 ✅
- [`53682ff0...`](https://testnet.pharosscan.xyz/tx/53682ff09d2e68b85f8c5304aa465d181a307b6b1d679781d0bfb8cffc96b0ed) → `SovereignLearner.updateDomainMastery(testing)` @ Block 24358812 ✅
- [`453f399a...`](https://testnet.pharosscan.xyz/tx/453f399ac3cfa0eb8c5bb9d42cc14bbdd0e2c1a728c0cd007ec7fe193488a87c) → `SovereignLearner.updateDomainMastery(trading)` @ Block 24358817 ✅

**x402 Machine-to-Machine Payments on Pharos:**
```bash
# Get payment config
curl https://sovereignomega.onrender.com/api/v1/x402/config
# → {chain_id: 688689, accepted_tokens: [PROS, USDC], skill_prices: {trade_evaluate: {PROS:"1.0",USDC:"0.10"}}}

# Verify payment and get nonce (testnet: any valid tx hash accepted)
curl -X POST https://sovereignomega.onrender.com/api/v1/x402/verify \
  -d '{"tx_hash":"0xabcdef...", "skill_id":"trade_evaluate", "token":"PROS"}'
# → {verified: true, nonce: "abc123", expires_at: 1750000000}

# Invoke premium skill
curl -X POST https://sovereignomega.onrender.com/api/v1/skills/invoke/trade_evaluate \
  -d '{"skill_id":"trade_evaluate","x402_payment_tx":"0xabcdef...","input":{"symbol":"BTC/USDT","direction":"LONG"}}'
```

USDC testnet: `0xE0BE08c77f415F577A1B3A9aD7a1Df1479564ec8` · Facilitator: `https://facilitator.pharos.xyz` · **20% discount for paying in $PROS**

### 6. User Experience and Clarity of Documentation

| Surface | URL |
|---------|-----|
| Live Homepage | https://sovereignomega.onrender.com/ |
| Real-time Dashboard (WebSocket + SSE) | https://sovereignomega.onrender.com/dashboard |
| Full Pipeline & On-Chain Trace | https://sovereignomega.onrender.com/pipeline |
| Swagger / OpenAPI | https://sovereignomega.onrender.com/docs |
| Agent Card (A2A) | https://sovereignomega.onrender.com/.well-known/agent.json |
| Skills Manifest | https://sovereignomega.onrender.com/.well-known/skills.json |

**Documentation files:**
- `README.md` — project overview, architecture, quick start
- `SKILL.md` — Pharos Skill Engine format (coding-agent discoverable)
- `SKILLS.md` — complete skill reference with full schemas and examples
- `HACKATHON.md` — this document
- `SECURITY.md` — CertiK Skill Scanner compliance
- `RENDER_DEPLOY.md` — deploy instructions
- `examples/` — LangChain orchestrator, Pharos skill composition, standalone usage

### 7. Alignment with Pharos AI Agent and On-Chain Economy Vision

The Pharos vision: *"on-chain payments, social interactions, and the deployment of intelligent agents at scale"*

| Pharos Vision | SOVEREIGN-Ω Implementation |
|---|---|
| **On-chain payments** | x402 HTTP 402 gate — premium skills require PROS/USDC on Pharos |
| **Intelligent agents at scale** | 6 composable skills — any agent can be made TRION-safe |
| **Reusable Skill modules** | MCP-compatible, schema-validated, independently callable |
| **Social interactions** | A2A federation with Ψ-gated peer acceptance |
| **On-chain identity** | SovereignRegistry stores agent state, moat, cycle count |
| **Compounding value** | Λ grows permanently with every coherent action, synced to chain |
| **Pharos MaaS alignment** | 20% PROS discount, native PROS payment, facilitator integration |

---

## Architecture

```
POST /api/v1/skills/invoke/{skill_id}
  │
  ├─ Free skill
  │     ChainManager.run_chains() [5 parallel LLM chains, 4s timeout guard]
  │     CoherenceEngine: Ψ = 0.25·P + 0.30·I + 0.20·C + 0.15·S + 0.10·W
  │     ActionGate.is_open(Ψ, Δ) → OPEN: ACT  |  CLOSED: SILENCE
  │     MoatAccumulator.accumulate() [log(Λ) grows, never shrinks]
  │     FAISS learn_from_cycle() [384-dim embedding stored]
  │     [every 100 cycles] SovereignRegistry.updateMoat() on-chain
  │     Response { gate_open, psi_score, delta_threshold, plane_breakdown }
  │
  └─ Premium skill
        No x402_payment_tx → HTTP 402 { accepts: [{PROS:"1.0"}, {USDC:"0.10"}] }
        Valid payment → executes full pipeline above
```

---

## Security (CertiK Skill Scanner Compliant)

- Private keys: env vars only, never hardcoded, never logged
- Action gate: no override path, no bypass, code-enforced
- x402 nonces: 5-minute expiry, sha256-derived, single-use
- Contradiction between reasoning chains → I(t) = 0.0 (adversarial injection blocked)
- Environmental anomaly z > 3σ → W(t) = 0.0 immediately
- 2% vault max per trade — oversized positions blocked
- 6% daily loss limit — automatic trading pause
- Rust ChaCha20 CSPRNG for entropy (not Python `random`)
- All txs signed locally — keys never leave environment

Full compliance doc: `SECURITY.md`

---

## Run Locally

```bash
git clone https://github.com/dev-analyshd/sovereign-omega
pip install -r requirements.txt
cp .env.example .env
# Set PHAROS_REGISTRY, PHAROS_VAULT, PHAROS_LEARNER, ANTHROPIC_API_KEY or NVIDIA_API_KEY
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Verify
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/.well-known/skills.json
curl -X POST http://localhost:8000/api/v1/skills/invoke/coherence_evaluate \
  -d '{"skill_id":"coherence_evaluate","input":{"query":"test"}}'
```

---

## Complete API Reference

### Skills
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/skills` | Full manifest (all 6 skills) | None |
| GET | `/api/v1/skills/{id}` | Single skill + schema | None |
| POST | `/api/v1/skills/invoke/{id}` | Invoke skill | x402 for premium |
| POST | `/api/v1/mcp` | MCP JSON-RPC 2.0 | None |
| GET | `/.well-known/skills.json` | Discovery manifest | None |
| GET | `/.well-known/agent.json` | A2A agent card | None |

### x402 Payments
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/x402/config` | Prices, tokens, agent address |
| POST | `/api/v1/x402/verify` | Verify tx hash → return nonce |
| GET | `/api/v1/x402/status` | Active payment windows |

### Intelligence & Moat
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Agent status + moat |
| GET | `/api/v1/intelligence` | IQ score + domain breakdown |
| GET | `/api/v1/moat` | Λ + projections (1d/7d/30d/90d/365d) |
| GET | `/api/v1/silence/stats` | Silence rate + interpretation |

### On-Chain
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/pharos/status` | Chain connection, address, chain ID |
| POST | `/api/v1/pharos/sync` | Push Λ + IQ to SovereignRegistry |

### Live Streams
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/stream/intelligence` | Ψ + Λ + IQ every 3s |
| GET | `/api/v1/stream/heartbeat` | 1Hz on-chain pulse |
| GET | `/api/v1/stream/actions` | Gate decisions as they happen |
| WS | `/ws/dashboard` | WebSocket dashboard feed (1 frame/sec) |

---

*SOVEREIGN-Ω · Phase 1 · Pharos Skill-to-Agent Dual Cascade Hackathon · June 2026*
*Prize pool: 50,000 $PROS · Phase 1 winners: 40 · Phase 1 prize: 20,000 $PROS*
*Judging: June 18–22, 2026*
