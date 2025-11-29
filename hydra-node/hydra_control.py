#!/usr/bin/env python3
"""
Hydra Control Client for SON Settlement Layer
Standalone implementation with local state management and CBOR generation.

Based on Hydra Head Protocol and ForkShield L1 Capsule NFT structure.
"""

import json
import os
import hashlib
import base64
import cbor2
from datetime import datetime
from typing import Dict, Any, Optional, List
import argparse
import nacl.signing
import nacl.encoding
from flask import Flask, request, jsonify

# Configuration
POLICY_ID = "674"  # ForkShield policy ID
STATE_DIR = "./state"
TEST_VECTORS_DIR = "./test_vectors"

class HydraControlClient:
    def __init__(self):
        self.state_dir = STATE_DIR
        self.test_vectors_dir = TEST_VECTORS_DIR
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.test_vectors_dir, exist_ok=True)

        # Load or initialize state
        self.heads = self._load_state("heads.json")
        self.orders = self._load_state("orders.json")

    def _load_state(self, filename: str) -> Dict[str, Any]:
        """Load state from JSON file"""
        filepath = os.path.join(self.state_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def _save_state(self, filename: str, data: Dict[str, Any]):
        """Save state to JSON file"""
        filepath = os.path.join(self.state_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def _generate_idempotency_key(self, session_id: str, payload: Dict[str, Any]) -> str:
        """Generate deterministic idempotency key"""
        payload_str = json.dumps(payload, sort_keys=True)
        combined = f"{session_id}:{payload_str}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _verify_signature(self, message: bytes, signature_b64: str, public_key_b64: str) -> bool:
        """Verify ED25519 signature using PyNaCl"""
        try:
            # Decode signature and public key
            signature = base64.b64decode(signature_b64)
            public_key = base64.b64decode(public_key_b64)

            # Create verifying key
            verify_key = nacl.signing.VerifyKey(public_key, encoder=nacl.encoding.RawEncoder)

            # Verify signature
            verify_key.verify(message, signature, encoder=nacl.encoding.RawEncoder)
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False

    def _create_cbor_metadata(self, verdict_payload: Dict[str, Any]) -> bytes:
        """Create CBOR-encoded metadata for ForkShield L1 Capsule NFT structure"""
        # Build the ForkShield capsule structure
        forkshield_data = {
            "verdict": verdict_payload['verdict'],
            "evidence_root": verdict_payload.get('evidence_hash', ''),
            "agent_collaboration": verdict_payload.get('agent_collaboration', []),
            "cost": "1.0 ADA",
            "signatures": [
                verdict_payload.get('sentinel_sig', ''),
                verdict_payload.get('oracle_sig', ''),
                verdict_payload.get('midnight_sig', '')
            ],
            "timestamp": verdict_payload.get('timestamp', datetime.utcnow().isoformat()),
            "session_id": verdict_payload['session_id']
        }

        # Create the full metadata structure
        metadata = {
            721: {  # CIP-25 NFT metadata label
                POLICY_ID: {
                    "ForkShield": forkshield_data
                }
            }
        }

        # Encode to CBOR bytes
        cbor_data = cbor2.dumps(metadata)
        return cbor_data

    def open_head(self, session_id: str) -> Dict[str, Any]:
        """Open a new Hydra head for the session"""
        if session_id in self.heads:
            raise ValueError(f"Head already exists for session {session_id}")

        # Generate deterministic head ID
        head_id = f"h-{session_id}"

        head_data = {
            'head_id': head_id,
            'session_id': session_id,
            'status': 'OPEN',
            'participants': ['sentinel', 'oracle', 'midnight'],
            'orders': [],
            'created_at': datetime.utcnow().isoformat(),
            'finalized_at': None
        }

        self.heads[session_id] = head_data
        self._save_state("heads.json", self.heads)

        result = {
            'event': 'HEAD_OPENED',
            'head_id': head_id,
            'session_id': session_id,
            'timestamp': head_data['created_at']
        }

        print(json.dumps(result, indent=2))
        return result

    def commit_verdict(self, session_id: str, verdict_payload: Dict[str, Any], skip_sig_check: bool = False) -> Dict[str, Any]:
        """Commit a verdict order to the Hydra head"""
        if session_id not in self.heads:
            raise ValueError(f"No head found for session {session_id}")

        head = self.heads[session_id]
        if head['status'] != 'OPEN':
            raise ValueError(f"Head {head['head_id']} is not open")

        # Verify signatures unless skipped
        if not skip_sig_check:
            # Load agent keys
            keys_file = os.path.join(self.test_vectors_dir, "agent_keys.json")
            if not os.path.exists(keys_file):
                raise ValueError("agent_keys.json not found. Run signing_helper.py to generate keys.")

            with open(keys_file, 'r') as f:
                agent_keys = json.load(f)

            # Load canonical message to verify against
            msg_file = os.path.join(self.test_vectors_dir, "message_to_sign.json")
            if not os.path.exists(msg_file):
                raise ValueError("message_to_sign.json not found.")

            with open(msg_file, 'r') as f:
                canonical_msg = json.load(f)

            # Canonical JSON for signing (sorted keys)
            message_bytes = json.dumps(canonical_msg, sort_keys=True, separators=(',', ':')).encode()

            # Verify each signature
            signatures = [
                (verdict_payload.get('sentinel_sig', ''), agent_keys['sentinel']['public_key'], 'sentinel'),
                (verdict_payload.get('oracle_sig', ''), agent_keys['oracle']['public_key'], 'oracle'),
                (verdict_payload.get('midnight_sig', ''), agent_keys['midnight']['public_key'], 'midnight')
            ]

            for sig_b64, pub_key_b64, agent in signatures:
                if not sig_b64:
                    raise ValueError(f"Missing signature for {agent}")
                if not self._verify_signature(message_bytes, sig_b64, pub_key_b64):
                    raise ValueError(f"Invalid signature for {agent}")

        # Generate idempotency key
        idempotency_key = self._generate_idempotency_key(session_id, verdict_payload)

        # Check for duplicate orders
        existing_order_ids = [order['order_id'] for order in head['orders']]
        order_id = f"o-{session_id}-{len(existing_order_ids) + 1:04d}"

        # Create CBOR metadata
        cbor_metadata = self._create_cbor_metadata(verdict_payload)

        order_data = {
            'order_id': order_id,
            'session_id': session_id,
            'head_id': head['head_id'],
            'verdict_payload': verdict_payload,
            'cbor_hex': cbor_metadata.hex(),
            'idempotency_key': idempotency_key,
            'status': 'COMMITTED',
            'proof_ref': None,
            'created_at': datetime.utcnow().isoformat()
        }

        # Store order
        order_key = f"{session_id}:{order_id}"
        self.orders[order_key] = order_data
        head['orders'].append(order_id)

        self._save_state("orders.json", self.orders)
        self._save_state("heads.json", self.heads)

        result = {
            'event': 'ORDER_COMMITTED',
            'order_id': order_id,
            'head_id': head['head_id'],
            'session_id': session_id,
            'cbor_hex': cbor_metadata.hex(),
            'idempotency_key': idempotency_key,
            'timestamp': order_data['created_at']
        }

        print(json.dumps(result, indent=2))
        return result

    def attach_proof(self, session_id: str, order_id: str, proof_ref: str) -> Dict[str, Any]:
        """Attach ZK proof reference to an order"""
        order_key = f"{session_id}:{order_id}"
        if order_key not in self.orders:
            raise ValueError(f"Order {order_id} not found for session {session_id}")

        order = self.orders[order_key]
        order['proof_ref'] = proof_ref
        order['proof_attached_at'] = datetime.utcnow().isoformat()

        self._save_state("orders.json", self.orders)

        result = {
            'event': 'PROOF_ATTACHED',
            'order_id': order_id,
            'session_id': session_id,
            'proof_ref': proof_ref,
            'timestamp': order['proof_attached_at']
        }

        print(json.dumps(result, indent=2))
        return result

    def finalize_head(self, session_id: str) -> Dict[str, Any]:
        """Close the Hydra head and finalize all orders"""
        if session_id not in self.heads:
            raise ValueError(f"No head found for session {session_id}")

        head = self.heads[session_id]
        if head['status'] != 'OPEN':
            raise ValueError(f"Head {head['head_id']} is not open")

        # Get all orders for this session
        session_orders = [self.orders[f"{session_id}:{order_id}"] for order_id in head['orders']]

        # Check that all orders have proofs attached
        for order in session_orders:
            if not order.get('proof_ref'):
                raise ValueError(f"Order {order['order_id']} missing proof attachment")

        finalized_at = datetime.utcnow().isoformat()
        head['status'] = 'FINALIZED'
        head['finalized_at'] = finalized_at

        # Update all orders
        for order in session_orders:
            order['status'] = 'FINALIZED'
            order['finalized_at'] = finalized_at

        self._save_state("heads.json", self.heads)
        self._save_state("orders.json", self.orders)

        result = {
            'event': 'ORDER_FINALIZED',
            'head_id': head['head_id'],
            'session_id': session_id,
            'finalized_orders': head['orders'],
            'proof_refs': [order.get('proof_ref') for order in session_orders],
            'timestamp': finalized_at
        }

        print(json.dumps(result, indent=2))
        return result

    def generate_cbor_only(self, verdict_payload: Dict[str, Any]) -> str:
        """Generate and return CBOR hex without creating orders"""
        cbor_metadata = self._create_cbor_metadata(verdict_payload)
        cbor_hex = cbor_metadata.hex()
        print(f"CBOR Hex: {cbor_hex}")
        return cbor_hex

# Global client instance
client = HydraControlClient()

# Flask app for HTTP server mode
app = Flask(__name__)

@app.route('/open', methods=['POST'])
def api_open_head():
    data = request.get_json()
    try:
        result = client.open_head(data['session_id'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/commit', methods=['POST'])
def api_commit_verdict():
    data = request.get_json()
    try:
        skip_check = data.get('skip_sig_check', False)
        result = client.commit_verdict(data['session_id'], data['verdict_payload'], skip_check)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/attach-proof', methods=['POST'])
def api_attach_proof():
    data = request.get_json()
    try:
        result = client.attach_proof(data['session_id'], data['order_id'], data['proof_ref'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/finalize', methods=['POST'])
def api_finalize_head():
    data = request.get_json()
    try:
        result = client.finalize_head(data['session_id'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/cbor-only', methods=['POST'])
def api_cbor_only():
    data = request.get_json()
    try:
        cbor_hex = client.generate_cbor_only(data['verdict_payload'])
        return jsonify({'cbor_hex': cbor_hex})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def main():
    parser = argparse.ArgumentParser(description='Hydra Control Client for SON Settlement')
    parser.add_argument('--server', action='store_true', help='Run as HTTP server')
    parser.add_argument('--open', action='store_true', help='Open a head')
    parser.add_argument('--commit', action='store_true', help='Commit a verdict')
    parser.add_argument('--attach-proof', action='store_true', help='Attach ZK proof')
    parser.add_argument('--finalize', action='store_true', help='Finalize head')
    parser.add_argument('--cbor-only', action='store_true', help='Generate CBOR only')
    parser.add_argument('--session-id', required=False, help='Session ID')
    parser.add_argument('--payload', help='Path to verdict payload JSON file')
    parser.add_argument('--order-id', help='Order ID for proof attachment')
    parser.add_argument('--proof-ref', help='ZK proof reference')
    parser.add_argument('--skip-sig-check', action='store_true', help='Skip signature verification')

    args = parser.parse_args()

    if args.server:
        port = int(os.environ.get('CONTROL_PORT', 8085))
        app.run(host='0.0.0.0', port=port, debug=True)
    elif args.open:
        if not args.session_id:
            parser.error("--session-id required for --open")
        client.open_head(args.session_id)
    elif args.commit:
        if not args.session_id or not args.payload:
            parser.error("--session-id and --payload required for --commit")
        with open(args.payload, 'r') as f:
            payload = json.load(f)
        client.commit_verdict(args.session_id, payload, args.skip_sig_check)
    elif args.attach_proof:
        if not args.session_id or not args.order_id or not args.proof_ref:
            parser.error("--session-id, --order-id, and --proof-ref required for --attach-proof")
        client.attach_proof(args.session_id, args.order_id, args.proof_ref)
    elif args.finalize:
        if not args.session_id:
            parser.error("--session-id required for --finalize")
        client.finalize_head(args.session_id)
    elif args.cbor_only:
        if not args.payload:
            parser.error("--payload required for --cbor-only")
        with open(args.payload, 'r') as f:
            payload = json.load(f)
        client.generate_cbor_only(payload)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
