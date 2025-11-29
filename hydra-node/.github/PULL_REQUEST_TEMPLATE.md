## What
Standalone Hydra Settlement Layer (Member 4) — CBOR metadata, ED25519 signature verification, CLI and REST endpoints, local persistence.

## How to run (short)
```bash
cd hydra-node
python -m venv .venv && source .venv/bin/activate  # or use conda/pipenv
pip install -r requirements.txt
./hydra_control_demo.sh
```

## Acceptance (what I tested)
- ✅ CLI flows: open → commit (CBOR) → attach-proof → finalize
- ✅ CBOR hex printed in commit output (600+ chars)
- ✅ state/heads.json and state/orders.json persisted
- ✅ --skip-sig-check supported for demo
- ✅ Docker build successful
- ✅ Unit tests pass (CBOR, idempotency, state persistence)
- ✅ No private keys in committed files

## Notes & next steps
- Private keys moved to `.gitignored` `demo_keys_local.json` (NEVER commit)
- CI added with security checks and smoke tests
- Next: integrate with real Hydra node (hydra-node API) and Cardano devnet
- Ready for Member1 (Architect) and Member2 (Sentinel) review

## Files changed
- `hydra_control.py` - Main settlement client with CBOR generation
- `signing_helper.py` - ED25519 key generation and signing
- `docker-compose.yml` - Standalone container setup
- `Dockerfile.hydra_control` - Python container build
- `requirements.txt` - Python dependencies
- `test_vectors/` - Sample payloads and keys (public keys only)
- `test_hydra_control.py` - Unit tests
- `.github/workflows/ci.yml` - CI/CD pipeline
- `README_RUN.md` - Complete documentation
- `.gitignore` - Security rules
- `demo-logs.txt` - Demo artifacts
- `CHANGELOG.md` - Release notes

## Security
- ✅ No private keys in committed files
- ✅ `.gitignore` protects sensitive files
- ✅ CI checks for private key leaks
- ⚠️ `--skip-sig-check` is ONLY for demos
