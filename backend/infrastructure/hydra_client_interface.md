# Hydra Client Interface Documentation

## Overview
The `hydra_client` module provides an interface for interacting with the Hydra speed layer in the Sentinel Orchestrator Network (SON). It handles opening Hydra heads, submitting orders, and managing the lifecycle of off-chain consensus sessions.

## Function Signatures

### open_head(session_id, participants, metadata)
- **Purpose**: Initializes a new Hydra head for a user session/scan.
- **Parameters**:
  - `session_id`: String, unique identifier for the session (e.g., "sess-001")
  - `participants`: Array of strings, DID identifiers (e.g., ["did:masumi:sentinel_01", "did:masumi:oracle_01"])
  - `metadata`: Object with session metadata (e.g., {"consensus_threshold": 0.67, "timeout_ms": 5000})
- **Returns**: Promise resolving to head_id (string, e.g., "h-0001")
- **Error Semantics**: Throws `HydraError` if head cannot be opened (e.g., invalid participants)
- **Retry Logic**: Idempotent; retries on network failure with exponential backoff

### submit_order(head_id, order_payload)
- **Purpose**: Submits a rejection or verdict order to the Hydra head.
- **Parameters**:
  - `head_id`: String, ID of the open head
  - `order_payload`: Object with order details (see schema below)
- **Returns**: Promise resolving to order_id (string, e.g., "o-001")
- **Error Semantics**: Throws `OrderRejectedError` if order invalid; `HeadClosedError` if head not open
- **Retry Logic**: Idempotent with idempotency key based on head_id + order_payload hash

### close_head(head_id)
- **Purpose**: Closes the Hydra head and finalizes all pending orders.
- **Parameters**:
  - `head_id`: String, ID of the head to close
- **Returns**: Promise resolving to finalization summary object
- **Error Semantics**: Throws `HeadNotFoundError` if head doesn't exist
- **Retry Logic**: Best-effort; may succeed partially

### get_head_status(head_id)
- **Purpose**: Retrieves current status of a Hydra head.
- **Parameters**:
  - `head_id`: String
- **Returns**: Promise resolving to status object (e.g., {"status": "OPEN", "orders_count": 3})
- **Error Semantics**: Throws `HeadNotFoundError`
- **Retry Logic**: Read-only, safe to retry

### finalize_order(head_id, order_id)
- **Purpose**: Manually finalize a specific order (rarely used; usually done on close).
- **Parameters**:
  - `head_id`: String
  - `order_id`: String
- **Returns**: Promise resolving to proof_ref (string)
- **Error Semantics**: Throws `OrderNotFoundError`
- **Retry Logic**: Idempotent

## Order Payload Schema
```json
{
  "order_type": "REJECTION" | "VERDICT",
  "verdict": "DANGER" | "SAFE",
  "evidence_hash": "sha256:...",
  "agent_votes": [
    {
      "agent_id": "did:masumi:sentinel_01",
      "vote": "DANGER",
      "weight": 0.4
    }
  ],
  "zk_proof_ref": null | "mock-zk-12345",
  "signatures": [
    {
      "agent_id": "did:masumi:sentinel_01",
      "sig": "mock-sig-base64"
    }
  ]
}
```

## Example Requests/Responses

### Open Head
Request:
```json
{
  "session_id": "sess-001",
  "participants": ["did:masumi:sentinel_01", "did:masumi:oracle_01"],
  "metadata": {"threshold": 0.67}
}
```
Response: `"h-0001"`

### Submit Order
Request:
```json
{
  "head_id": "h-0001",
  "order_payload": {
    "order_type": "REJECTION",
    "verdict": "DANGER",
    "evidence_hash": "sha256:abc123...",
    "agent_votes": [{"agent_id": "did:masumi:sentinel_01", "vote": "DANGER", "weight": 0.5}],
    "zk_proof_ref": "mock-zk-12345",
    "signatures": [{"agent_id": "did:masumi:sentinel_01", "sig": "mock-sig"}]
  }
}
```
Response: `"o-001"`

## Error Semantics
- All functions throw typed errors extending `HydraClientError`
- Network errors trigger automatic retries (up to 3 attempts)
- Idempotency ensures no duplicate operations on retry
