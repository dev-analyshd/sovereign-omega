# SOVEREIGN-Ω

> *Truth or silence. The silence is information.*

An autonomous intelligence system governed by TRION mathematics. It acts only when coherent, learns from every cycle, and accumulates a permanent compounding moat.

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

- **P** — Perceptual: signal entropy (Shannon H / H_max)
- **I** — Inferential: reasoning chain consistency (contradiction = hard zero)
- **C** — Consensus: slow independent convergence scoring
- **S** — Self-Reflection: query familiarity via memory density
- **W** — World Model: environmental anomaly detection (z > 3σ = zero)

## Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI + uvicorn |
| Contracts | Solidity 0.8.24, Hardhat |
| Chain | Pharos (testnet: 688688 / mainnet: 1672) |
| Memory | FAISS (L2 index, persisted every write) |
| Trading | ccxt + pandas-ta + Bayesian Kelly sizing |
| Reasoning | 5 parallel chains via Anthropic Claude |
| Entropy | Rust (PyO3 + ChaCha20 CSPRNG) |
| Social | Twitter (tweepy) + Discord.py + python-telegram-bot |

## Quick Start

```bash
# 1. Copy env template
cp .env.example .env
# Edit .env — see comments inside

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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Agent status + moat |
| POST | /api/v1/action | Evaluate an action (gated) |
| POST | /api/v1/trade/evaluate | Evaluate a trade |
| GET | /api/v1/intelligence | IQ score + breakdown |
| GET | /api/v1/intelligence/domains | Domain mastery map |
| GET | /api/v1/moat | Moat state + projections |
| GET | /api/v1/silence/log | Silence episode log |
| GET | /api/v1/pharos/status | On-chain connection |
| POST | /api/v1/pharos/sync | Push state to Pharos |

## Contracts (Pharos)

| Contract | Purpose |
|----------|---------|
| SovereignRegistry | Agent identity + moat state on-chain |
| SovereignVault | Trading capital + on-chain coherence gate |
| SovereignLearner | Domain mastery ledger + IQ milestones |

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

- **Testnet**: Chain ID 688688 | RPC: https://testnet.pharosnetwork.xyz | Explorer: https://testnet.pharosscan.xyz
- **Mainnet**: Chain ID 1672 | RPC: https://rpc.pharos.xyz | Explorer: https://pharosscan.xyz
