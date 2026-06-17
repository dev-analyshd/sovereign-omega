# sovereign-omega-sdk

> Pharos-native SOVEREIGN-Ω skills as LangChain tools.  
> Plug TRION coherence scoring, Bayesian-Kelly trading, and x402-gated reasoning into any `pharos-agent-kit` agent in two lines.

---

## What is SOVEREIGN-Ω?

SOVEREIGN-Ω is an autonomous intelligence agent built natively on Pharos chain and governed by TRION mathematics:

```
Ω(a,t) = [Ψ(t) ≥ Δ(t)] · R(a,t) · e^(Λ·t)
```

- **Ψ(t)** — cognitive coherence across 5 planes (Perceptual · Inferential · Consensus · Self-Reflection · World Model)
- **Δ(t)** — dynamic threshold that rises in volatile/novel conditions
- **Λ(t)** — compounding intelligence moat, monotonically non-decreasing
- **Gate** — binary: if Ψ < Δ, the agent stays silent. Truth or silence — the silence is information.

---

## Installation

```bash
npm install sovereign-omega-sdk
# or
pnpm add sovereign-omega-sdk
```

---

## Quick Start — pharos-agent-kit integration

```typescript
import { PharosAgentKit, createPharosTools } from "pharos-agent-kit";
import { SovereignOmegaKit, createSovereignTools } from "sovereign-omega-sdk";

// Initialize pharos-agent-kit as normal
const pharos = new PharosAgentKit(
  process.env.WALLET_PRIVATE_KEY!,
  "https://rpc-testnet.pharos.xyz",
  { OPENAI_API_KEY: process.env.OPENAI_API_KEY! }
);

// Initialize SOVEREIGN-Ω
const sovereign = new SovereignOmegaKit({
  baseUrl: "https://your-sovereign-agent.replit.dev",
  // Optional: add x402 config for premium skills
  x402: {
    walletAddress: "0xYourWalletAddress",
    token: "PROS",  // 20% discount vs USDC
    signPayment: async (req) => {
      // Sign the x402 payment request with your private key
      // Returns a base64-encoded signed authorization header
      return await signWithViem(req);
    },
  },
});

// Merge tools — SOVEREIGN-Ω skills are now first-class LangChain tools
const tools = [
  ...createPharosTools(pharos),
  ...createSovereignTools(sovereign.client),
];

// Use with your LLM of choice
const agent = await createReactAgent({ llm, tools });
```

---

## Available Skills (Tools)

### Free Skills (no payment required)

| Tool Name | Description |
|-----------|-------------|
| `sovereign_coherence_evaluate` | Run TRION Ψ across all 5 planes. Returns gate decision (ACT/SILENCE) |
| `sovereign_moat_status` | Current Λ, IQ score, cycle count, domain mastery, 30-day projections |
| `sovereign_silence_check` | Would this action be silenced? Returns failing planes and reason |
| `sovereign_intelligence_score` | Full IQ report with human-readable interpretation |

### Premium Skills (x402 — $PROS or USDC on Pharos chain)

| Tool Name | Price (PROS) | Price (USDC) | Description |
|-----------|--------------|--------------|-------------|
| `sovereign_trade_evaluate` | 0.8 PROS *(20% off)* | 0.10 USDC | Bayesian-Kelly trade signal: EXECUTE/WAIT/SILENCE + Kelly fraction |
| `sovereign_reasoning_chain` | 1.6 PROS *(20% off)* | 0.20 USDC | 5-chain parallel reasoner with contradiction detection |

> **$PROS discount:** Paying in native $PROS gets you 20% off, aligned with the Pharos MaaS launch incentive.

---

## Direct API (without LangChain)

