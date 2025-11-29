# Hydra Event and Message Specifications

## Overview
This document defines the event names, payloads, and message schemas for Hydra integration in the Sentinel Orchestrator Network (SON). Events are emitted to the internal message bus and can be consumed by the frontend for real-time UI updates.

## Message Bus Events

### HYDRA_REQUEST (Backend -> Hydra)
Messages sent to Hydra to trigger actions.

Schema:
```json
{
  "type": "HYDRA_REQUEST",
  "request_id": "req-uuid",
  "action": "OPEN_HEAD" | "SUBMIT_ORDER" | "CLOSE_HEAD" | "GET_STATUS",
  "session_id": "sess-001",
  "head_id": "h-0001",  // optional, for actions requiring head
  "participants": ["did:masumi:..."],  // for OPEN_HEAD
  "payload": { ... },  // order payload for SUBMIT_ORDER
  "timestamp": "2025-11-29T17:00:00Z"
}
```

### HYDRA_EVENT (Hydra -> Bus)
Events emitted by Hydra for status updates.

Schema:
```json
{
  "type": "HYDRA_EVENT",
  "event": "HEAD_OPENED" | "ORDER_COMMITTED" | "ORDER_FINALIZED" | "HEAD_CLOSED",
  "head_id": "h-0001",
  "session_id": "sess-001",
  "order_id": "o-001",  // optional
  "proof_ref": "mock-zk-12345",  // optional, for FINALIZED
  "timestamp": "2025-11-29T17:00:00Z"
}
```

## WebSocket Events (Frontend)

### hydra:head-opened
Emitted when a new Hydra head is opened.

Payload:
```json
{
  "head_id": "h-0001",
  "session_id": "sess-001",
  "participants_count": 2
}
```

### hydra:order-committed
Emitted when an order is committed to the head.

Payload:
```json
{
  "order_id": "o-001",
  "head_id": "h-0001",
  "verdict": "DANGER",
  "evidence_hash": "sha256:abc123...",
  "agent_votes_count": 1
}
```

### hydra:order-finalized
Emitted when an order is finalized (includes zk_proof_ref for frontend to block transactions).

Payload:
```json
{
  "order_id": "o-001",
  "head_id": "h-0001",
  "proof_ref": "mock-zk-12345",
  "finalized_at": "2025-11-29T17:00:00Z"
}
```

### hydra:head-closed
Emitted when a head is closed.

Payload:
```json
{
  "head_id": "h-0001",
  "session_id": "sess-001",
  "finalized_orders_count": 1
}
```

## Order Payload Schema

### Rejection Order
```json
{
  "order_type": "REJECTION",
  "verdict": "DANGER" | "SAFE",
  "evidence_hash": "sha256:...",
  "agent_votes": [
    {
      "agent_id": "did:masumi:sentinel_01",
      "vote": "DANGER" | "SAFE",
      "weight": 0.4
    }
  ],
  "zk_proof_ref": null | "string",
  "signatures": [
    {
      "agent_id": "did:masumi:sentinel_01",
      "sig": "mock-sig-base64"
    }
  ]
}
```

### Verdict Order
```json
{
  "order_type": "VERDICT",
  "verdict": "DANGER" | "SAFE",
  "evidence_hash": "sha256:...",
  "agent_votes": [
    {
      "agent_id": "did:masumi:sentinel_01",
      "vote": "DANGER" | "SAFE",
      "weight": 0.4,
      "consensus_weight": "30%"
    }
  ],
  "zk_proof_ref": "string",
  "signatures": [
    {
      "agent_id": "did:masumi:sentinel_01",
      "sig": "mock-sig-base64"
    }
  ]
}
```

## Mock Message Examples

### Sentinel Verdict Message
```json
{
  "from": "did:masumi:sentinel_01",
  "vote": "DANGER",
  "risk_score": 100,
  "flags": ["NO_REPLAY_PROTECTION", "MINORITY_FORK"],
  "evidence_hash": "sha256:abc123def456",
  "session_id": "sess-001"
}
```

### Oracle Consensus Message
```json
{
  "from": "did:masumi:oracle_01",
  "consensus_hash": "sha256:consensus123",
  "threshold_met": true,
  "session_id": "sess-001"
}
```

### Midnight ZK Proof Message
```json
{
  "from": "did:midnight:zk_01",
  "proof_ref": "zk-proof-uuid",
  "order_id": "o-001",
  "session_id": "sess-001"
}
```

## Event Flow Example

1. **Scan Initiated**: Frontend sends scan request to backend.

2. **Head Opened**:
   - Backend sends HYDRA_REQUEST with action="OPEN_HEAD"
   - Hydra emits HYDRA_EVENT with event="HEAD_OPENED"
   - Frontend receives hydra:head-opened via WebSocket

3. **Verdict Received**:
   - Sentinel sends verdict message to bus
   - Backend processes and sends HYDRA_REQUEST with action="SUBMIT_ORDER"
   - Hydra emits HYDRA_EVENT with event="ORDER_COMMITTED"
   - Frontend receives hydra:order-committed

4. **ZK Proof Attached**:
   - Midnight attaches proof
   - Order updated internally

5. **Head Closed**:
   - Backend sends HYDRA_REQUEST with action="CLOSE_HEAD"
   - Hydra emits HYDRA_EVENT with event="ORDER_FINALIZED"
   - Frontend receives hydra:order-finalized with proof_ref
   - Frontend blocks user transaction instantly

## Error Events

### hydra:error
Emitted on failures.

Payload:
```json
{
  "error_type": "HEAD_OPEN_FAILED" | "ORDER_REJECTED" | "NETWORK_ERROR",
  "message": "Human-readable error",
  "head_id": "h-0001",  // optional
  "session_id": "sess-001"
}
