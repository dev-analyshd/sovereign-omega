import os
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/pharos/status")
async def pharos_status():
    try:
        from pharos.chain_client import PharosClient
        client = PharosClient()

        if client.simulation_mode:
            return {
                "connected": False,
                "mode": "simulation",
                "address": client.address,
                "chain_id": client.chain_id,
                "network": os.getenv("PHAROS_NETWORK", "testnet"),
                "vault_balance": 0.0,
                "registry": client.registry_address,
                "vault": client.vault_address,
                "learner": client.learner_address,
                "note": "Set DEPLOYER_PRIVATE_KEY secret to enable on-chain transactions. Simulation mode: all chain calls return mock tx hashes.",
            }

        connected = await client.is_connected()
        balance = await client.get_vault_balance()
        return {
            "connected": connected,
            "mode": "on_chain",
            "address": client.address,
            "chain_id": client.chain_id,
            "network": os.getenv("PHAROS_NETWORK", "testnet"),
            "vault_balance": balance,
            "registry": client.registry_address,
            "vault": client.vault_address,
            "learner": client.learner_address,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/pharos/sync")
async def sync_to_pharos():
    try:
        from pharos.chain_client import PharosClient
        from core.moat_accumulator import MoatAccumulator
        from learning.intelligence_score import IntelligenceScorer

        client = PharosClient()
        moat = MoatAccumulator()
        scorer = IntelligenceScorer()
        iq = await scorer.compute()

        tx = await client.update_registry_moat(moat.get_current_lambda(), moat.n_cycles, iq)
        return {
            "status": "simulated" if client.simulation_mode else "synced",
            "tx_hash": tx,
            "lambda": moat.get_current_lambda(),
            "iq": iq,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
