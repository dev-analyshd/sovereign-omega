"""
SOVEREIGN-Ω · Pharos Skill Composition
========================================
Shows how to compose multiple skills into an agent decision workflow.
This is the Skill-to-Agent cascade pattern for Phase 1 submission.

Pattern:
  coherence_evaluate → silence_check → [trade_evaluate if gate open]

Requirements: pip install requests
"""

import requests
import json
from datetime import datetime

BASE = "https://sovereignomega.onrender.com"
INVOKE = f"{BASE}/api/v1/skills/invoke"


def invoke(skill_id: str, input_data: dict, payment_tx: str = None) -> dict:
    payload = {"skill_id": skill_id, "input": input_data}
    if payment_tx:
        payload["x402_payment_tx"] = payment_tx
    r = requests.post(f"{INVOKE}/{skill_id}", json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("output", data)


def sovereign_decision_pipeline(
    market_query: str,
    symbol: str = "BTC/USDT",
    direction: str = "LONG",
    trade_payment_tx: str = None
) -> dict:
    """
    Full Skill-to-Agent cascade using 3 SOVEREIGN-Ω skills:
    1. coherence_evaluate  → is the environment coherent enough to reason?
    2. silence_check       → should this specific action be silenced?
    3. trade_evaluate      → (premium, optional) what's the optimal position size?

    Returns a structured decision dict.
    """
    ts = datetime.utcnow().isoformat()
    print(f"\n{'='*60}")
    print(f"SOVEREIGN-Ω Skill Cascade · {ts}")
    print(f"Query: {market_query}")
    print(f"{'='*60}")

    # ── Skill 1: Coherence Evaluate ──────────────────────────────────────────
    print("\n[Skill 1/3] coherence_evaluate")
    coherence = invoke("coherence_evaluate", {
        "query": market_query,
        "domain": "trading",
        "context": {
            "volatility": 0.18,
            "novelty": 0.25,
            "environmental_signals": {"vix": 17.5, "btc_dom": 52.1},
            "input_channels": {"price_feed": [95000, 95200, 95050, 95280]}
        }
    })
    psi = coherence.get("psi_score", 0)
    delta = coherence.get("delta_threshold", 1)
    gate = coherence.get("gate_open", False)
    print(f"  Ψ = {psi:.4f}  Δ = {delta:.4f}  Gate: {'OPEN ✅' if gate else 'SILENCE 🔇'}")
    planes = coherence.get("plane_breakdown", {})
    print(f"  Planes → P={planes.get('p',0):.3f}  I={planes.get('i',0):.3f}  "
          f"C={planes.get('c',0):.3f}  S={planes.get('s',0):.3f}  W={planes.get('w',0):.3f}")

    if not gate:
        print("\n  → Silence Protocol activated. Pipeline halted.")
        return {
            "decision": "SILENCE",
            "reason": f"Ψ ({psi:.4f}) < Δ ({delta:.4f}) — cognitive coherence insufficient",
            "psi": psi, "delta": delta, "skills_invoked": 1
        }

    # ── Skill 2: Silence Check ───────────────────────────────────────────────
    print("\n[Skill 2/3] silence_check")
    silence = invoke("silence_check", {
        "proposed_action": f"{direction} {symbol}",
        "stakes": 0.75,
        "domain": "trading"
    })
    silenced = silence.get("silenced", silence.get("silence_recommended", False))
    reason = silence.get("reason", silence.get("recommendation", "—"))
    print(f"  Silenced: {silenced}")
    print(f"  Reason:   {reason}")

    if silenced:
        return {
            "decision": "SILENCE",
            "reason": reason,
            "psi": psi, "delta": delta, "skills_invoked": 2
        }

    # ── Skill 3: Trade Evaluate (Premium) ────────────────────────────────────
    if trade_payment_tx:
        print("\n[Skill 3/3] trade_evaluate (Premium — x402 verified)")
        trade = invoke("trade_evaluate", {
            "symbol": symbol,
            "direction": direction,
            "strategy": "momentum",
            "market_data": {"price": 95000, "volume_24h": 28_000_000_000}
        }, payment_tx=trade_payment_tx)
        action = trade.get("action", "UNKNOWN")
        kelly = trade.get("kelly_fraction", 0)
        risk = trade.get("risk_level", "UNKNOWN")
        print(f"  Action:       {action}")
        print(f"  Kelly fraction: {kelly:.4f}")
        print(f"  Risk level:   {risk}")
        return {
            "decision": action,
            "kelly_fraction": kelly,
            "risk_level": risk,
            "psi": psi, "delta": delta,
            "skills_invoked": 3,
            "trade_detail": trade
        }
    else:
        print("\n[Skill 3/3] trade_evaluate — SKIPPED (no x402 payment)")
        print("  Send 1.0 PROS on Pharos chain 688689, verify at /api/v1/x402/verify")
        return {
            "decision": "GATE_OPEN_PAYMENT_REQUIRED",
            "reason": "Coherence gate open. Provide x402 payment to invoke trade_evaluate.",
            "psi": psi, "delta": delta,
            "skills_invoked": 2
        }


def show_agent_card():
    """Fetch and display the agent's A2A discovery card."""
    r = requests.get(f"{BASE}/.well-known/agent.json", timeout=10)
    card = r.json()
    print("\n=== Agent Discovery Card ===")
    print(f"  Name:         {card['name']}")
    print(f"  Version:      {card['version']}")
    print(f"  Chain:        {card['chain']['name']} (testnet {card['chain']['chain_id_testnet']})")
    print(f"  Capabilities: {list(card['capabilities'].keys())}")
    contracts = card['chain']['contracts']
    print(f"  Registry:  {contracts['registry']}")
    print(f"  Vault:     {contracts['vault']}")
    print(f"  Learner:   {contracts['learner']}")


if __name__ == "__main__":
    show_agent_card()

    # Run the full 3-skill cascade
    result = sovereign_decision_pipeline(
        market_query="Market conditions for BTC long position — evaluate coherence and trade viability",
        symbol="BTC/USDT",
        direction="LONG",
        trade_payment_tx=None  # Set to verified tx hash to invoke premium trade_evaluate
    )

    print(f"\n{'='*60}")
    print("FINAL DECISION:")
    print(json.dumps(result, indent=2))

    print(f"\n{'='*60}")
    print("To activate premium trade_evaluate:")
    print(f"  1. GET {BASE}/api/v1/x402/config")
    print(f"  2. Send 1.0 PROS → 0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20")
    print(f"  3. POST {BASE}/api/v1/x402/verify")
    print(f"  4. Re-run with trade_payment_tx='0x...'")
