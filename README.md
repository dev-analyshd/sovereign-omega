# SOVEREIGN-Ω · 6 MCP Skills for Verifiable Agent Cognition

> *Truth or silence. The silence is information.*

**Phase 1 Submission — Pharos "Skill-to-Agent Dual Cascade Hackathon"**

SOVEREIGN-Ω provides **6 reusable MCP Skills** that any AI agent can call to add mathematically-verified cognition to its decision-making — coherence scoring, silence gating, trade sizing, parallel reasoning, and more. All skills are independently callable over HTTP or MCP JSON-RPC 2.0, x402-monetized on Pharos, and backed by on-chain contracts.

**The included Agent is the reference implementation** showing how all 6 skills compose into a self-governing autonomous entity with a compounding intelligence moat (Λ).

```bash
# Any agent can call a free skill — no SDK, no runtime
curl -X POST https://<agent-host>/api/v1/skills/invoke/coherence_evaluate \
  -H "Content-Type: application/json" \
  -d '{"skill_id":"coherence_evaluate","input":{"query":"Should I act now?","domain":"trading"}}'
# → {"gate_open": true, "psi_score": 0.762, "plane_breakdown": {...}}
```

| Skill | Tier | Purpose |
|---|---|---|
| `coherence_evaluate` | 🆓 Free | TRION Ψ-score across 5 cognitive planes |
| `silence_check` | 🆓 Free | Should this action be silenced? |
| `moat_status` | 🆓 Free | Live Λ reputation score + projection |
| `intelligence_score` | 🆓 Free | IQ breakdown with domain mastery |
| `trade_evaluate` | 💰 1 PROS | Bayesian Kelly trade sizing + risk gate |
| `reasoning_chain` | 💰 2 PROS | 5 parallel reasoning chains, best returned |

→ **Full skill specs:** [`SKILLS.md`](./SKILLS.md) · **Examples:** [`examples/`](./examples/) · **Schemas:** [`skills/`](./skills/)

---

## Under the Hood: TRION Mathematics

An autonomous intelligence system governed by TRION mathematics. It acts only when coherent, learns from every cycle, and accumulates a permanent compounding moat on Pharos chain.

---

## Core Equation

```
Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)
```

| Symbol | Meaning |
|--------|---------|
| Ψ(t) | Coherence score across 5 cognitive planes |
| Δ(t) | Dynamic action threshold |
| R(a,t) | Reward/relevance of action `a` |
| Λ(t) | Moat coefficient — **never decreases** |

## Five Cognitive Planes

```
Ψ(t) = 0.25·P(t) + 0.30·I(t) + 0.20·C(t) + 0.15·S(t) + 0.10·W(t)
```

| Plane | Weight | Description | Hard-zero condition |
|-------|--------|-------------|---------------------|
| **P** | 0.25 | Perceptual: signal entropy (Shannon H / H_max) | — |
| **I** | 0.30 | Inferential: reasoning chain consistency | Contradiction between chains → 0.0 |
| **C** | 0.20 | Consensus: slow independent convergence scoring | — |
| **S** | 0.15 | Self-Reflection: query familiarity via memory density | — |
| **W** | 0.10 | World Model: environmental anomaly detection | z-score > 3σ → 0.0 |

## Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI + uvicorn |
| Contracts | Solidity 0.8.24, Hardhat |
| Chain | Pharos (testnet: 688689 / mainnet: 1672) |
| Memory | FAISS (L2 index, persisted every write) |
| Trading | ccxt + pandas-ta + Bayesian Kelly sizing |
| Reasoning | 5 parallel chains via Anthropic Claude |
| Entropy | Rust (PyO3 + ChaCha20 CSPRNG) |
| Real-time | WebSocket dashboard + 4 SSE streams |

## Quick Start

