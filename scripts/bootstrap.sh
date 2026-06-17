#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo " SOVEREIGN-Ω Bootstrap"
echo "============================================"

# Check required env vars
REQUIRED=(DEPLOYER_PRIVATE_KEY SESSION_SECRET)
for var in "${REQUIRED[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

# Create data dirs
mkdir -p data

# Python deps
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Rust entropy module (if Rust is installed)
if command -v cargo &>/dev/null; then
  echo "[2/4] Building Rust entropy engine..."
  cd entropy
  pip install maturin --quiet
  maturin develop --release
  cd ..
else
  echo "[2/4] Rust not found. Skipping entropy module (Python fallback will be used)."
fi

# Node deps for Hardhat
echo "[3/4] Installing Hardhat dependencies..."
cd pharos/contracts/deploy
npm install --quiet
cd ../../..

# DB schema
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "[4/4] Applying database schema..."
  psql "$DATABASE_URL" -f storage/schema.sql
else
  echo "[4/4] DATABASE_URL not set. Skipping DB schema."
fi

echo ""
echo "Bootstrap complete. Run with:"
echo "  uvicorn api.main:app --host 0.0.0.0 --port 8000"
