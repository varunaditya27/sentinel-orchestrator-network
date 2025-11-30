#!/bin/bash

echo "========================================"
echo "Testing Sentinel Orchestrator Network APIs"
echo "========================================"
echo ""

# 1. System Status
echo "[1] Testing /api/v1/system/status..."
curl -s http://localhost:8000/api/v1/system/status
echo ""
echo "----------------------------------------"

# 2. Agents Info
echo "[2] Testing /api/v1/agents/info..."
curl -s http://localhost:8000/api/v1/agents/info
echo ""
echo "----------------------------------------"

# 3. Treasury Risk Report (Current)
echo "[3] Testing /api/v1/treasury/risk/current..."
curl -s http://localhost:8000/api/v1/treasury/risk/current
echo ""
echo "----------------------------------------"

# 4. Treasury Analysis (High Risk Proposal)
echo "[4] Testing /api/v1/treasury/analyze (High Risk)..."
curl -s -X POST http://localhost:8000/api/v1/treasury/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "gov_action_test_high",
    "amount": 60000000000000,
    "proposer_id": "stake_test_new_wallet",
    "metadata": {
        "title": "Give me money",
        "abstract": "I need funds.",
        "rationale": "Trust me."
    }
  }'
echo ""
echo "----------------------------------------"

# 5. Treasury Analysis (Low Risk Proposal)
echo "[5] Testing /api/v1/treasury/analyze (Low Risk)..."
curl -s -X POST http://localhost:8000/api/v1/treasury/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "gov_action_test_low",
    "amount": 5000000000,
    "proposer_id": "stake1u8y...",
    "metadata": {
        "title": "Valid Infrastructure Proposal",
        "abstract": "Detailed infrastructure upgrade plan with milestones.",
        "rationale": "Necessary for network scaling. See attached PDF for full breakdown."
    }
  }'
echo ""
echo "----------------------------------------"

# 6. Scan History
echo "[6] Testing /api/v1/scans/history..."
curl -s http://localhost:8000/api/v1/scans/history
echo ""
echo "========================================"
echo "Tests Completed"
echo "========================================"
