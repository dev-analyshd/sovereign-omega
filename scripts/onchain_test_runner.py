"""
SOVEREIGN-Ω On-Chain Transaction Test Runner
Runs 50 on-chain transactions across all 3 Pharos contracts.
Usage: python3 scripts/onchain_test_runner.py
"""
import asyncio
import os
import sys
import time
import random
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def _async_tx(client, fn):
    """Run a synchronous _build_and_send_tx in a thread."""
    return await asyncio.to_thread(client._build_and_send_tx, fn)


async def run_onchain_tests():
    print("=" * 68)
    print("  SOVEREIGN-Ω — ON-CHAIN TRANSACTION TEST RUNNER")
    print("  Pharos Atlantic Testnet  |  Chain ID: 688689")
    print("=" * 68)

    try:
        from pharos.chain_client import PharosClient
        client = PharosClient()
        print(f"  Wallet : {client.address}")
        from web3 import Web3
        bal = client.w3.eth.get_balance(client.address)
        print(f"  Balance: {bal/1e18:.4f} PROS")
    except Exception as e:
        print(f"[FAIL] PharosClient init: {e}")
        return

    results = []
    tx_confirmed = 0
    tx_failed = 0

    async def run_tx(idx: int, label: str, fn_or_coro):
        nonlocal tx_confirmed, tx_failed
        start = time.time()
        try:
            if asyncio.iscoroutine(fn_or_coro):
                tx = await fn_or_coro
            else:
                tx = await _async_tx(client, fn_or_coro)
            elapsed = time.time() - start
            is_real = tx and len(tx) == 66 and tx.startswith("0x")
            icon = "✅" if is_real else "⚠️ "
            if is_real:
                tx_confirmed += 1
            else:
                tx_failed += 1
            short = tx[:20] + "..." if tx else "N/A"
            print(f"  {icon} [{idx:02d}] {label:<38} {short}  ({elapsed:.1f}s)")
            results.append({"idx": idx, "label": label, "tx": tx, "confirmed": is_real})
        except Exception as e:
            elapsed = time.time() - start
            tx_failed += 1
            msg = str(e)[:55]
            print(f"  ❌ [{idx:02d}] {label:<38} ERR: {msg}  ({elapsed:.1f}s)")
            results.append({"idx": idx, "label": label, "error": str(e), "confirmed": False})

    # ── Block 1: Registry.recordSilence (12 txns) ──────────────────────────────
    print(f"\n── Block 1: Registry · recordSilence (12 txns) {'─'*20}")
    for i in range(12):
        psi   = round(0.20 + i * 0.03, 4)
        delta = round(0.72 + i * 0.01, 4)
        reason = f"SILENCE: Ψ={psi} < Δ={delta} · plane_gap={delta-psi:.4f}"
        if client.registry:
            fn = client.registry.functions.recordSilence(
                int(psi * 1e18), int(delta * 1e18), reason[:200]
            )
            await run_tx(i + 1, f"recordSilence #{i+1}", fn)
        else:
            print(f"  ⚠️  [{i+1:02d}] registry not loaded — skipping")

    # ── Block 2: Vault.recordSilencedTrade (12 txns) ───────────────────────────
    print(f"\n── Block 2: Vault · recordSilencedTrade (12 txns) {'─'*17}")
    for i in range(12):
        psi   = round(0.30 + i * 0.02, 4)
        delta = round(0.80 + i * 0.005, 4)
        if client.vault:
            fn = client.vault.functions.recordSilencedTrade(
                int(psi * 1e18), int(delta * 1e18)
            )
            await run_tx(i + 13, f"recordSilencedTrade #{i+1}", fn)
        else:
            print(f"  ⚠️  [{i+13:02d}] vault not loaded — skipping")

    # ── Block 3: Learner.updateDomainMastery (14 txns) ─────────────────────────
    print(f"\n── Block 3: Learner · updateDomainMastery (14 txns) {'─'*15}")
    domains = [
        ("trading",         0.72, 28),
        ("defi",            0.65, 19),
        ("blockchain",      0.58, 14),
        ("reasoning",       0.80, 35),
        ("risk_management", 0.61, 12),
        ("consensus",       0.55, 8),
        ("analytics",       0.68, 22),
        ("security",        0.70, 17),
        ("strategy",        0.63, 11),
        ("research",        0.75, 30),
        ("market_data",     0.50, 6),
        ("arbitrage",       0.48, 5),
        ("sentiment",       0.52, 7),
        ("on_chain_data",   0.60, 10),
    ]
    for i, (domain, mastery, count) in enumerate(domains):
        if client.learner:
            fn = client.learner.functions.updateDomainMastery(
                domain, int(mastery * 1e18), count
            )
            await run_tx(i + 25, f"updateDomainMastery[{domain}]", fn)
        else:
            print(f"  ⚠️  [{i+25:02d}] learner not loaded — skipping")

    # ── Block 4: Registry.updateFAISSHash (6 txns) ─────────────────────────────
    print(f"\n── Block 4: Registry · updateFAISSHash (6 txns) {'─'*19}")
    for i in range(6):
        seed = f"faiss_v{i}_{time.time()}"
        raw_hash = hashlib.sha256(seed.encode()).digest()
        b32_hash = raw_hash  # bytes32 — 32 raw bytes
        vec_count = i * 128 + 64
        if client.registry:
            fn = client.registry.functions.updateFAISSHash(b32_hash, vec_count)
            await run_tx(i + 39, f"updateFAISSHash #{i+1} ({vec_count} vecs)", fn)
        else:
            print(f"  ⚠️  [{i+39:02d}] registry not loaded — skipping")

    # ── Block 5: Registry.updateMoat with growing Λ (6 txns) ──────────────────
    print(f"\n── Block 5: Registry · updateMoat — growing Λ (6 txns) {'─'*12}")
    lambdas = [0.010100, 0.010200, 0.010350, 0.010550, 0.010800, 0.011100]
    for i, lam in enumerate(lambdas):
        cycles = i + 5
        iq     = round(lam * 8.0, 6)
        await run_tx(
            i + 45,
            f"updateMoat [Λ={lam:.6f}]",
            client.update_registry_moat(lam, cycles, iq),
        )

    # ── Summary ────────────────────────────────────────────────────────────────
    print()
    print("=" * 68)
    total = len(results)
    print(f"  RESULTS: ✅ {tx_confirmed} confirmed on-chain  |  ❌ {tx_failed} failed  |  {total} total")
    print("=" * 68)

    confirmed = [r for r in results if r.get("confirmed")]
    if confirmed:
        print(f"\n  Confirmed on-chain tx hashes (first 8):")
        for r in confirmed[:8]:
            print(f"    [{r['idx']:02d}] {r.get('tx', 'N/A')}")
        if len(confirmed) > 8:
            print(f"    ... and {len(confirmed)-8} more confirmed txns")

    return results


if __name__ == "__main__":
    asyncio.run(run_onchain_tests())
