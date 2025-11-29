# Hydra Integration Demo README

## Overview
This README provides step-by-step instructions for running the Hydra speed layer demo in mock mode for the Sentinel Orchestrator Network (SON) hackathon. The demo showcases ultra-low-latency settlement of agent verdicts using Hydra heads.

## Prerequisites
- Docker and Docker Compose installed
- Access to the SON backend and frontend (for full integration)

## Demo Setup
1. Navigate to the hydra-node directory:
   ```bash
   cd hydra-node
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Verify services are running:
   ```bash
   docker-compose ps
   ```
   Expected: hydra-node and mock-control-app running.

## Demo Script
Run the following steps to simulate the full flow:

### Step 1: Start Hydra Node
- Services are already started via docker-compose.

### Step 2: Open Hydra Head
Send a POST request to open a head for session "sess-001":
```bash
curl -X POST http://localhost:8084/hydra/open \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-001",
    "participants": ["did:masumi:sentinel_01", "did:masumi:oracle_01"],
    "metadata": {"threshold": 0.67}
  }'
```
Expected Response: `{"head_id": "h-0001"}`

### Step 3: Submit Mock Sentinel Verdict
Simulate sending a mock message to the internal message bus (or directly to mock endpoint):
```bash
curl -X POST http://localhost:8084/hydra/mock-verdict \
  -H "Content-Type: application/json" \
  -d '{
    "from": "did:masumi:sentinel_01",
    "vote": "DANGER",
    "risk_score": 100,
    "flags": ["NO_REPLAY_PROTECTION"],
    "evidence_hash": "sha256:abc123def456",
    "session_id": "sess-001"
  }'
```

### Step 4: Submit Rejection Order
```bash
curl -X POST http://localhost:8084/hydra/submit-order \
  -H "Content-Type: application/json" \
  -d '{
    "head_id": "h-0001",
    "order_payload": {
      "order_type": "REJECTION",
      "verdict": "DANGER",
      "evidence_hash": "sha256:abc123def456",
      "agent_votes": [
        {
          "agent_id": "did:masumi:sentinel_01",
          "vote": "DANGER",
          "weight": 0.5
        }
      ],
      "zk_proof_ref": null,
      "signatures": [
        {
          "agent_id": "did:masumi:sentinel_01",
          "sig": "mock-sig-base64"
        }
      ]
    }
  }'
```
Expected Response: `{"order_id": "o-001"}`

### Step 5: Simulate Midnight ZK Proof Attachment
```bash
curl -X POST http://localhost:8084/hydra/attach-zk \
  -H "Content-Type: application/json" \
  -d '{
    "head_id": "h-0001",
    "order_id": "o-001",
    "zk_proof_ref": "mock-zk-12345"
  }'
```

### Step 6: Close Head and Finalize
```bash
curl -X POST http://localhost:8084/hydra/close \
  -H "Content-Type: application/json" \
  -d '{
    "head_id": "h-0001"
  }'
```
Expected Response: `{"finalized_orders": ["o-001"], "proof_refs": ["mock-zk-12345"]}`

### Step 7: Check Status
```bash
curl http://localhost:8084/hydra/status/h-0001
```
Expected Response: `{"status": "CLOSED", "orders_count": 1}`

## Expected UI Logs
When integrated with frontend:
```
[HYDRA] HEAD_OPENED head_id=h-0001 session=sess-001
[HYDRA] ORDER_COMMITTED order_id=o-001 head_id=h-0001 verdict=DANGER evidence=sha256:abc123def456
[HYDRA] ORDER_FINALIZED order_id=o-001 proof_ref=mock-zk-12345
```

## Performance Targets (Mock Mode)
- Open head: <50ms
- Submit order: <20ms
- Close head: <100ms
- End-to-end: <200ms

## Troubleshooting
- If services fail to start, check Docker logs: `docker-compose logs`
- Ensure ports 4001 and 8084 are free
- For full integration, ensure backend message bus is configured to forward HydraAction requests

## Cleanup
```bash
docker-compose down
