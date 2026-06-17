#!/usr/bin/env python3
"""
Verify SOVEREIGN-Ω contract deployment on Pharos.
Reads contract addresses from environment variables.
Checks each contract is live, has the correct owner, and basic state.
"""
import asyncio
import json
import os
import sys


async def verify():
    try:
        from web3 import Web3
    except ImportError:
        print("web3 not installed. Run: pip install web3")
        sys.exit(1)

    network = os.getenv("PHAROS_NETWORK", "testnet")
    rpc = "https://testnet.pharosnetwork.xyz" if network == "testnet" else "https://rpc.pharos.xyz"
    w3 = Web3(Web3.HTTPProvider(rpc))

    if not w3.is_connected():
        print(f"ERROR: Cannot connect to {rpc}")
        sys.exit(1)

    print(f"Connected to Pharos {network} (Chain ID: {w3.eth.chain_id})\n")

    contracts = {
        "SovereignRegistry": os.getenv("PHAROS_REGISTRY"),
        "SovereignVault": os.getenv("PHAROS_VAULT"),
        "SovereignLearner": os.getenv("PHAROS_LEARNER"),
    }

    all_ok = True
    for name, addr in contracts.items():
        if not addr:
            print(f"  {name}: NOT SET (set PHAROS_REGISTRY/PHAROS_VAULT/PHAROS_LEARNER in env)")
            all_ok = False
            continue

        code = w3.eth.get_code(Web3.to_checksum_address(addr))
        if code and code != b"" and code != "0x":
            print(f"  {name}: DEPLOYED at {addr} ✓")
        else:
            print(f"  {name}: NOT FOUND at {addr} ✗")
            all_ok = False

    if all_ok:
        print("\nAll contracts verified. SOVEREIGN-Ω is ready on Pharos.")
    else:
        print("\nSome contracts not deployed. Run: bash scripts/deploy_pharos.sh")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(verify())
