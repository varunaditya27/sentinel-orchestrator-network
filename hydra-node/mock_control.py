#!/usr/bin/env python3
"""
Mock Control App for Hydra Speed Layer Demo
Provides HTTP endpoints for testing Hydra integration in mock mode.
"""

import json
import time
import uuid
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Mock data storage
heads = {}
orders = {}
next_head_id = 1
next_order_id = 1

@app.route('/hydra/open', methods=['POST'])
def open_head():
    """Open a new Hydra head"""
    data = request.get_json()
    global next_head_id

    head_id = f"h-{next_head_id:04d}"
    next_head_id += 1

    heads[head_id] = {
        'session_id': data['session_id'],
        'participants': data['participants'],
        'metadata': data.get('metadata', {}),
        'status': 'OPEN',
        'orders': [],
        'created_at': datetime.utcnow().isoformat()
    }

    # Simulate latency
    time.sleep(0.012)  # 12ms average

    print(f"[HYDRA] HEAD_OPENED head_id={head_id} session={data['session_id']}")
    return jsonify({'head_id': head_id})

@app.route('/hydra/submit-order', methods=['POST'])
def submit_order():
    """Submit an order to a head"""
    data = request.get_json()
    head_id = data['head_id']
    global next_order_id

    if head_id not in heads:
        return jsonify({'error': 'Head not found'}), 404

    if heads[head_id]['status'] != 'OPEN':
        return jsonify({'error': 'Head not open'}), 400

    order_id = f"o-{next_order_id:04d}"
    next_order_id += 1

    order = {
        'order_id': order_id,
        'head_id': head_id,
        'payload': data['order_payload'],
        'status': 'COMMITTED',
        'zk_proof_ref': None,
        'created_at': datetime.utcnow().isoformat()
    }

    orders[order_id] = order
    heads[head_id]['orders'].append(order_id)

    # Simulate latency
    time.sleep(0.005)  # 5ms average

    verdict = data['order_payload']['verdict']
    evidence = data['order_payload']['evidence_hash']
    print(f"[HYDRA] ORDER_COMMITTED order_id={order_id} head_id={head_id} verdict={verdict} evidence={evidence}")
    return jsonify({'order_id': order_id})

@app.route('/hydra/attach-zk', methods=['POST'])
def attach_zk():
    """Attach ZK proof to an order"""
    data = request.get_json()
    order_id = data['order_id']

    if order_id not in orders:
        return jsonify({'error': 'Order not found'}), 404

    orders[order_id]['zk_proof_ref'] = data['zk_proof_ref']

    # Simulate latency
    time.sleep(0.001)  # 1ms

    return jsonify({'updated': True})

@app.route('/hydra/close', methods=['POST'])
def close_head():
    """Close a head and finalize orders"""
    data = request.get_json()
    head_id = data['head_id']

    if head_id not in heads:
        return jsonify({'error': 'Head not found'}), 404

    heads[head_id]['status'] = 'CLOSED'
    finalized_orders = heads[head_id]['orders']
    proof_refs = []

    for order_id in finalized_orders:
        if order_id in orders:
            proof_ref = orders[order_id].get('zk_proof_ref', 'mock-zk-default')
            proof_refs.append(proof_ref)
            print(f"[HYDRA] ORDER_FINALIZED order_id={order_id} proof_ref={proof_ref}")

    # Simulate latency
    time.sleep(0.025)  # 25ms average

    return jsonify({
        'finalized_orders': finalized_orders,
        'proof_refs': proof_refs
    })

@app.route('/hydra/status/<head_id>', methods=['GET'])
def get_status(head_id):
    """Get head status"""
    if head_id not in heads:
        return jsonify({'error': 'Head not found'}), 404

    head = heads[head_id]
    return jsonify({
        'status': head['status'],
        'orders_count': len(head['orders'])
    })

@app.route('/hydra/mock-verdict', methods=['POST'])
def mock_verdict():
    """Mock endpoint for sentinel verdicts"""
    data = request.get_json()
    # In real implementation, this would trigger order submission
    return jsonify({'processed': True, 'triggered_order': True})

if __name__ == '__main__':
    port = int(__import__('os').environ.get('MOCK_PORT', 8084))
    app.run(host='0.0.0.0', port=port, debug=True)
