# SOVEREIGN-Ω

Autonomous on-chain AI agent built natively on Pharos chain. Governed by TRION mathematics — acts only when cognitively coherent across 5 planes (Ψ ≥ Δ), or stays silent.

## How to Run

```bash
pip install -r requirements.txt
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 5000
```

## Live Interfaces

| URL | What it is |
|-----|------------|
| `/` | System overview — live Λ, IQ, plane scores |
| `/dashboard` | Real-time WebSocket dashboard — Ψ chart, Λ curve, federation peer map |
| `/docs` | Swagger / OpenAPI interactive docs |
| `/.well-known/agent.json` | A2A agent discovery card |
| `/api/v1/mcp` | MCP JSON-RPC 2.0 endpoint (6 tools) |

## Environment Variables

Set in Replit Secrets:
- `DEPLOYER_PRIVATE_KEY` — Pharos testnet wallet private key (required for on-chain mode)
- `ANTHROPIC_API_KEY` — Claude API key (required for real LLM reasoning chains; without it agent uses mock mode)

Set as shared env vars (already configured):
- `PHAROS_NETWORK=testnet`
- `PHAROS_REGISTRY=0x6EAB7862385329BdaaD32f2b9587a66E768018Ba`
- `PHAROS_VAULT=0xAbC106D943a6Aff91A0B29f4a77E4009323d7A66`
- `PHAROS_LEARNER=0x799006C9b1e946d3A2909b81F3C3087D71bB9F84`
- `TRADING_ENABLED=true`

## Architecture

```
Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)
Ψ(t) = 0.25·P + 0.30·I + 0.20·C + 0.15·S + 0.10·W
```

- **5 cognitive planes**: Perceptual · Inferential · Consensus · Self-Reflection · World Model
- **Silence Protocol**: if Ψ < Δ, the agent emits nothing — silence is information
- **Compounding moat Λ**: grows every coherent cycle, never decreases
- **3 Pharos contracts**: SovereignRegistry, SovereignVault, SovereignLearner
- **6 MCP Skills**: 4 free, 2 premium (x402 $PROS / USDC)

## User Preferences

- Keep private keys only as Replit Secrets — never in `.replit` or committed files
- Trading threshold is 25% higher than general gate (Rule 12) — by design
