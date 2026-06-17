# SOVEREIGN-Ω — Pharos Phase 1 Hackathon Submission
## "Skill-to-Agent Dual Cascade" · DoraHacks · [dorahacks.io/hackathon/pharos-phase1](https://dorahacks.io/hackathon/pharos-phase1)

> *Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)*
> *Truth or silence. The silence is information.*

---

## 🏆 What We Built

**SOVEREIGN-Ω** is a production-grade autonomous intelligence agent built natively on Pharos chain. It solves the core problem the hackathon names: *"Most agents today possess neither reusable Skill assets nor durable social graphs and payment behaviors."*

We built exactly that — **6 reusable MCP Skills**, **x402 machine-to-machine payments**, **on-chain Pharos contracts**, and a **compounding moat** (Λ) that grows with every coherent action and never decreases.

---

## 🎯 Judging Criteria — How We Score

### 1. Innovation ✅
**TRION Mathematics** — a novel 5-plane cognitive coherence framework that no agent framework uses:

```
Ψ(t) = 0.25·P(t) + 0.30·I(t) + 0.20·C(t) + 0.15·S(t) + 0.10·W(t)
```

| Plane | Signal |
|-------|--------|
| **P** Perceptual | Shannon entropy of input channels (Rust CSPRNG) |
| **I** Inferential | Multi-chain reasoning consistency (contradiction → I=0.0) |
| **C** Consensus | Slow independent convergence score |
| **S** Self-Reflection | Memory density / familiarity weighting |
| **W** World Model | Environmental anomaly detection (z > 3σ → W=0.0) |

**The Compounding Moat** — intelligence that compounds forever:
```
log(Λ(t)) = log(Λ₀) + Σᵢ log(1 + ηᵢ · ρᵢ)    Λ never decreases. Ever.
```

**The Silence Protocol** — agents that know when NOT to act are more valuable than agents that always act.

