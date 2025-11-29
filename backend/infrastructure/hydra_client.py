"""
=============================================================================
Sentinel Orchestrator Network (SON) - Hydra Client
=============================================================================

This module provides the WebSocket connector to the Hydra L2 consensus layer.
Hydra enables ultra-fast off-chain consensus between agents.

Responsibilities:
- Establish and maintain WebSocket connection to Hydra node
- Submit vote payloads wrapped in CBOR transaction metadata
- Handle Hydra consensus responses and confirmations
- Implement fallback to local ledger.json if Docker/Hydra fails

Connection Details:
- Default endpoint: ws://127.0.0.1:4001
- Protocol: Hydra WebSocket API

Owner: Member 3 (The Speed Demon)
Technology: Python, websockets library, CBOR encoding

Backup Plan:
If Hydra connection fails, write votes to local ledger.json file
with simulated consensus delay (sleep 0.5s).

=============================================================================
"""

import asyncio
import json
import websockets
import cbor2
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
import os
import time

logger = logging.getLogger(__name__)

class HydraClient:
    def __init__(self, ws_url: str = "ws://127.0.0.1:4001", fallback_path: str = "ledger.json"):
        self.ws_url = ws_url
        self.fallback_path = fallback_path
        self.websocket = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.session_data = {}

    async def connect(self) -> bool:
        """Establish WebSocket connection to Hydra node"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            logger.info(f"Connected to Hydra node at {self.ws_url}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Hydra node: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from Hydra node")

    async def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to Hydra node and wait for response"""
        if not self.connected:
            return await self._fallback_send(message)

        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent message to Hydra: {message}")

            # Wait for response with timeout
            response = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=30.0
            )
            response_data = json.loads(response)
            logger.info(f"Received response from Hydra: {response_data}")
            return response_data

        except Exception as e:
            logger.error(f"WebSocket communication failed: {e}")
            return await self._fallback_send(message)

    async def _fallback_send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to local ledger when Hydra is unavailable"""
        logger.warning("Using fallback ledger for consensus")

        # Simulate consensus delay
        await asyncio.sleep(0.5)

        # Create mock response
        if message.get('action') == 'open_head':
            head_id = f"fallback_head_{int(time.time())}"
            response = {
                'event': 'HEAD_OPENED',
                'head_id': head_id,
                'session_id': message.get('session_id')
            }
        elif message.get('action') == 'commit_verdict':
            order_id = f"fallback_order_{int(time.time())}"
            response = {
                'event': 'ORDER_COMMITTED',
                'order_id': order_id,
                'head_id': message.get('head_id')
            }
        elif message.get('action') == 'finalize_head':
            response = {
                'event': 'ORDER_FINALIZED',
                'head_id': message.get('head_id'),
                'receipt': {'fallback': True}
            }
        else:
            response = {'error': 'Unknown action', 'fallback': True}

        # Log to local ledger
        self._log_to_ledger(message, response)
        return response

    def _log_to_ledger(self, request: Dict[str, Any], response: Dict[str, Any]):
        """Log transaction to local ledger file"""
        try:
            entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'request': request,
                'response': response,
                'fallback': True
            }

            # Load existing ledger
            if os.path.exists(self.fallback_path):
                with open(self.fallback_path, 'r') as f:
                    ledger = json.load(f)
            else:
                ledger = []

            ledger.append(entry)

            # Save updated ledger
            with open(self.fallback_path, 'w') as f:
                json.dump(ledger, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to log to ledger: {e}")

    async def open_head(self, session_id: str, participants: List[str]) -> Dict[str, Any]:
        """Open a new Hydra head for agent consensus"""
        message = {
            'action': 'open_head',
            'session_id': session_id,
            'participants': participants,
            'timestamp': datetime.utcnow().isoformat()
        }

        response = await self.send_message(message)
        self.session_data[session_id] = {
            'head_id': response.get('head_id'),
            'participants': participants,
            'status': 'OPEN'
        }
        return response

    async def submit_verdict(self, session_id: str, verdict_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit agent verdict to Hydra head"""
        head_id = self.session_data.get(session_id, {}).get('head_id')
        if not head_id:
            raise ValueError(f"No head found for session {session_id}")

        # Create CBOR metadata
        cbor_data = self._create_verdict_cbor(verdict_payload)

        message = {
            'action': 'commit_verdict',
            'head_id': head_id,
            'session_id': session_id,
            'verdict_payload': verdict_payload,
            'cbor_metadata': cbor_data.hex(),
            'timestamp': datetime.utcnow().isoformat()
        }

        response = await self.send_message(message)

        # Store order info
        if session_id not in self.session_data:
            self.session_data[session_id] = {'orders': []}
        self.session_data[session_id]['orders'].append({
            'order_id': response.get('order_id'),
            'verdict': verdict_payload
        })

        return response

    async def finalize_head(self, session_id: str) -> Dict[str, Any]:
        """Finalize the Hydra head and settle on L1"""
        head_id = self.session_data.get(session_id, {}).get('head_id')
        if not head_id:
            raise ValueError(f"No head found for session {session_id}")

        message = {
            'action': 'finalize_head',
            'head_id': head_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        }

        response = await self.send_message(message)
        return response

    def _create_verdict_cbor(self, verdict_payload: Dict[str, Any]) -> bytes:
        """Create CBOR-encoded metadata for verdict settlement"""
        # Extract signatures
        sentinel_sig = verdict_payload.get('sentinel_sig', '')
        oracle_sig = verdict_payload.get('oracle_sig', '')
        midnight_sig = verdict_payload.get('midnight_sig', '')

        # Create metadata matching L1 Capsule NFT structure
        metadata = {
            674: {  # Policy ID for ForkShield
                "ForkShield": {
                    "verdict": verdict_payload['verdict'],
                    "evidence_hash": verdict_payload['evidence_hash'],
                    "agent_collaboration": verdict_payload.get('agent_collaboration', []),
                    "timestamp": verdict_payload.get('timestamp', datetime.utcnow().isoformat()),
                    "session_id": verdict_payload['session_id'],
                    "signatures": [
                        base64.b64decode(sentinel_sig) if sentinel_sig else b'',
                        base64.b64decode(oracle_sig) if oracle_sig else b'',
                        base64.b64decode(midnight_sig) if midnight_sig else b''
                    ]
                }
            }
        }

        return cbor2.dumps(metadata)

    async def listen_for_events(self):
        """Listen for incoming events from Hydra node"""
        if not self.connected:
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                event_type = data.get('event')

                # Call registered handlers
                if event_type in self.message_handlers:
                    await self.message_handlers[event_type](data)
                else:
                    logger.info(f"Received unhandled event: {event_type}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("Hydra WebSocket connection closed")
            self.connected = False

    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler function"""
        self.message_handlers[event_type] = handler

# Synchronous wrapper for easier backend integration
class HydraClientSync:
    def __init__(self, ws_url: str = "ws://127.0.0.1:4001"):
        self.client = HydraClient(ws_url)
        self.loop = None

    def _ensure_loop(self):
        """Ensure asyncio event loop exists"""
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def connect(self) -> bool:
        """Synchronous connect"""
        self._ensure_loop()
        return self.loop.run_until_complete(self.client.connect())

    def open_head(self, session_id: str, participants: List[str]) -> Dict[str, Any]:
        """Synchronous head opening"""
        self._ensure_loop()
        return self.loop.run_until_complete(self.client.open_head(session_id, participants))

    def submit_verdict(self, session_id: str, verdict_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous verdict submission"""
        self._ensure_loop()
        return self.loop.run_until_complete(self.client.submit_verdict(session_id, verdict_payload))

    def finalize_head(self, session_id: str) -> Dict[str, Any]:
        """Synchronous head finalization"""
        self._ensure_loop()
        return self.loop.run_until_complete(self.client.finalize_head(session_id))

    def disconnect(self):
        """Synchronous disconnect"""
        if self.loop and self.client.connected:
            self.loop.run_until_complete(self.client.disconnect())
