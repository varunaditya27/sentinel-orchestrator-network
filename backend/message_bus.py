import logging
import json
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageBus:
    """
    Inter-agent message bus for Sentinel Orchestrator Network (SON).
    
    Features:
    - Agent registry with DID → Ed25519 public key mapping
    - Cryptographic signature verification (IACP/2.0 protocol)
    - WebSocket broadcasting for real-time client updates
    - Message envelope validation and routing
    """
    
    def __init__(self):
        # Registry mapping Agent DIDs (strings) to Ed25519 Public Keys (base64 strings)
        self.registry: Dict[str, str] = {}
        
        # Active WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Message history (optional, for debugging)
        self.message_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
        logger.info("MessageBus initialized")

    # =========================================================================
    # CONNECTION MANAGEMENT
    # =========================================================================

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Unregister a closed WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    # =========================================================================
    # AGENT REGISTRATION
    # =========================================================================

    def register_agent(self, did: str, public_key_b64: str):
        """
        Register an agent with the message bus.
        
        Args:
            did: Agent DID (e.g., "did:masumi:sentinel_01")
            public_key_b64: Base64-encoded Ed25519 public key
        """
        self.registry[did] = public_key_b64
        logger.info(f"✅ Registered agent: {did}")

    def unregister_agent(self, did: str):
        """Unregister an agent from the message bus."""
        if did in self.registry:
            del self.registry[did]
            logger.info(f"Unregistered agent: {did}")

    def get_registered_agents(self) -> List[str]:
        """Get list of all registered agent DIDs."""
        return list(self.registry.keys())

    # =========================================================================
    # MESSAGE PUBLISHING & BROADCASTING
    # =========================================================================

    async def publish(self, envelope: Dict[str, Any]) -> bool:
        """
        Verify and publish a signed message envelope.
        
        Expected envelope structure (IACP/2.0):
        {
            "protocol": "IACP/2.0",
            "type": "MESSAGE_TYPE",
            "from_did": "did:...",
            "to_did": "did:..." (optional),
            "payload": { ... },
            "signature": "base64_string",
            "timestamp": "ISO8601"
        }
        
        Returns:
            bool: True if published successfully, False if verification failed
        """
        sender_did = envelope.get("from_did")
        payload = envelope.get("payload")
        signature_b64 = envelope.get("signature")
        message_type = envelope.get("type", "UNKNOWN")

        # Validate envelope structure
        if not sender_did:
            logger.warning("❌ Dropped message: Missing 'from_did'")
            return False

        if sender_did not in self.registry:
            logger.warning(f"❌ Dropped message: Unknown sender DID {sender_did}")
            return False

        if not signature_b64:
            logger.warning("❌ Dropped message: Missing 'signature'")
            return False

        # Verify the signature
        public_key_b64 = self.registry[sender_did]
        
        if not await self._verify_signature(
            envelope, public_key_b64, sender_did
        ):
            logger.error(f"❌ SECURITY ALERT: Invalid signature from {sender_did}. Dropping message.")
            return False

        # Signature valid - broadcast the message
        logger.info(f"✅ Verified {message_type} from {sender_did}. Broadcasting to {len(self.active_connections)} clients...")
        
        # Store in history
        self._store_message(envelope)
        
        # Broadcast to all connected clients
        await self.broadcast(envelope)
        
        return True

    async def _verify_signature(
        self,
        envelope: Dict[str, Any],
        public_key_b64: str,
        sender_did: str
    ) -> bool:
        """
        Verify the Ed25519 signature of an envelope.
        
        Args:
            envelope: The signed message envelope
            public_key_b64: Base64-encoded public key
            sender_did: The sender's DID (for logging)
            
        Returns:
            bool: True if signature is valid
        """
        try:
            signature_b64 = envelope.get("signature")
            
            # Reconstruct the original message (exclude signature)
            message = {k: v for k, v in envelope.items() if k != "signature"}
            
            # Serialize deterministically
            message_bytes = json.dumps(
                message, sort_keys=True, separators=(',', ':')
            ).encode('utf-8')
            
            # Decode signature (try hex first, then base64)
            signature_bytes = None
            try:
                if len(signature_b64) < 200:
                    signature_bytes = bytes.fromhex(signature_b64)
            except ValueError:
                pass
            
            if not signature_bytes:
                signature_bytes = __import__('base64').b64decode(signature_b64)
            
            # Verify
            public_key_bytes = __import__('base64').b64decode(public_key_b64)
            verify_key = VerifyKey(public_key_bytes)
            verify_key.verify(message_bytes, signature_bytes)
            
            return True

        except BadSignatureError:
            logger.error(f"❌ Signature verification failed for {sender_did}")
            return False
        except Exception as e:
            logger.error(f"❌ Error verifying signature: {str(e)}")
            return False

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected WebSocket clients.
        
        Args:
            message: The message envelope to broadcast
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return

        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected_clients.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected_clients:
            self.disconnect(connection)

    # =========================================================================
    # MESSAGE HISTORY & UTILITY
    # =========================================================================

    def _store_message(self, envelope: Dict[str, Any]):
        """Store message in history for debugging."""
        message_record = {
            "from_did": envelope.get("from_did"),
            "type": envelope.get("type"),
            "timestamp": envelope.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "payload_keys": list(envelope.get("payload", {}).keys())
        }
        
        self.message_history.append(message_record)
        
        # Keep history size bounded
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]

    def get_message_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent message history."""
        return self.message_history[-limit:]

    # =========================================================================
    # LEGACY METHODS (for backward compatibility)
    # =========================================================================

    async def subscribe(self, websocket: WebSocket):
        """
        Legacy endpoint for Frontend to listen to events.
        Kept for backward compatibility.
        """
        await self.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.disconnect(websocket)