### 2. Technical Completeness ✅
Production-ready, not a demo:
- ✅ FastAPI backend running on Pharos testnet
- ✅ 6 MCP-compatible Agent Skills with full JSON schemas
- ✅ **`SKILL.md` at repo root** — Pharos Skill Engine format, coding-agent-discoverable
- ✅ x402 HTTP 402 payment gate ($PROS + USDC · facilitator: https://facilitator.pharos.xyz)
- ✅ Pharos Atlantic testnet USDC: `0xE0BE08c77f415F577A1B3A9aD7a1Df1479564ec8`
- ✅ A2A agent discovery (`/.well-known/agent.json` + `/.well-known/skills.json`)
- ✅ 3 Solidity smart contracts deployed on Pharos (Registry, Vault, Learner)
- ✅ FAISS vector memory (persists to disk on every write)
- ✅ Bayesian Kelly criterion trading engine
- ✅ Parallel reasoning chains (5 independent chains per query)
- ✅ Background self-improvement loop + daily risk reset

### 3. Security ✅ (CertiK Skill Scanner Compliant)
- ✅ **Private keys** loaded from environment variables only — never hardcoded (Rule 6)
- ✅ **Action Gate** has no override, no bypass, no exception — code-enforced
- ✅ **x402 payment nonces** expire in 5 minutes — no replay attacks
- ✅ **Silence Protocol** enforced before any social/trading action
- ✅ **World Model anomaly detection** — z > 3σ immediately kills W(t) = 0.0
- ✅ **Inferential contradiction** → I(t) = 0.0 hard stop (prevents adversarial injection)
- ✅ **2% vault max per trade** — risk manager blocks oversized positions
- ✅ **6% daily loss limit** — automatic pause until next day
- ✅ Rust CSPRNG for entropy (not Python `random`) — `sovereign_entropy` module
- ✅ All transactions signed locally; keys never leave the environment

See `SECURITY.md` for full CertiK Skill Scanner compliance documentation.

### 4. Deployment On-Chain ✅
- ✅ 3 Pharos smart contracts: `SovereignRegistry`, `SovereignVault`, `SovereignLearner`
- ✅ Moat state (Λ, cycles, IQ) synced to chain via `POST /api/v1/pharos/sync`
- ✅ Trade entries logged on-chain via `SovereignVault`
- ✅ Domain mastery milestones written via `SovereignLearner`
- ✅ x402 payment verification against Pharos chain RPC
- ✅ Skills registered with on-chain addresses in manifest

---

## 🔌 Skill-to-Agent Architecture

### The 6 Skills

| Skill ID | Tier | Description | x402 Price |
|----------|------|-------------|------------|
| `coherence_evaluate` | Free | TRION Ψ score across 5 planes | — |
| `moat_status` | Free | Current Λ, IQ, cycle count + projection | — |
| `intelligence_score` | Free | Full IQ breakdown with domain mastery | — |
| `silence_check` | Free | Should this action be silenced? | — |
| `trade_evaluate` | **Premium** | Autonomous trading: Kelly + Bayesian edge | 1.0 PROS / 0.10 USDC |
| `reasoning_chain` | **Premium** | 5 parallel reasoning chains, best returned | 2.0 PROS / 0.20 USDC |

### Invoke a Free Skill (no payment)
```bash
curl -X POST https://your-agent.replit.app/api/v1/skills/invoke/coherence_evaluate \
  -H "Content-Type: application/json" \
  -d '{"skill_id": "coherence_evaluate", "input": {"query": "Should I execute this trade?", "domain": "trading"}}'
```

### Invoke a Premium Skill (x402 flow)
```bash
# Step 1: Get payment config
curl https://your-agent.replit.app/api/v1/x402/config

# Step 2: Send $PROS payment on Pharos chain
# (use pharos-agent-kit or ethers.js)

# Step 3: Verify payment and get nonce
curl -X POST https://your-agent.replit.app/api/v1/x402/verify \
  -d '{"tx_hash": "0x...", "skill_id": "trade_evaluate", "token": "PROS"}'

# Step 4: Invoke skill with payment proof
curl -X POST https://your-agent.replit.app/api/v1/skills/invoke/trade_evaluate \
  -d '{"skill_id": "trade_evaluate", "x402_payment_tx": "0x...", "input": {"symbol": "BTC/USDT", "direction": "LONG"}}'
```

### Agent Discovery (A2A / Anvita Flow)
```bash
# Agent card
curl https://your-agent.replit.app/.well-known/agent.json

# Skills manifest
curl https://your-agent.replit.app/.well-known/skills.json

# Runtime discover with live Λ + IQ
curl https://your-agent.replit.app/api/v1/agent/discover
```

---

## 📡 Complete API Reference

### Core Agent Skills
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/skills` | Full skill manifest | None |
| GET | `/api/v1/skills/{id}` | Get single skill definition | None |
| POST | `/api/v1/skills/invoke/{id}` | Invoke a skill | x402 for premium |

### x402 Payments
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/x402/config` | Payment config ($PROS + USDC prices) |
| POST | `/api/v1/x402/verify` | Verify tx + get nonce |
| GET | `/api/v1/x402/status` | Active payment windows |

### Agent Discovery
| Method | Path | Description |
|--------|------|-------------|
| GET | `/.well-known/agent.json` | A2A agent card |
| GET | `/.well-known/skills.json` | MCP skills manifest |
| GET | `/api/v1/agent/discover` | Live agent state + runtime |
| GET | `/api/v1/agent/peers` | Peer agents (A2A) |

### Intelligence & Moat
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Agent status + moat |
| GET | `/api/v1/intelligence` | IQ score breakdown |
| GET | `/api/v1/moat` | Λ state + 1d/7d/30d/90d/365d projections |
| GET | `/api/v1/silence/stats` | Silence rate + interpretation |

### Core Actions
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/action` | Coherence-gated action evaluation |
| POST | `/api/v1/trade/evaluate` | Autonomous trading decision |
| GET | `/api/v1/pharos/status` | On-chain connection state |
| POST | `/api/v1/pharos/sync` | Push Λ + IQ to chain |

---

## 🔗 Pharos Chain Integration

### Smart Contracts
| Contract | Purpose | Chain |
|----------|---------|-------|
| `SovereignRegistry` | Agent identity, moat state, cycle counter | Pharos testnet/mainnet |
| `SovereignVault` | Trading capital, on-chain coherence gate per trade | Pharos testnet/mainnet |
| `SovereignLearner` | Domain mastery ledger, IQ milestones | Pharos testnet/mainnet |

### Chain IDs
- **Testnet (Atlantic Ocean)**: `688689` — RPC: `https://testnet.pharosnetwork.xyz`
- **Mainnet (Pacific Ocean)**: `1672` — RPC: `https://rpc.pharos.xyz`

### x402 Payment Token Addresses
- **$PROS**: Native token on Pharos
- **USDC**: Circle CCTP deployed on Pharos mainnet
- **20% discount** when paying in $PROS (aligned with Pharos MaaS launch incentive)

---

## 🦀 Rust Entropy Module

High-performance cryptographic primitives compiled via `maturin` + PyO3:

```rust
// ChaCha20 CSPRNG — NOT Python's random
fn collect_entropy(seed: Option<u64>) -> Vec<f64>       // 256-sample entropy vector
fn shannon_entropy(values: Vec<f64>) -> f64              // H normalized to [0,1]
fn entropy_fingerprint(data: &str, key: &str) -> String  // HMAC-SHA256 fingerprint
fn generate_noise_vector(seed: u64, dim: usize, scale: f64) -> Vec<f64>
fn sample_indices(n: usize, k: usize, seed: u64) -> Vec<usize>  // Fisher-Yates
fn sha256_hex(data: &str) -> String
```

Shannon entropy feeds the **Perceptual plane** P(t), making SOVEREIGN-Ω's coherence score cryptographically grounded — not guessable, not manipulable.

---

## 💡 Why SOVEREIGN-Ω Wins

| Criterion | Most Agents | SOVEREIGN-Ω |
|-----------|-------------|-------------|
| Reusable Skills | Demo-only, no schema | 6 MCP skills with full JSON schema |
| On-chain presence | Wallet, nothing more | 3 contracts: registry + vault + learner |
| Payment model | Manual, human-mediated | x402 HTTP 402, machine-to-machine |
| Agent discovery | None | `/.well-known/agent.json` + A2A peers |
| Security | No formal model | Silence Protocol + CertiK-ready |
| Intelligence growth | Static | Compounding Λ, never decreases |
| Silence | Acts on everything | Acts only when Ψ ≥ Δ |

---

## 🚀 Run It

```bash
# Clone and start
git clone <repo>
pip install -r requirements.txt

# Build Rust entropy module
cd entropy && maturin build --release && pip install target/wheels/*.whl && cd ..

# Set environment
cp .env.example .env
# Fill in PHAROS_REGISTRY, PHAROS_VAULT, PHAROS_LEARNER (from deploy_pharos.sh)

# Start
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Verify
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/.well-known/agent.json
curl http://localhost:8000/api/v1/skills
```

---

## 📊 Live Demo

- **Health**: `GET /api/v1/health`
- **Agent Card**: `GET /.well-known/agent.json`
- **All Skills**: `GET /api/v1/skills`
- **Invoke Skill**: `POST /api/v1/skills/invoke/coherence_evaluate`
- **x402 Config**: `GET /api/v1/x402/config`
- **Swagger UI**: `/docs`

---

---

## 🧩 SKILL.md — Pharos Skill Engine Format

SOVEREIGN-Ω ships a `SKILL.md` at the root of this repository. This is the standard Pharos Skill Engine format (introduced by Anthropic, adopted across Claude Code, Cursor, Codex, and Pharos skills directories). It allows any AI coding agent to discover and invoke our skills without manual setup.

The `SKILL.md` covers:
- All 6 skill IDs and tiers
- Free and x402 premium invocation curl examples
- MCP JSON-RPC config block
- Chain details (chain ID 688689, USDC testnet address, facilitator URL)
- TRION framework summary
- Security properties

This satisfies the "Skills First" requirement of the hackathon — our skills are **reusable, documented, and coding-agent-discoverable** per the Pharos Skill Engine spec.

---

*Built for Pharos Phase 1 — "Skill-to-Agent Dual Cascade Hackathon" · June 2026*
*Deadline: June 18, 2026 @ 15:59 UTC · Total Prize Pool: 150,000 $PROS*
