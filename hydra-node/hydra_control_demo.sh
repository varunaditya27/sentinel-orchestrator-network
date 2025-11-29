#!/bin/bash

# Hydra Control Demo Script for SON Settlement Layer
# This script demonstrates the complete settlement flow

echo "=== SON Hydra Settlement Layer Demo ==="
echo "This demo shows CBOR generation, signature verification, and state management"
echo ""

# Step 1: Open a head
echo "Step 1: Opening Hydra head for session sess-001"
python hydra_control.py --open --session-id sess-001
echo ""

# Step 2: Commit a verdict (with signature verification skipped for demo)
echo "Step 2: Committing verdict order (SAFE transaction)"
python hydra_control.py --commit --session-id sess-001 --payload test_vectors/v1_safe.json --skip-sig-check
echo ""

# Step 3: Attach ZK proof
echo "Step 3: Attaching ZK proof reference"
python hydra_control.py --attach-proof --session-id sess-001 --order-id o-sess-001-0001 --proof-ref zk-proof-safe-transaction-uuid
echo ""

# Step 4: Finalize the head
echo "Step 4: Finalizing Hydra head"
python hydra_control.py --finalize --session-id sess-001
echo ""

echo "=== Demo Complete ==="
echo "Check the ./state/ directory for persisted state files"
echo "Check the output above for CBOR hex and event confirmations"
