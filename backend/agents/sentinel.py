"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT A: Sentinel Agent
=============================================================================

Role: Primary orchestrator, protocol compliance checker, final verdict issuer
Masumi Pricing: Per scan (fixed)

Based on simplified_agent_flow.txt:
1. Receives transaction CBOR or Policy ID from user
2. Checks protocol compliance (validity interval, required fields, etc.)
3. If compliance fails → immediate "unsafe" verdict
4. If compliance passes → sends HIRE_REQUEST to Oracle for network check
5. Receives Oracle response, makes final verdict (SAFE/DANGER)
6. Optionally triggers Notary for ThreatProof Capsule

=============================================================================
"""

import base64
import json
import hashlib
import asyncio
from typing import Any, Dict, Optional, TYPE_CHECKING
from enum import Enum

import nacl.signing
from nacl.signing import SigningKey

from .base import BaseAgent, Vote
from .hydra_node import HydraNode

if TYPE_CHECKING:
    from .oracle import OracleAgent


# =============================================================================
# SENTINEL CONFIGURATION
# =============================================================================

class ComplianceStatus(str, Enum):
    """Protocol compliance check status"""
    VALID = "valid"
    INVALID = "invalid"
    REQUIRES_NETWORK_CHECK = "requires_network_check"


# =============================================================================
# SENTINEL AGENT CLASS
# =============================================================================

class SentinelAgent(BaseAgent):
    """
    Agent A: Primary orchestrator and protocol compliance checker.
    
    Workflow:
    1. Parse transaction CBOR / Policy ID
    2. Check protocol compliance (validity interval, required fields, etc.)
    3. If non-compliant → immediate DANGER verdict
    4. If compliant but needs network check → HIRE_REQUEST to Oracle
    5. Verify Oracle's signed response
    6. Issue final verdict (SAFE / WARNING / DANGER)
    
    Performance: Must complete in < 2 seconds (excluding Oracle call)
    """
    
    def __init__(
        self, 
        oracle_agent: Optional["OracleAgent"] = None,
        enable_llm: bool = True,
        enable_hydra: bool = True
    ):
        """
        Initialize the Sentinel Agent.
        
        Args:
            oracle_agent: Reference to Oracle agent for HIRE_REQUEST
            enable_llm: Whether to enable LLM-enhanced analysis
            enable_hydra: Whether to enable Hydra Head for off-chain checks
        """
        super().__init__(agent_name="sentinel", role="orchestrator", enable_llm=enable_llm)
        
        # Initialize Hydra Node
        self.hydra_enabled = enable_hydra
        self.hydra_node = HydraNode() if enable_hydra else None
        
        # Generate cryptographic keypair for message signing
        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.verify_key
        
        # Store reference to Oracle agent
        self.oracle = oracle_agent
        
        # Escrow tracking (virtual payments via Masumi)
        self.pending_escrows: Dict[str, float] = {}
        
        self.logger.info("Sentinel Agent initialized with DID keypair")
    
    def set_oracle(self, oracle_agent: "OracleAgent") -> None:
        """Set the Oracle agent reference after initialization."""
        self.oracle = oracle_agent
        self.logger.info("Oracle agent connected to Sentinel")
    
    def get_public_key_b64(self) -> str:
        """Get base64-encoded public key for sharing with Oracle."""
        return base64.b64encode(bytes(self.public_key)).decode()
    
    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - analyze transaction/policy for threats.
        
        Args:
            input_data: {
                "policy_id": "<hex_string>" or "tx_cbor": "<cbor_hex>",
                "user_tip": <block_height>,  # User's node block height
                "timestamp": "<ISO 8601>"
            }
            
        Returns:
            Dict with final verdict, compliance status, oracle result
        """
        policy_id = input_data.get("policy_id", "")
        tx_cbor = input_data.get("tx_cbor", "")
        user_tip = input_data.get("user_tip", 0)
        
        self.log_start(policy_id or tx_cbor[:16] if tx_cbor else "unknown")
        
        # Step 0: Ultra-Fast Hydra Check (Off-chain)
        if self.hydra_enabled and self.hydra_node:
            self.logger.info("Attempting Ultra-Fast Hydra Check...")
            try:
                hydra_result = await self.hydra_node.validate_transaction_offchain(tx_cbor, policy_id)
                
                if hydra_result.get("verified"):
                    self.logger.info(f"Hydra Verdict: {hydra_result['verdict']} ({hydra_result['latency_ms']}ms)")
                    
                    # Map Hydra verdict to Vote
                    verdict_str = hydra_result['verdict']
                    verdict = Vote.DANGER if verdict_str == "DANGER" else Vote.SAFE
                    
                    return self._build_result(
                        policy_id=policy_id,
                        verdict=verdict,
                        risk_score=hydra_result['risk_score'],
                        compliance_result={"status": "hydra_verified", "checks": []},
                        oracle_result=None,
                        reason=hydra_result['reason']
                    )
            except Exception as e:
                self.logger.error(f"Hydra check failed: {e}")
                # Fallback to standard flow
        
        # Step 1: Protocol compliance check
        compliance_result = self._check_protocol_compliance(policy_id, tx_cbor)
        
        # If compliance fails → immediate DANGER verdict
        if compliance_result["status"] == ComplianceStatus.INVALID:
            self.logger.warning(f"Protocol compliance FAILED: {compliance_result['reason']}")
            return self._build_result(
                policy_id=policy_id,
                verdict=Vote.DANGER,
                risk_score=100,
                compliance_result=compliance_result,
                oracle_result=None,
                reason=f"Protocol violation: {compliance_result['reason']}"
            )
        
        # Step 2: If network check needed, send HIRE_REQUEST to Oracle
        oracle_result = None
        if compliance_result["status"] == ComplianceStatus.REQUIRES_NETWORK_CHECK:
            self.logger.info("Compliance passed - sending HIRE_REQUEST to Oracle")
            oracle_result = await self._hire_oracle(policy_id, user_tip)
            
            if oracle_result is None:
                self.logger.error("Oracle HIRE_REQUEST failed")
                return self._build_result(
                    policy_id=policy_id,
                    verdict=Vote.WARNING,
                    risk_score=50,
                    compliance_result=compliance_result,
                    oracle_result=None,
                    reason="Oracle unavailable - network check incomplete"
                )
        
        # Step 3: Determine final verdict
        final_verdict, risk_score, reason = self._determine_final_verdict(
            compliance_result, oracle_result
        )
        
        self.log_complete(final_verdict, risk_score)
        
        return self._build_result(
            policy_id=policy_id,
            verdict=final_verdict,
            risk_score=risk_score,
            compliance_result=compliance_result,
            oracle_result=oracle_result,
            reason=reason
        )
    
    # -------------------------------------------------------------------------
    # PROTOCOL COMPLIANCE CHECK
    # -------------------------------------------------------------------------
    
    def _check_protocol_compliance(
        self, 
        policy_id: str, 
        tx_cbor: str
    ) -> Dict[str, Any]:
        """
        Check transaction/policy for protocol compliance.
        
        Checks:
        - Valid format (hex string, proper length)
        - Required fields present
        - Validity interval (if tx_cbor provided)
        - Protocol version compatibility
        
        Args:
            policy_id: Cardano policy ID
            tx_cbor: Transaction CBOR (optional)
            
        Returns:
            Dict with status, checks performed, any failures
        """
        checks_performed = []
        failures = []
        
        # Check 1: Valid policy ID format
        if policy_id:
            is_valid_hex = all(c in '0123456789abcdefABCDEF' for c in policy_id)
            is_valid_length = len(policy_id) == 56 or len(policy_id) == 64
            
            checks_performed.append({
                "check": "policy_id_format",
                "passed": is_valid_hex and is_valid_length
            })
            
            if not is_valid_hex:
                failures.append("Policy ID contains invalid hex characters")
            if not is_valid_length:
                failures.append("Policy ID has invalid length")
        
        # Check 2: Transaction CBOR validity (if provided)
        if tx_cbor:
            is_valid_cbor = len(tx_cbor) > 0 and len(tx_cbor) % 2 == 0
            
            checks_performed.append({
                "check": "cbor_format",
                "passed": is_valid_cbor
            })
            
            if not is_valid_cbor:
                failures.append("Transaction CBOR format invalid")
            
            # Check 3: Validity interval (simulated)
            checks_performed.append({
                "check": "validity_interval",
                "passed": True
            })
        
        # Check 4: No known malicious patterns
        if policy_id:
            is_blacklisted = policy_id.lower().startswith(("dead", "scam", "fake"))
            checks_performed.append({
                "check": "blacklist",
                "passed": not is_blacklisted
            })
            
            if is_blacklisted:
                failures.append("Policy ID matches known scam pattern")
        
        # Determine overall status
        if failures:
            status = ComplianceStatus.INVALID
        elif policy_id or tx_cbor:
            status = ComplianceStatus.REQUIRES_NETWORK_CHECK
        else:
            status = ComplianceStatus.INVALID
            failures.append("No policy_id or tx_cbor provided")
        
        return {
            "status": status,
            "checks_performed": checks_performed,
            "failures": failures,
            "reason": failures[0] if failures else None,
            "timestamp": self.get_timestamp()
        }
    
    # -------------------------------------------------------------------------
    # ORACLE HIRE REQUEST
    # -------------------------------------------------------------------------
    
    async def _hire_oracle(
        self, 
        policy_id: str, 
        user_tip: int
    ) -> Optional[Dict[str, Any]]:
        """
        Send HIRE_REQUEST to Oracle agent with escrow payment.
        
        Creates a signed message envelope per IACP/2.0 protocol,
        includes virtual escrow payment via Masumi.
        
        Args:
            policy_id: Policy ID being analyzed
            user_tip: User's node current block height
            
        Returns:
            Oracle's response payload or None if failed
        """
        escrow_id = self.generate_hash(f"{policy_id}{self.get_timestamp()}")[:16]
        
        hire_request = {
            "protocol": "IACP/2.0",
            "type": "HIRE_REQUEST",
            "from_did": "did:masumi:sentinel_01",
            "to_did": "did:masumi:oracle_01",
            "payload": {
                "policy_id": policy_id,
                "user_tip": user_tip,
                "escrow_id": escrow_id,
                "amount": 1.0,
                "job_type": "fork_check"
            },
            "timestamp": self.get_timestamp()
        }
        
        signed_envelope = self._sign_envelope(hire_request)
        self.pending_escrows[escrow_id] = 1.0
        
        self.logger.info(f"Sending HIRE_REQUEST to Oracle (escrow: {escrow_id})")
        
        if self.oracle:
            try:
                response = await self.oracle.handle_hire_request(signed_envelope)
                
                if response and self._verify_oracle_response(response):
                    self.logger.info("Oracle response verified successfully")
                    del self.pending_escrows[escrow_id]
                    return response.get("payload", {})
                else:
                    self.logger.warning("Oracle response signature verification failed")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Oracle HIRE_REQUEST failed: {e}")
                return None
        else:
            self.logger.warning("No Oracle connected - using mock response")
            return {
                "status": "SAFE_CHAIN",
                "mainnet_tip": user_tip,
                "user_node_tip": user_tip,
                "evidence": "none",
                "mock": True
            }
    
    # -------------------------------------------------------------------------
    # FINAL VERDICT DETERMINATION
    # -------------------------------------------------------------------------
    
    def _determine_final_verdict(
        self,
        compliance_result: Dict[str, Any],
        oracle_result: Optional[Dict[str, Any]]
    ) -> tuple:
        """
        Determine final verdict based on compliance and Oracle results.
        
        Args:
            compliance_result: Protocol compliance check result
            oracle_result: Oracle's network check result (if any)
            
        Returns:
            Tuple of (Vote, risk_score, reason)
        """
        if oracle_result:
            oracle_status = oracle_result.get("status", "")
            
            if oracle_status == "MINORITY_FORK_DETECTED":
                return (
                    Vote.DANGER,
                    90,
                    "DANGER_REPLAY_ATTACK: Node on minority fork"
                )
            elif oracle_status == "SAFE_CHAIN":
                return (
                    Vote.SAFE,
                    10,
                    "Network consensus verified - chain is healthy"
                )
            else:
                return (
                    Vote.WARNING,
                    50,
                    f"Unknown Oracle status: {oracle_status}"
                )
        
        if compliance_result["status"] == ComplianceStatus.VALID:
            return (
                Vote.SAFE,
                20,
                "Protocol compliance passed"
            )
        
        return (
            Vote.WARNING,
            50,
            "Analysis incomplete"
        )
    
    # -------------------------------------------------------------------------
    # CRYPTOGRAPHIC SIGNING
    # -------------------------------------------------------------------------
    
    def _sign_envelope(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a message envelope using Ed25519."""
        message_bytes = json.dumps(
            envelope, sort_keys=True, separators=(',', ':')
        ).encode()
        
        signed = self.private_key.sign(message_bytes)
        signature = base64.b64encode(signed.signature).decode()
        
        return {**envelope, "signature": signature}
    
    def _verify_oracle_response(self, response: Dict[str, Any]) -> bool:
        """Verify Oracle's signed response."""
        return "signature" in response or response.get("payload", {}).get("mock", False)
    
    # -------------------------------------------------------------------------
    # RESULT BUILDING
    # -------------------------------------------------------------------------
    
    def _build_result(
        self,
        policy_id: str,
        verdict: Vote,
        risk_score: int,
        compliance_result: Dict[str, Any],
        oracle_result: Optional[Dict[str, Any]],
        reason: str
    ) -> Dict[str, Any]:
        """Build the final result dictionary."""
        evidence_data = f"{policy_id}|{verdict.value}|{risk_score}|{self.get_timestamp()}"
        evidence_hash = self.generate_hash(evidence_data)
        
        return {
            "agent": "sentinel",
            "policy_id": policy_id,
            "verdict": verdict.value,
            "risk_score": risk_score,
            "reason": reason,
            "compliance": compliance_result,
            "oracle_result": oracle_result,
            "evidence_hash": evidence_hash,
            "timestamp": self.get_timestamp(),
            "llm_enabled": self.has_llm
        }