```typescript
const sovereign = new SovereignOmegaKit({ baseUrl: "https://your-agent.replit.dev" });

// Check coherence before any high-stakes action
const coherence = await sovereign.evaluateCoherence(
  "Execute 10% portfolio swap into PROS on Pharos DEX",
  "trading"
);

if (!coherence.gate_open) {
  console.log(`SILENCE: Ψ=${coherence.psi_score} < Δ=${coherence.delta_threshold}`);
  console.log("Failing planes:", coherence.plane_breakdown);
  return; // Do not act
}

// Check if action would be silenced (quick boolean check)
const silenced = await sovereign.wouldBeSilenced("post bullish tweet", "social");

// Get intelligence level
const moat = await sovereign.getMoatStatus();
console.log(`Λ=${moat.lambda} | IQ=${moat.iq_score} (${moat.iq_interpretation})`);

// Premium: trade evaluation (requires x402 config)
const trade = await sovereign.evaluateTrade({
  symbol: "BTC/USDT",
  direction: "LONG",
  strategy: "momentum",
  volatility: 0.04,
});
console.log(`Decision: ${trade.decision} | Kelly: ${trade.kelly_fraction}`);
```

---

## MCP (Model Context Protocol) Integration

Use with Claude Desktop, Continue.dev, or any MCP-compatible host:

```typescript
import { getSovereignMcpTools, executeMcpTool, SovereignClient } from "sovereign-omega-sdk";

const client = new SovereignClient({ baseUrl: "https://your-agent.replit.dev" });

// Get MCP tool definitions
const tools = getSovereignMcpTools();

// Execute a tool call from your MCP host
const result = await executeMcpTool(client, "sovereign_coherence_evaluate", {
  query: "Is this a good time to execute a DeFi trade?",
  domain: "trading",
});

console.log(result.content[0].text);
```

Or point your MCP host directly at the server endpoint:

```json
{
  "mcpServers": {
    "sovereign-omega": {
      "url": "https://your-agent.replit.dev/api/v1/mcp",
      "transport": "http"
    }
  }
}
```

---

## The Five Cognitive Planes

Every skill invocation runs TRION mathematics across all five planes simultaneously:

```
Ψ(t) = 0.25·P(t) + 0.30·I(t) + 0.20·C(t) + 0.15·S(t) + 0.10·W(t)
```

| Plane | Weight | What it measures |
|-------|--------|-----------------|
| **P** — Perceptual | 25% | Shannon entropy of input signals. Low entropy → 0.0 hard floor |
| **I** — Inferential | 30% | Internal reasoning consistency. Contradiction → 0.0 hard stop |
| **C** — Consensus | 20% | Slow independent chain convergence (fast agreement = low score) |
| **S** — Self-Reflection | 15% | Memory density — how familiar is this query? `tanh(D/D_ref)` |
| **W** — World Model | 10% | Environment normality. z-score > 3σ on any signal → 0.0 |

---

## x402 Payment Flow

Premium skills use HTTP 402 / x402 — machine-to-machine payments built into Pharos:

```
Agent A calls trade_evaluate
  → 402 Payment Required (nonce, amount, payTo)
  → Agent A signs payment with its wallet
  → Retry with X-Payment header
  → SOVEREIGN-Ω verifies and executes skill
  → Response returned
```

The SDK handles this automatically when `x402` config is provided — you never see the 402.

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/skills` | GET | List all skills with schemas |
| `/api/v1/skills/invoke/{skill_id}` | POST | Invoke a skill |
| `/api/v1/mcp` | POST | MCP JSON-RPC 2.0 endpoint |
| `/api/v1/mcp/manifest` | GET | MCP server manifest |
| `/api/v1/x402/config` | GET | Payment configuration |
| `/.well-known/agent.json` | GET | A2A agent discovery card |
| `/.well-known/skills.json` | GET | MCP skills manifest |

---

## Links

- **Agent**: https://your-agent.replit.dev  
- **Agent Card**: https://your-agent.replit.dev/.well-known/agent.json  
- **MCP Server**: https://your-agent.replit.dev/api/v1/mcp  
- **x402 Config**: https://your-agent.replit.dev/api/v1/x402/config  
- **Chain**: Pharos Testnet (chain ID 688688) / Mainnet (1672)

---

## License

MIT
