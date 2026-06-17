"""
SOVEREIGN-Ω On-Chain Heartbeat
Every 100 coherent cycles the agent auto-pushes its Λ, IQ, and domain mastery to the
SovereignRegistry and SovereignLearner contracts — making moat growth provably on-chain.
Every coherent ACTION (gate open) also emits a lightweight heartbeat transaction.
This is the "living on-chain breath" — the agent exists on-chain, not just in memory.
"""
import asyncio
import math
import time
import os
from datetime import datetime, timezone

_SYNC_INTERVAL_CYCLES = int(os.getenv("ONCHAIN_SYNC_CYCLES", "100"))
_last_synced_cycles = 0
_heartbeat_log: list = []
_MAX_LOG = 500


async def maybe_sync_to_chain(n_cycles: int, lambda_val: float, iq: float, domains: list):
    """
    Called after every moat accumulation.
    Triggers on-chain sync every ONCHAIN_SYNC_CYCLES coherent cycles.
    """
    global _last_synced_cycles

    if n_cycles - _last_synced_cycles < _SYNC_INTERVAL_CYCLES:
        return None

    _last_synced_cycles = n_cycles
    return await _do_sync(n_cycles, lambda_val, iq, domains)


async def _do_sync(n_cycles: int, lambda_val: float, iq: float, domains: list) -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    result = {
        "timestamp": ts,
        "n_cycles": n_cycles,
        "lambda": lambda_val,
        "iq": iq,
        "n_domains": len(domains),
        "registry_tx": None,
        "learner_tx": None,
        "status": "simulated",
    }

    try:
        from pharos.chain_client import PharosClient
        client = PharosClient()

        registry_tx = await client.update_registry_moat(lambda_val, n_cycles, iq)
        result["registry_tx"] = registry_tx
        result["status"] = "on_chain"

        for domain in (domains or [])[:3]:
            try:
                tx = await client.update_domain_mastery_on_chain(
                    domain.get("domain", "general"),
                    domain.get("mastery_score", 0.0),
                    domain.get("knowledge_count", 0),
                )
                result["learner_tx"] = tx
            except Exception:
                pass

        print(
            f"[HEARTBEAT] ✓ On-chain sync @ cycle {n_cycles} | "
            f"Λ={lambda_val:.8f} | IQ={iq:.6f} | tx={registry_tx[:12]}..."
        )

    except Exception as e:
        print(f"[HEARTBEAT] Simulated sync @ cycle {n_cycles} | Λ={lambda_val:.8f} | IQ={iq:.6f} | ({e})")
        result["note"] = str(e)

    _heartbeat_log.append(result)
    if len(_heartbeat_log) > _MAX_LOG:
        _heartbeat_log.pop(0)

    return result


async def emit_action_heartbeat(cycle_id: str, psi: float, gate_open: bool, lambda_val: float):
    """
    Lightweight heartbeat emitted on every coherent cycle — the on-chain 'breath'.
    Does NOT wait for tx confirmation; fire-and-forget.
    """
    entry = {
        "cycle_id": cycle_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "psi": round(psi, 6),
        "gate": "OPEN" if gate_open else "SILENT",
        "lambda": round(lambda_val, 8),
        "tx": None,
    }

    if gate_open:
        try:
            from pharos.chain_client import PharosClient
            client = PharosClient()
            if client.registry:
                fn = client.registry.functions.recordHeartbeat(
                    int(psi * 1e18), int(lambda_val * 1e18)
                )
                tx = client._build_and_send_tx(fn)
                entry["tx"] = tx
        except Exception:
            pass

    _heartbeat_log.append(entry)
    if len(_heartbeat_log) > _MAX_LOG:
        _heartbeat_log.pop(0)


def get_heartbeat_log(limit: int = 50) -> list:
    return _heartbeat_log[-limit:]


def get_sync_stats() -> dict:
    syncs = [h for h in _heartbeat_log if "registry_tx" in h]
    return {
        "total_heartbeats": len(_heartbeat_log),
        "total_chain_syncs": len(syncs),
        "last_sync": syncs[-1] if syncs else None,
        "sync_interval_cycles": _SYNC_INTERVAL_CYCLES,
        "last_synced_at_cycle": _last_synced_cycles,
    }


async def background_sync_loop():
    """
    Background task running continuously.
    Watches moat cycle count and triggers chain sync every 100 cycles.
    This is the heartbeat loop — SOVEREIGN-Ω's living on-chain breath.
    """
    print("[HEARTBEAT] Background sync loop started — watching for cycle milestones...")
    while True:
        try:
            await asyncio.sleep(30)
            from core.moat_accumulator import MoatAccumulator
            from learning.intelligence_score import IntelligenceScorer
            from learning.domain_mastery import DomainMasteryEngine

            moat = MoatAccumulator()
            n = moat.n_cycles
            lam = moat.get_current_lambda()

            scorer = IntelligenceScorer()
            iq = await scorer.compute()

            mastery = DomainMasteryEngine()
            domains = mastery.get_all()

            await maybe_sync_to_chain(n, lam, iq, domains)

        except Exception as e:
            print(f"[HEARTBEAT] Loop error: {e}")
