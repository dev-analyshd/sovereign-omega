# SOVEREIGN-Ω Contract Deployment Notes

## Status: Compiled ✓ | Deployed: Pending (fund wallet first)

The 3 Solidity contracts compiled successfully with Hardhat 2.22 / Solidity 0.8.24.

## Why Deployment Requires Manual Step

The Pharos testnet RPC (`https://testnet.pharosnetwork.xyz`) blocks POST/RPC calls from
cloud-hosted IPs via CloudFront WAF. Deploy from a local machine or a VPS.

## Deploy Command (from local machine)

```bash
cd pharos/contracts/deploy
npm install
# Set your private key (from Replit secrets or local env):
export DEPLOYER_PRIVATE_KEY=<your-key>
npx hardhat run deploy.js --network pharos_testnet
```

## Fund Your Wallet First

Get testnet tokens from the Pharos faucet:
https://testnet.pharosnetwork.xyz/

## After Deployment

Copy the 3 addresses from the output into your `.env`:
```
PHAROS_REGISTRY=0x...
PHAROS_VAULT=0x...
PHAROS_LEARNER=0x...
```

Then run:
```bash
python scripts/verify_deployment.py
```

## Networks

| Network | Chain ID | RPC | Explorer |
|---------|----------|-----|----------|
| Testnet | 688688 | https://testnet.pharosnetwork.xyz | https://testnet.pharosscan.xyz |
| Mainnet | 1672 | https://rpc.pharos.xyz | https://pharosscan.xyz |
