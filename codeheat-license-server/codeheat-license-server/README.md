# CodeHeat License Server (Stripe → Webhook → Mint → Download)

This repo contains the public backend code. **Private key and minter are NOT in GitHub.**

## What is private?
- Ed25519 private key (base64) → env var `LICENSE_PRIVATE_KEY_B64`
- Minter module python file → env var `LICENSE_MINTER_PY_B64` OR local `private/license_minter.py`

## Local dev
1) Create venv
2) Put secrets into `.env` (not committed)
3) Run server
4) Use Stripe CLI to forward webhooks
5) Run a test checkout via `/api/checkout`

## Railway
1) Deploy from GitHub
2) Add Postgres plugin
3) Set env vars
4) Add Stripe webhook endpoint pointing to `/webhook`
