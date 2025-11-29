# Standalone Hydra Settlement Layer for SON
# Complete offline implementation with CBOR generation and signature verification

## Overview
This standalone settlement layer demonstrates all Member-4 responsibilities:
- ✅ CBOR metadata generation for ForkShield L1 Capsules
- ✅ ED25519 signature verification with PyNaCl
- ✅ Agent signature aggregation
- ✅ Idempotency key computation
- ✅ Deterministic state management
- ✅ REST API endpoints

**No external dependencies required - runs completely offline!**

## Quick Start (Local Python)

### Prerequisites
- Python 3.10+
- Install dependencies: `pip install -r requirements.txt`

### Generate Agent Keys
```bash
python signing_helper.py
```
This generates ED25519 keypairs for sentinel, oracle, and midnight agents.

### Run the Demo
```bash
chmod +x hydra_control_demo.sh
./hydra_control_demo.sh
```

Expected output:
```
=== SON Hydra Settlement Layer Demo ===
Step 1: Opening Hydra head for session sess-001
{"event": "HEAD_OPENED", "head_id": "h-sess-001", "session_id": "sess-001", "timestamp": "..."}

Step 2: Committing verdict order (SAFE transaction)
{"event": "ORDER_COMMITTED", "order_id": "o-sess-001-0001", "head_id": "h-sess-001", "cbor_hex": "...", "idempotency_key": "...", "timestamp": "..."}

Step 3: Attaching ZK proof reference
{"event": "PROOF_ATTACHED", "order_id": "o-sess-001-0001", "session_id": "sess-001", "proof_ref": "zk-proof-safe-transaction-uuid", "timestamp": "..."}

Step 4: Finalizing Hydra head
{"event": "ORDER_FINALIZED", "head_id": "h-sess-001", "finalized_orders": ["o-sess-001-0001"], "proof_refs": ["zk-proof-safe-transaction-uuid"], "timestamp": "..."}

=== Demo Complete ===
```

## Manual CLI Usage

### Open Head
```bash
python hydra_control.py --open --session-id sess-001
```

### Commit Verdict (Skip Signature Check)
```bash
python hydra_control.py --commit --session-id sess-001 --payload test_vectors/v1_safe.json --skip-sig-check
```

### Attach Proof
```bash
python hydra_control.py --attach-proof --session-id sess-001 --order-id o-sess-001-0001 --proof-ref mock-zk-111
```

### Finalize Head
```bash
python hydra_control.py --finalize --session-id sess-001
```

### Generate CBOR Only
```bash
python hydra_control.py --cbor-only --payload test_vectors/v1_safe.json
```

## Docker Usage

### Build and Run
```bash
docker-compose up --build -d
```

### Check Status
```bash
docker-compose ps
docker-compose logs hydra-control
```

### Test API
```bash
# Open head
curl -X POST http://localhost:8085/open -H "Content-Type: application/json" -d '{"session_id": "sess-002"}'

# Commit verdict
curl -X POST http://localhost:8085/commit -H "Content-Type: application/json" -d '{"session_id": "sess-002", "verdict_payload": {...}, "skip_sig_check": true}'

# Finalize
curl -X POST http://localhost:8085/finalize -H "Content-Type: application/json" -d '{"session_id": "sess-002"}'
```

## CBOR Metadata Structure

The settlement layer generates CBOR metadata matching the ForkShield L1 Capsule:

```json
{
  "721": {
    "674": {
      "ForkShield": {
        "verdict": "SAFE|DANGER",
        "evidence_root": "sha256:...",
        "agent_collaboration": [...],
        "cost": "1.0 ADA",
        "signatures": ["base64_sig1", "base64_sig2", "base64_sig3"],
        "timestamp": "ISO8601",
        "session_id": "sess-xxx"
      }
    }
  }
}
```

Example CBOR hex output:
```
a11802a164466f726b536869656c64a6667665726469637464534146456b65766964656e63655f686173687838207368613235363a616263...
```

## Signature Verification

### Generate Real Signatures
```bash
# Sign a message
python signing_helper.py --sign --private-key <base64_private_key> --message-file test_vectors/message_to_sign.json
```

### Skip Verification (Demo Mode)
Use `--skip-sig-check` flag for testing without real signatures.

## State Persistence

All state is persisted in `./state/`:
- `heads.json` - Head metadata and status
- `orders.json` - Order details and CBOR data