```bash
# 1. Copy env template
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY for full LLM reasoning

# 2. Bootstrap (Python + Hardhat + optional Rust)
bash scripts/bootstrap.sh

# 3. Deploy contracts to Pharos testnet
bash scripts/deploy_pharos.sh pharos_testnet
# Copy addresses from output into .env

# 4. Verify deployment
python scripts/verify_deployment.py

# 5. Start the agent
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Live Interfaces

| URL | Description |
|-----|-------------|
| `/` | System overview — live Λ, IQ, domain mastery |
| `/dashboard` | **Real-time WebSocket dashboard** — Ψ chart, Λ curve, plane bars, federation peer map, gate feed |
| `/docs` | Swagger / OpenAPI interactive docs |
| `/.well-known/agent.json` | A2A agent discovery card |

## API Endpoints

### Core Agent

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Agent status + Λ + IQ |
| POST | `/api/v1/action` | Evaluate an action (Ψ-gated) |
| POST | `/api/v1/trade/evaluate` | Evaluate a trade (Bayesian Kelly) |
| GET | `/api/v1/intelligence` | IQ score + breakdown |
| GET | `/api/v1/intelligence/domains` | Domain mastery map |
| GET | `/api/v1/moat` | Λ state + projections |
| GET | `/api/v1/silence/stats` | Silence rate + episode log |
| GET | `/api/v1/pharos/status` | On-chain connection + balances |
| POST | `/api/v1/pharos/sync` | Push Λ + IQ state to Pharos |

### MCP Skills (6 total — 4 free, 2 paid via x402)

| Method | Path | Tier | Description |
|--------|------|------|-------------|
| GET | `/api/v1/skills` | — | Skill manifest |
| POST | `/api/v1/skills/invoke/coherence_evaluate` | FREE | Full 5-plane TRION Ψ score |
| POST | `/api/v1/skills/invoke/moat_status` | FREE | Λ + projections |
| POST | `/api/v1/skills/invoke/silence_check` | FREE | Gate open/silent for a context |
| POST | `/api/v1/skills/invoke/intelligence_score` | FREE | IQ(t) score |
| POST | `/api/v1/skills/invoke/trade_evaluate` | 1.0 PROS / 0.10 USDC | Bayesian trade evaluation |
| POST | `/api/v1/skills/invoke/reasoning_chain` | 2.0 PROS / 0.20 USDC | 5 parallel LLM reasoning chains |
| POST | `/api/v1/mcp` | — | MCP JSON-RPC 2.0 endpoint |
| GET | `/api/v1/x402/config` | — | x402 M2M payment config |

### Federation (A2A)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/federation/announce` | Peer announces itself (Ψ-gated) |
| POST | `/api/v1/federation/invite` | SOVEREIGN-Ω invites a peer |
| POST | `/api/v1/federation/handshake` | Mutual coherence exchange |
| GET | `/api/v1/federation/peers` | Peer registry |
| GET | `/api/v1/federation/network` | Full graph with Ψ scores |
| GET | `/api/v1/federation/broadcast` | SSE: live intelligence feed |

### Live Streaming

| Method | Path | Description |
|--------|------|-------------|
| WS | `/ws/dashboard` | WebSocket: full state frame every 1 second |
| GET | `/api/v1/stream/intelligence` | SSE: Ψ + Λ + IQ every 3 seconds |
| GET | `/api/v1/stream/heartbeat` | SSE: 1 Hz on-chain heartbeat |
| GET | `/api/v1/stream/moat` | SSE: Λ growth on every accumulation |
| GET | `/api/v1/stream/actions` | SSE: live gate decisions (ACT / SILENCE) |

## WebSocket Dashboard

Open `/dashboard` in a browser to see the full real-time visual:

- **Gate status** — animated SILENCE / OPEN badge with Ψ vs Δ live
- **Ψ rolling chart** — 60-second coherence window (Chart.js)
- **log(Λ) growth curve** — moat accumulation over time (Chart.js)
- **5-plane bar chart** — live P · I · C · S · W breakdown
- **Metrics strip** — cycles, Λ, IQ, chain syncs, next sync countdown
- **Federation peer map** — SVG force graph of A2A peer network
- **Gate decision feed** — scrolling log of every SILENCE / OPEN decision

WebSocket reconnects automatically on disconnect.

## On-Chain Heartbeat

Every 100 coherent cycles, SOVEREIGN-Ω automatically pushes its state to Pharos:

- `SovereignRegistry` — agent identity + current Λ
- `SovereignVault` — trading capital + coherence gate
- `SovereignLearner` — domain mastery + IQ milestones

Every individual action also emits a per-action heartbeat to chain.

## Contracts (Pharos)

| Contract | Address (testnet) | Purpose |
|----------|-------------------|---------|
| SovereignRegistry | `0x6EAB7862385329BdaaD32f2b9587a66E768018Ba` | Agent identity + moat state |
| SovereignVault | `0xAbC106D943a6Aff91A0B29f4a77E4009323d7A66` | Trading capital + on-chain gate |
| SovereignLearner | `0x799006C9b1e946d3A2909b81F3C3087D71bB9F84` | Domain mastery ledger + IQ milestones |

## The Rules (Never Broken)

1. FAISS persists to disk on every write
2. Λ(moat) never decreases — ever
3. Action gate has no override. No bypass. No exception.
4. SILENCE is logged before any other action in that cycle
5. Social posts require Ψ ≥ 0.70
6. Private keys loaded from environment only — never hardcoded
7. Max 2% of vault per trade position
8. 6% daily loss = trading paused until next day
9. Contradiction between reasoning chains → I(t) = 0.0 (hard stop)
10. World model z-score > 3.0 → W(t) = 0.0 immediately

## Pharos Networks

- **Testnet**: Chain ID 688689 | RPC: https://testnet.pharosnetwork.xyz | Explorer: https://testnet.pharosscan.xyz
- **Mainnet**: Chain ID 1672 | RPC: https://rpc.pharos.xyz | Explorer: https://pharosscan.xyz

## Note on LLM Reasoning

The `ANTHROPIC_API_KEY` must be a valid key from [console.anthropic.com](https://console.anthropic.com) for the P (Perceptual) and C (Consensus) planes to score fully. Without it:
- P = 0.0 (no signal entropy from LLM output)
- C is reduced (no reasoning chain convergence)
- Ψ stays low → gate stays SILENT (by design — the Silence Protocol refuses to act without full cognitive coherence)

This is correct behaviour. Set the key in Replit Secrets → `ANTHROPIC_API_KEY`.
