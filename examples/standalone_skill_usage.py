"""
SOVEREIGN-Ω · Standalone Skill Usage
=====================================
Demonstrates calling each of the 6 skills via plain HTTP.
No SDK, no runtime, no TRION engine needed — just requests.

Requirements: pip install requests
"""

import requests

BASE = "https://sovereignomega.onrender.com"
INVOKE = f"{BASE}/api/v1/skills/invoke"


def call_skill(skill_id: str, input_data: dict, payment_tx: str = None) -> dict:
    payload = {"skill_id": skill_id, "input": input_data}
    if payment_tx:
        payload["x402_payment_tx"] = payment_tx
    r = requests.post(f"{INVOKE}/{skill_id}", json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


# ─── 1. coherence_evaluate ────────────────────────────────────────────────────
print("\n=== 1. coherence_evaluate (Free) ===")
result = call_skill("coherence_evaluate", {
    "query": "Should I execute a BTC long position right now?",
    "domain": "trading",
    "context": {
        "volatility": 0.18,
        "novelty": 0.25,
        "environmental_signals": {"vix": 17.5, "btc_dom": 52.1}
    }
})
out = result["output"]
print(f"  Ψ score:    {out['psi_score']:.4f}")
print(f"  Δ threshold: {out['delta_threshold']:.4f}")
print(f"  Gate:       {'OPEN ✅' if out['gate_open'] else 'SILENCE 🔇'}")
print(f"  Planes:     P={out['plane_breakdown']['p']:.3f}  I={out['plane_breakdown']['i']:.3f}  "
      f"C={out['plane_breakdown']['c']:.3f}  S={out['plane_breakdown']['s']:.3f}  "
      f"W={out['plane_breakdown']['w']:.3f}")


# ─── 2. silence_check ─────────────────────────────────────────────────────────
print("\n=== 2. silence_check (Free) ===")
result = call_skill("silence_check", {
    "proposed_action": "Deploy 50% of vault capital into a new DeFi protocol",
    "stakes": 0.9,
    "domain": "trading"
})
out = result["output"]
print(f"  Silenced:   {out.get('silenced', out.get('silence_recommended'))}")
print(f"  Reason:     {out.get('reason', out.get('recommendation', '—'))}")
print(f"  Ψ score:    {out.get('psi_score', '—')}")


# ─── 3. moat_status ───────────────────────────────────────────────────────────
print("\n=== 3. moat_status (Free) ===")
result = call_skill("moat_status", {})
out = result["output"]
print(f"  Λ (moat):   {out.get('lambda', out.get('moat_lambda', '—'))}")
print(f"  IQ:         {out.get('iq', '—')}")
print(f"  Cycles:     {out.get('cycles', '—')}")


# ─── 4. intelligence_score ────────────────────────────────────────────────────
print("\n=== 4. intelligence_score (Free) ===")
result = call_skill("intelligence_score", {"include_projection": True})
out = result["output"]
print(f"  IQ:         {out.get('iq', out.get('intelligence_score', '—'))}")
print(f"  Λ:          {out.get('lambda', out.get('moat_lambda', '—'))}")


# ─── 5. trade_evaluate (Premium — requires x402 payment) ─────────────────────
print("\n=== 5. trade_evaluate (Premium — 1.0 PROS) ===")
print("  To invoke, first complete x402 payment flow:")
print(f"  1. GET  {BASE}/api/v1/x402/config")
print(f"  2. Send 1.0 PROS to 0xdBbf66CAD621dA3Ec186D18b29a135d2A5d42d20 on Pharos (chain 688689)")
print(f"  3. POST {BASE}/api/v1/x402/verify  {{tx_hash, skill_id, token}}")
print(f"  4. POST {INVOKE}/trade_evaluate with x402_payment_tx in body")
print()
print("  Example after payment:")
print("""
  result = call_skill("trade_evaluate", {
      "symbol": "BTC/USDT",
      "direction": "LONG",
      "strategy": "momentum",
      "market_data": {"price": 95000, "volume_24h": 28_000_000_000}
  }, payment_tx="0x<verified_tx>")
  # Returns: action, kelly_fraction, win_probability, expected_value, risk_level
""")


# ─── 6. reasoning_chain (Premium — requires x402 payment) ────────────────────
print("\n=== 6. reasoning_chain (Premium — 2.0 PROS) ===")
print("  Runs 5 parallel reasoning chains, detects contradictions, returns best answer.")
print("  Same x402 flow as trade_evaluate — send 2.0 PROS before invoking.")


# ─── Skills discovery ─────────────────────────────────────────────────────────
print("\n=== Skills Manifest ===")
manifest = requests.get(f"{BASE}/api/v1/skills", timeout=10).json()
print(f"  Agent:  {manifest.get('agent_name', manifest.get('agent_id'))}")
print(f"  Skills: {len(manifest.get('skills', []))}")
for s in manifest.get("skills", []):
    tier_label = "💰 Premium" if s["tier"] == "premium" else "🆓 Free   "
    print(f"    {tier_label}  {s['id']}")

print("\n✅ All free skills callable. Premium skills require x402 $PROS payment on Pharos.")
