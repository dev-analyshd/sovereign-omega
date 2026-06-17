#!/usr/bin/env bash
set -euo pipefail

NETWORK="${1:-pharos_testnet}"

echo "============================================"
echo " SOVEREIGN-Ω Contract Deployment"
echo " Network: $NETWORK"
echo "============================================"

if [[ -z "${DEPLOYER_PRIVATE_KEY:-}" ]]; then
  echo "ERROR: DEPLOYER_PRIVATE_KEY not set"
  echo "Set it as a Replit secret or environment variable. Never hardcode it."
  exit 1
fi

echo "Installing Hardhat dependencies..."
cd pharos/contracts/deploy
npm install --quiet

echo "Compiling contracts..."
npx hardhat compile

echo "Deploying to $NETWORK..."
npx hardhat run deploy.js --network "$NETWORK"

echo ""
echo "Deployment complete. See pharos/deployments/${NETWORK}_latest.json for addresses."
echo "Add the addresses to your .env file or Replit secrets."
