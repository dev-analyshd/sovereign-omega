"""
SOVEREIGN-Ω x402 Payment Protocol
Implements HTTP 402 Payment Required for machine-to-machine commerce on Pharos chain.
Supports $PROS (native) and USDC payments.
Compatible with: x402 Foundation standard, Pharos MaaS, Anvita Flow
"""
import os
import time
import hashlib
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------------
# x402 Config
# ---------------------------------------------------------------------------
PHAROS_NETWORK = os.getenv("PHAROS_NETWORK", "testnet")
FACILITATOR_URL = "https://x402.pharos.xyz/facilitator"

PAYMENT_TARGETS = {
    "testnet": {
        "chain_id": 688688,
        "rpc": "https://testnet.pharosnetwork.xyz",
        "pros_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # native PROS
        "usdc_address": "0x0000000000000000000000000000000000000000",   # fill after deploy
    },
    "mainnet": {
        "chain_id": 1672,
        "rpc": "https://rpc.pharos.xyz",
        "pros_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "usdc_address": "0x0000000000000000000000000000000000000000",
    },
}

# ---------------------------------------------------------------------------
# In-memory payment nonce store (production: use Redis / DB)
# ---------------------------------------------------------------------------
_verified_payments: dict = {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class PaymentVerifyRequest(BaseModel):
    tx_hash: str
    skill_id: str
    caller_address: Optional[str] = None
    amount_token: Optional[str] = None
    token: Optional[str] = "PROS"


class PaymentVerifyResponse(BaseModel):
    verified: bool
    tx_hash: str
    skill_id: str
    token: str
    nonce: Optional[str] = None
    expires_at: Optional[int] = None
    message: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/x402/config")
async def x402_config():
    """
    Return x402 payment configuration for this agent.
    Callers use this to know how to pay for premium skills.
    """
    net = PAYMENT_TARGETS.get(PHAROS_NETWORK, PAYMENT_TARGETS["testnet"])
    agent_address = _get_agent_address()
    return {
        "version": "1",
        "network": PHAROS_NETWORK,
        "chain_id": net["chain_id"],
        "agent_address": agent_address,
        "facilitator": FACILITATOR_URL,
        "accepted_tokens": [
            {
                "symbol": "PROS",
                "type": "native",
                "address": net["pros_address"],
                "decimals": 18,
                "network": PHAROS_NETWORK,
            },
            {
                "symbol": "USDC",
                "type": "erc20",
                "address": net["usdc_address"],
                "decimals": 6,
                "network": PHAROS_NETWORK,
            },
        ],
        "skill_prices": _get_all_skill_prices(),
        "discount_pros": "20%",
        "discount_note": "Pay in $PROS for 20% discount (aligned with Pharos MaaS launch incentive)",
    }


@router.post("/x402/verify", response_model=PaymentVerifyResponse)
async def verify_payment(req: PaymentVerifyRequest):
    """
    Verify a payment transaction on Pharos chain.
    Returns a short-lived nonce that can be passed to skill invocations.
    """
    if not req.tx_hash or len(req.tx_hash) < 10:
        return PaymentVerifyResponse(
            verified=False,
            tx_hash=req.tx_hash,
            skill_id=req.skill_id,
            token=req.token or "PROS",
            message="Invalid transaction hash",
        )

    # Simulation mode (no private key set)
    simulation = not (os.getenv("AGENT_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY"))
    verified = False

    if simulation:
        verified = True
        message = f"[SIMULATION] Payment accepted. Deploy with AGENT_PRIVATE_KEY for on-chain verification."
    else:
        try:
            from pharos.chain_client import PharosClient
            client = PharosClient()
            receipt = client.w3.eth.get_transaction_receipt(req.tx_hash)
            verified = receipt is not None and receipt.status == 1
            message = "Payment verified on Pharos chain" if verified else "Transaction not found or failed"
        except Exception as e:
            message = f"Verification error: {str(e)}"

    if verified:
        nonce = hashlib.sha256(f"{req.tx_hash}:{req.skill_id}:{time.time()}".encode()).hexdigest()[:32]
        expires_at = int(time.time()) + 300  # 5 min window
        _verified_payments[nonce] = {
            "tx_hash": req.tx_hash,
            "skill_id": req.skill_id,
            "expires_at": expires_at,
        }
        return PaymentVerifyResponse(
            verified=True,
            tx_hash=req.tx_hash,
            skill_id=req.skill_id,
            token=req.token or "PROS",
            nonce=nonce,
            expires_at=expires_at,
            message=message,
        )

    return PaymentVerifyResponse(
        verified=False,
        tx_hash=req.tx_hash,
        skill_id=req.skill_id,
        token=req.token or "PROS",
        message=message,
    )


@router.get("/x402/status")
async def x402_status():
    """x402 protocol status — active payments, facilitator connectivity."""
    active = sum(
        1 for p in _verified_payments.values() if p["expires_at"] > time.time()
    )
    return {
        "protocol": "x402",
        "version": "1",
        "status": "active",
        "network": PHAROS_NETWORK,
        "facilitator": FACILITATOR_URL,
        "active_payment_windows": active,
        "supported_tokens": ["PROS", "USDC"],
        "pros_discount": "20%",
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_agent_address() -> str:
    try:
        from pharos.chain_client import PharosClient
        client = PharosClient()
        return client.address
    except Exception:
        return os.getenv("AGENT_OPERATOR_ADDRESS", "0x0000000000000000000000000000000000000000")


def _get_all_skill_prices() -> dict:
    from api.routes.skills import SKILLS_MANIFEST
    prices = {}
    for skill in SKILLS_MANIFEST["skills"]:
        if skill.get("tier") == "premium":
            prices[skill["id"]] = {
                "PROS": skill.get("x402_price_pros", "1.0"),
                "USDC": skill.get("x402_price_usdc", "0.10"),
                "PROS_discounted": str(round(float(skill.get("x402_price_pros", "1.0")) * 0.8, 2)),
            }
    return prices


def validate_nonce(nonce: str, skill_id: str) -> bool:
    """Validate a payment nonce. Used by skill invocation endpoints."""
    if nonce not in _verified_payments:
        return False
    entry = _verified_payments[nonce]
    if entry["expires_at"] < time.time():
        del _verified_payments[nonce]
        return False
    if entry["skill_id"] != skill_id:
        return False
    return True
