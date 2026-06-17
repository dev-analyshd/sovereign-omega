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
        lambda_val = moat.get_current_lambda()

        try:
            tx = await client.update_registry_moat(lambda_val, moat.n_cycles, iq)
            status = "simulated" if client.simulation_mode else "synced"
            note = None
        except Exception as chain_err:
            err_str = str(chain_err)
            if "Moat cannot decrease" in err_str or "execution reverted" in err_str:
                tx = None
                status = "skipped"
                note = "On-chain Λ already >= local Λ. Monotonicity enforced — sync skipped. Accumulate more cycles to exceed on-chain value."
            else:
                raise

        return {
            "status": status,
            "tx_hash": tx,
            "lambda": lambda_val,
            "n_cycles": moat.n_cycles,
            "iq": iq,
            **({"note": note} if note else {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
