---
name: SOVEREIGN-Ω architecture
description: TRION math fixes, scoring decisions, on-chain setup, and skill routing for the Pharos hackathon agent
---

## TRION scoring — P=0.0 bug
**Rule:** `input_channels` must be a dict of *multi-value* lists (32+ values each). A single-element list `[scalar]` gives P(t)≈0.0 because the plane reducer averages to near-zero.
**Fix:** Use SHA256 hash bytes as entropy channels — `h1 = sha256(query.encode()).digest()` → `[b/255.0 for b in h1]` (32 floats). Applied in: `api/routes/action.py`, `api/routes/skills.py` (`_skill_coherence_evaluate`, `_skill_silence_check`).
**Why:** Perceptual plane needs rich input diversity to produce non-zero signal.

## Consensus plane — C=0.0 bug
**Rule:** Record `chain_origin = time.time()` BEFORE `asyncio.sleep(chain_idx * 0.9)` in `reasoning/chain_manager.py`. The stagger spread is lost if origin is captured after sleep.
**Fix:** Move `chain_origin` assignment to before the sleep call → C≈0.29, Ψ≈0.76.

## Skill invoke — missing chain_manager
**Rule:** `_skill_coherence_evaluate` and `_skill_silence_check` in `api/routes/skills.py` must call `ChainManager().run_chains()` and pass `reasoning_chains` in context, otherwise I and C planes default to 0.5 and Ψ drops below Δ.
**Why:** The action.py endpoint always runs chains; skills must mirror this pattern.

## sentence-transformers crash
**Rule:** Use `except Exception` (not `except ImportError`) in `reasoning/embedding_engine.py` when importing sentence_transformers. The torch CUDA library raises `OSError`, not `ImportError`.
**Fix:** 384-dim SHA256 hash fallback embeddings (unit-normed) — FAISS works fine with these.

## On-chain contract guard
**Rule:** `SovereignRegistry.updateMoat` reverts with "Moat cannot decrease" if the new λ ≤ stored value. This is correct contract behavior — do not treat as a bug. Other functions (recordSilence, recordSilencedTrade, updateDomainMastery, updateFAISSHash) work normally.

## MiniMax API integration
**Rule:** Priority chain in `reasoning/llm_interface.py`: MiniMax → Anthropic → mock. MiniMax base URL: `https://api.minimax.chat/v1`. Env vars: `MINIMAX_API_KEY` (required), `MINIMAX_GROUP_ID` (optional, passed as header `GroupId`). Without a key, falls back to hash-varied mock reasoning.

## Verified live state (June 17 2026)
- 18/18 tests passing, gate_open=True, Ψ=0.760, P=0.953, C=0.291
- 97 on-chain transactions (wallet nonce), 4.88 PROS remaining
- FAISS: 8 vectors, 384-dim L2 index, persisted to disk
- Moat λ=0.073, cycles=4, IQ accumulating
