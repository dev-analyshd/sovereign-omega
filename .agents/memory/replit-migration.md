---
name: Replit migration fixes
description: Decisions and constraints from migrating SOVEREIGN-Ω to Replit environment
---

## App runs on port 5000 (webview)
Replit webview output type requires port 5000. Workflow command: `python3 -m uvicorn api.main:app --host 0.0.0.0 --port 5000`

**Why:** Replit's preview pane only proxies port 5000 for webview output type. The system will reject any other port with webview.

## Use `python3 -m uvicorn` not `uvicorn` binary
The uvicorn binary path (`/home/runner/workspace/.pythonlibs/bin/uvicorn`) is not on PATH. `python3 -m uvicorn` always works.

## pandas-ta is blocked by Replit package firewall
`pandas-ta` is unavailable in the registry. Market feed has a native fallback using pandas `.rolling()` for ATR/RSI — already implemented. Do not add pandas-ta back to requirements.txt.

## DEPLOYER_PRIVATE_KEY must stay as a Replit Secret
It was previously a plain env var (leaked). It is now stored as an encrypted secret. The code reads it via `os.getenv("DEPLOYER_PRIVATE_KEY")` which works for both.

## LLM model for Replit AI Integration
Use `claude-haiku-4-5` (not `claude-3-5-haiku-20241022`). Set `base_url=AI_INTEGRATIONS_ANTHROPIC_BASE_URL` when available. Falls back to plain `ANTHROPIC_API_KEY`.

## FAISS dimension must match embedding engine
`memory/faiss_store.py` DIM was 256 but `reasoning/embedding_engine.py` returns 384-dim vectors. Fixed to DIM=384.

## SelfReflectionPlane embedding
Was using SHA-256 hash as embedding (32-dim). Fixed to use `EmbeddingEngine().embed()` with fallback to hash-based embed.

## MCP: resources/list and prompts/list are required
MCP spec mandates these methods. Both now return empty lists (valid response). Added before the unknown-method fallback in `mcp_server.py`.

## x402 payTo was zero address
`skills.py` had `payTo: 0x000...000`. Fixed to call `_get_agent_address()` which reads from `PharosClient`. The helper function must be defined locally in skills.py (not imported from x402.py).

## MCP premium skill dispatch was a stub
`mcp_server.py` lines 393–397 returned static text for trade_evaluate and reasoning_chain. Fixed to call real `TradingDecisionEngine` and `ChainManager`.

## MCP IQ formula was wrong
`moat_status` and `intelligence_score` in mcp_server.py used `lam * exp(lam * cycles)` — incorrect. Fixed to call `IntelligenceScorer.get_breakdown()` which uses the correct formula with domain mastery.

## HACKATHON.md chain ID typo
Said `688688`, correct testnet chain ID is `688689`. Fixed.
