#!/usr/bin/env python3
"""
Simple unit tests for Hydra Control Client
Run with: python -m pytest test_hydra_control.py -v
"""

import json
import os
import tempfile
import shutil
from hydra_control import HydraControlClient

def test_cbor_generation():
    """Test CBOR metadata generation produces valid hex"""
    client = HydraControlClient()

    # Test payload
    payload = {
        "session_id": "test-123",
        "verdict": "SAFE",
        "evidence_hash": "sha256:abcdef1234567890",
        "agent_collaboration": [],
        "timestamp": "2025-01-01T00:00:00Z",
        "sentinel_sig": "dGVzdA==",
        "oracle_sig": "dGVzdA==",
        "midnight_sig": "dGVzdA=="
    }

    cbor_hex = client.generate_cbor_only(payload)

    # Should be long hex string
    assert len(cbor_hex) > 100
    assert all(c in '0123456789abcdef' for c in cbor_hex.lower())

    print(f"✓ CBOR generation test passed - length: {len(cbor_hex)}")

def test_idempotency_key():
    """Test idempotency key generation is deterministic"""
    client = HydraControlClient()

    session_id = "test-session"
    payload = {"verdict": "SAFE", "evidence": "test"}

    key1 = client._generate_idempotency_key(session_id, payload)
    key2 = client._generate_idempotency_key(session_id, payload)

    assert key1 == key2
    assert len(key1) == 16
    assert all(c in '0123456789abcdef' for c in key1)

    print(f"✓ Idempotency key test passed - key: {key1}")

def test_state_persistence():
    """Test state loading and saving"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create temporary client with custom state dir
        client = HydraControlClient()
        client.state_dir = temp_dir
        client.heads = {"test": "data"}
        client.orders = {"test": "order"}

        # Save state
        client._save_state("heads.json", client.heads)
        client._save_state("orders.json", client.orders)

        # Load state
        loaded_heads = client._load_state("heads.json")
        loaded_orders = client._load_state("orders.json")

        assert loaded_heads == {"test": "data"}
        assert loaded_orders == {"test": "order"}

        print("✓ State persistence test passed")

def test_head_operations():
    """Test head open/commit/finalize flow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        client = HydraControlClient()
        client.state_dir = temp_dir

        session_id = "test-head-ops"

        # Open head
        result = client.open_head(session_id)
        assert result["event"] == "HEAD_OPENED"
        assert result["session_id"] == session_id

        # Commit order
        payload = {
            "session_id": session_id,
            "verdict": "SAFE",
            "evidence_hash": "sha256:test",
            "agent_collaboration": [],
            "timestamp": "2025-01-01T00:00:00Z",
            "sentinel_sig": "dGVzdA==",
            "oracle_sig": "dGVzdA==",
            "midnight_sig": "dGVzdA=="
        }

        result = client.commit_verdict(session_id, payload, skip_sig_check=True)
        assert result["event"] == "ORDER_COMMITTED"
        assert result["session_id"] == session_id
        assert "cbor_hex" in result
        assert "idempotency_key" in result

        # Attach proof
        order_id = result["order_id"]
        result = client.attach_proof(session_id, order_id, "test-proof")
        assert result["event"] == "PROOF_ATTACHED"
        assert result["order_id"] == order_id

        # Finalize
        result = client.finalize_head(session_id)
        assert result["event"] == "ORDER_FINALIZED"
        assert result["session_id"] == session_id
        assert order_id in result["finalized_orders"]

        print("✓ Head operations test passed")

if __name__ == "__main__":
    print("Running Hydra Control unit tests...")

    try:
        test_cbor_generation()
        test_idempotency_key()
        test_state_persistence()
        test_head_operations()

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
