import json
import logging
import asyncio
import websockets
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class HydraClient:
    """
    Client for interacting with a real Hydra Node via WebSocket.
    Connects to the Hydra API (default port 4001).
    """

    def __init__(self, host: str = "localhost", port: int = 4001):
        self.uri = f"ws://{host}:{port}"
        self.connection = None
        self.lock = asyncio.Lock()

    async def connect(self):
        """Establish WebSocket connection to Hydra Node."""
        try:
            self.connection = await websockets.connect(self.uri)
            logger.info(f"✅ Connected to Hydra Node at {self.uri}")
            
            # Start a background task to keep the connection alive/listen
            # For this simple implementation, we'll read responses on demand or have a listener
            # But for request/response patterns, we might need a correlation ID system
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Hydra Node: {e}")
            self.connection = None

    async def close(self):
        """Close the connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Hydra Node connection closed")

    async def send_request(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a JSON message to the Hydra Node and wait for a response.
        Note: Hydra API is event-based. This is a simplified request/response wrapper.
        """
        if not self.connection:
            await self.connect()
            if not self.connection:
                return None

        async with self.lock:
            try:
                await self.connection.send(json.dumps(message))
                logger.debug(f"Sent to Hydra: {message}")
                
                # In a real scenario, we'd need to match the response to the request.
                # Hydra sends "CommandFailed" or specific events like "TxValid".
                # For now, we'll listen for the next relevant message.
                
                # Wait for a response (timeout 1s)
                response = await asyncio.wait_for(self.connection.recv(), timeout=1.0)
                data = json.loads(response)
                logger.debug(f"Received from Hydra: {data}")
                return data
                
            except asyncio.TimeoutError:
                logger.warning("Hydra request timed out")
                return None
            except Exception as e:
                logger.error(f"Error communicating with Hydra: {e}")
                return None

    async def validate_tx(self, tx_cbor: str) -> Dict[str, Any]:
        """
        Validate a transaction by submitting it to the Hydra Head.
        Uses the 'NewTx' input.
        """
        # Construct NewTx message
        # https://hydra.family/head-protocol/api-reference#operation-publish-new-transaction
        message = {
            "tag": "NewTx",
            "transaction": {
                "type": "Hex",
                "cbor": tx_cbor
            }
        }
        
        # Send and wait for response
        # Note: Hydra broadcasts 'TxValid' or 'TxInvalid' to all clients.
        # We are simplifying by assuming the next message is the response for us.
        # In production, we'd need a proper event loop.
        
        response = await self.send_request(message)
        
        if not response:
            return {"valid": False, "reason": "No response from Hydra Node"}
            
        tag = response.get("tag")
        
        if tag == "TxValid":
            return {
                "valid": True,
                "tx_id": response.get("transactionId"),
                "reason": "Validated by Hydra Head"
            }
        elif tag == "TxInvalid":
            return {
                "valid": False,
                "reason": f"Hydra Rejected: {response.get('validationError', {}).get('reason', 'Unknown')}"
            }
        elif tag == "CommandFailed":
             return {
                "valid": False,
                "reason": f"Command Failed: {response.get('clientInput', {}).get('tag')} - {response.get('reason')}"
            }
            
        return {"valid": False, "reason": f"Unexpected response: {tag}"}