Example heads.json:
```json
{
  "sess-001": {
    "head_id": "h-sess-001",
    "session_id": "sess-001",
    "status": "FINALIZED",
    "participants": ["sentinel", "oracle", "midnight"],
    "orders": ["o-sess-001-0001"],
    "created_at": "2025-11-29T18:30:00.000000",
    "finalized_at": "2025-11-29T18:30:05.000000"
  }
}
```

## Event Timeline Example

```
[HYDRA] HEAD_OPENED head_id=h-sess-001 session=sess-001
[HYDRA] ORDER_COMMITTED order_id=o-sess-001-0001 head_id=h-sess-001 cbor_hex=a11802a164...
[HYDRA] PROOF_ATTACHED order_id=o-sess-001-0001 proof_ref=zk-proof-safe-transaction-uuid
[HYDRA] ORDER_FINALIZED head_id=h-sess-001 finalized_orders=["o-sess-001-0001"] proof_refs=["zk-proof-safe-transaction-uuid"]
```

## Integration for Teammates

### REST API Endpoints
The settlement layer exposes these endpoints when run with `--server`:

- `POST /open` - Open new head
  ```json
  {"session_id": "your-session-id"}
  // Returns: {"event": "HEAD_OPENED", "head_id": "h-your-session-id", ...}
  ```

- `POST /commit` - Commit verdict with CBOR generation
  ```json
  {"session_id": "your-session-id", "verdict_payload": {...}, "skip_sig_check": true}
  // Returns: {"event": "ORDER_COMMITTED", "cbor_hex": "...", "idempotency_key": "...", ...}
  ```

- `POST /attach-proof` - Attach ZK proof reference
  ```json
  {"session_id": "your-session-id", "order_id": "o-...", "proof_ref": "zk-proof-hash"}
  // Returns: {"event": "PROOF_ATTACHED", ...}
  ```

- `POST /finalize` - Finalize head settlement
  ```json
  {"session_id": "your-session-id"}
  // Returns: {"event": "ORDER_FINALIZED", "finalized_orders": [...], "proof_refs": [...], ...}
  ```

### Expected Event Flow
1. **HEAD_OPENED** → Head created, ready for orders
2. **ORDER_COMMITTED** → CBOR metadata generated, order ready for proof
3. **PROOF_ATTACHED** → ZK proof linked to order
4. **ORDER_FINALIZED** → Head closed, settlement complete

### Future Integration Points
- Replace `--skip-sig-check` with real signature validation
- Connect to live Hydra node API endpoints
- Add Cardano devnet for L1 settlement testing
- Implement shared idempotency key validation

## Security & Production Notes

⚠️ **IMPORTANT**: The `--skip-sig-check` flag is ONLY for demos. Always use real signature verification in production.

⚠️ **Private Keys**: Never commit `demo_keys_local.json` or any file containing private keys to git.

⚠️ **State Persistence**: The `./state/` directory contains settlement state. Back up regularly in production.

## Member-4 Compliance Checklist

- ✅ **CBOR Generation**: Valid ForkShield L1 Capsule metadata
- ✅ **Signature Verification**: ED25519 with PyNaCl
- ✅ **Agent Aggregation**: Sentinel + Oracle + Midnight signatures
- ✅ **Idempotency Keys**: SHA256 hash of session + payload
- ✅ **CLI Commands**: All required flags implemented
- ✅ **Skip Sig Check**: Demo mode flag available
- ✅ **State Persistence**: JSON files in ./state/
- ✅ **Event Emission**: Structured JSON events with timestamps
- ✅ **Offline Operation**: No external dependencies
- ✅ **Deterministic Results**: Same inputs → same outputs

## Troubleshooting

### Docker Issues
```bash
# Clean rebuild
docker-compose down -v
docker system prune -f
docker-compose up --build

# Check logs
docker-compose logs hydra-control
```

### Signature Errors
- Ensure `agent_keys.json` exists (run `python signing_helper.py`)
- Check signature format (should be base64)
- Use `--skip-sig-check` for testing

### State Issues
- Delete `./state/` directory for clean start
- Check file permissions
- Ensure JSON files are valid

## Files Summary

- `hydra_control.py` - Main settlement client
- `signing_helper.py` - ED25519 key generation and signing
- `docker-compose.yml` - Standalone container setup
- `Dockerfile.hydra_control` - Python container build
- `requirements.txt` - Python dependencies
- `hydra_control_demo.sh` - Automated demo script
- `test_vectors/` - Sample payloads and keys
- `state/` - Persistent state storage (created at runtime)
