"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT B: Oracle Agent
=============================================================================

Role: Blockchain verifier, fork detection, network consensus checker
Masumi Pricing: Per hire (via Sentinel escrow)

Based on simplified_agent_flow.txt:
1. Receives HIRE_REQUEST from Sentinel with escrow payment
2. Coordinates 5 specialist mini-agents for comprehensive analysis:
   - BlockScanner: Block height comparison, fork detection
   - StakeAnalyzer: Stake pool analysis, minority control
   - VoteDoctor: Governance vote analysis
   - MempoolSniffer: Mempool transaction analysis  
   - ReplayDetector: Transaction replay detection
3. Aggregates results using Bayesian fusion
4. Returns signed verdict to Sentinel

=============================================================================
"""

import asyncio
import base64
import json
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

import nacl.signing
from nacl.signing import SigningKey

from .base import BaseAgent, Vote, Severity
from .specialists import (
    BlockScanner,
    StakeAnalyzer,
    VoteDoctor,
    MempoolSniffer,
    ReplayDetector,
)


# =============================================================================
# ORACLE AGENT CLASS
# =============================================================================

@dataclass
class AggregatedResult:
    """Aggregated result from all specialists."""
    overall_risk: float  # 0.0 - 1.0
    severity: Severity
    vote: Vote
    findings: List[str]
    specialist_results: Dict[str, Any]
    confidence: float  # 0.0 - 1.0


class OracleAgent(BaseAgent):
    """
    Agent B: Blockchain verifier and network consensus checker.
    
    Coordinates 5 specialist mini-agents:
    1. BlockScanner - Block height comparison, fork detection
    2. StakeAnalyzer - Stake pool analysis, minority control detection
    3. VoteDoctor - Governance vote analysis
    4. MempoolSniffer - Mempool transaction analysis
    5. ReplayDetector - Transaction replay detection
    
    Uses Bayesian fusion to aggregate specialist results into a
    unified risk assessment.
    
    Performance: Should complete within 5 seconds (parallel specialist execution)
    """
    
    # Weight factors for Bayesian fusion (sum = 1.0)
    SPECIALIST_WEIGHTS = {
        "BlockScanner": 0.25,     # Fork detection is critical
        "StakeAnalyzer": 0.20,   # Stake concentration affects security
        "VoteDoctor": 0.15,      # Governance attacks are important
        "MempoolSniffer": 0.20,  # Mempool analysis for front-running
        "ReplayDetector": 0.20, # Replay attacks are severe
    }
    
    def __init__(self, enable_llm: bool = True):
        """
        Initialize the Oracle Agent with all specialist agents.
        
        Args:
            enable_llm: Whether to enable LLM-enhanced analysis
        """
        super().__init__(agent_name="oracle", role="verifier", enable_llm=enable_llm)
        
        # Generate cryptographic keypair for message signing
        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.verify_key
        
        # Initialize specialist agents
        self.specialists = {
            "BlockScanner": BlockScanner(),
            "StakeAnalyzer": StakeAnalyzer(),
            "VoteDoctor": VoteDoctor(),
            "MempoolSniffer": MempoolSniffer(),
            "ReplayDetector": ReplayDetector(),
        }
        
        self.logger.info(f"Oracle Agent initialized with {len(self.specialists)} specialists")
    
    def get_public_key_b64(self) -> str:
        """Get base64-encoded public key for verification."""
        return base64.b64encode(bytes(self.public_key)).decode()
    
    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD  
    # -------------------------------------------------------------------------
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - run all specialists and aggregate results.
        
        Args:
            input_data: {
                "policy_id": "<hex_string>",
                "address": "<cardano_address>",
                "user_tip": <block_height>,
                "context": {}
            }
            
        Returns:
            Dict with aggregated analysis results
        """
        policy_id = input_data.get("policy_id", "")
        address = input_data.get("address", "")
        user_tip = input_data.get("user_tip", 0)
        context = input_data.get("context", {})
        
        # Use address if provided, else use policy_id
        target = address if address else policy_id
        
        self.log_start(target[:16] if target else "unknown")
        
        # Run all specialists in parallel
        aggregated = await self._run_specialists(target, context)
        
        self.log_complete(aggregated.vote, int(aggregated.overall_risk * 100))
        
        return self._build_result(
            policy_id=policy_id,
            address=address,
            aggregated=aggregated
        )
    
    # -------------------------------------------------------------------------
    # HIRE REQUEST HANDLER (Called by Sentinel)
    # -------------------------------------------------------------------------
    
    async def handle_hire_request(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle HIRE_REQUEST from Sentinel agent.
        
        Validates the request, runs specialist analysis, and returns
        a signed response.
        
        Args:
            envelope: Signed IACP/2.0 message envelope from Sentinel
            
        Returns:
            Signed response envelope with analysis results
        """
        self.logger.info("Received HIRE_REQUEST from Sentinel")
        
        # Extract request details
        payload = envelope.get("payload", {})
        policy_id = payload.get("policy_id", "")
        user_tip = payload.get("user_tip", 0)
        escrow_id = payload.get("escrow_id", "")
        job_type = payload.get("job_type", "fork_check")
        
        self.logger.info(f"Processing job: {job_type} for policy: {policy_id[:16]}...")
        
        # Determine target (address format vs policy_id)
        target = policy_id
        context = {
            "user_tip": user_tip,
            "job_type": job_type,
            "escrow_id": escrow_id,
        }
        
        # Run specialist analysis
        aggregated = await self._run_specialists(target, context)
        
        # Determine Oracle status based on aggregated results
        oracle_status = self._determine_oracle_status(aggregated)
        
        # Build response payload
        response_payload = {
            "status": oracle_status,
            "mainnet_tip": user_tip,  # In production, fetch from node
            "user_node_tip": user_tip,
            "risk_score": aggregated.overall_risk,
            "verdict": aggregated.vote.value,  # Fixed: was 'vote'
            "reason": "; ".join(aggregated.findings[:3]) if aggregated.findings else "No significant risks",
            "severity": aggregated.severity.value,
            "findings": aggregated.findings[:5],  # Top 5 findings
            "specialist_summary": {
                name: {
                    "risk": result.get("risk_score", 0),
                    "severity": result.get("severity", "info"),
                }
                for name, result in aggregated.specialist_results.items()
            },
            "confidence": aggregated.confidence,
            "evidence": self.generate_hash(
                f"{policy_id}|{oracle_status}|{aggregated.overall_risk}"
            ),
            "escrow_id": escrow_id,
        }
        
        # Build and sign response envelope
        response_envelope = {
            "protocol": "IACP/2.0",
            "type": "HIRE_RESPONSE",
            "from_did": "did:masumi:oracle_01",
            "to_did": envelope.get("from_did", "did:masumi:sentinel_01"),
            "payload": response_payload,
            "timestamp": self.get_timestamp(),
        }
        
        signed_response = self._sign_envelope(response_envelope)
        
        self.logger.info(f"Returning HIRE_RESPONSE: {oracle_status}")
        return signed_response
    
    # -------------------------------------------------------------------------
    # SPECIALIST COORDINATION
    # -------------------------------------------------------------------------
    
    async def _run_specialists(
        self, 
        target: str, 
        context: Dict[str, Any]
    ) -> AggregatedResult:
        """
        Run all specialist agents in parallel and aggregate results.
        
        Args:
            target: Address or policy ID to analyze
            context: Additional context for specialists
            
        Returns:
            AggregatedResult with Bayesian-fused risk assessment
        """
        self.logger.info(f"Running {len(self.specialists)} specialists in parallel")
        
        # Create tasks for all specialists
        tasks = {}
        for name, specialist in self.specialists.items():
            tasks[name] = specialist.scan(target, context)
        
        # Run all specialists concurrently with timeout protection
        results = {}
        try:
            # FIXED: Added timeout to prevent hanging on slow specialists
            gathered = await asyncio.wait_for(
                asyncio.gather(*tasks.values(), return_exceptions=True),
                timeout=10.0  # 10 second overall timeout
            )
            
            for name, result in zip(tasks.keys(), gathered):
                if isinstance(result, Exception):
                    self.logger.warning(f"{name} failed with: {result}")
                    results[name] = {
                        "risk_score": 0.1,
                        "severity": "low",
                        "findings": [f"Specialist error: {str(result)}"],
                        "metadata": {"error": True},
                        "success": False,
                    }
                else:
                    results[name] = {
                        "risk_score": result.risk_score,
                        "severity": result.severity.value,
                        "findings": result.findings,
                        "metadata": result.metadata,
                        "success": result.success,
                    }
                    self.logger.debug(f"{name}: risk={result.risk_score:.2f}, severity={result.severity.value}")
        
        except asyncio.TimeoutError:
            self.logger.error("Specialist execution timeout - some specialists may be unresponsive")
            # Return partial results with timeout indication
            for name in tasks.keys():
                if name not in results:
                    results[name] = {
                        "risk_score": 0.15,
                        "severity": "low",
                        "findings": ["Specialist timed out"],
                        "metadata": {"timeout": True},
                        "success": False,
                    }
                    
        except Exception as e:
            self.logger.error(f"Specialist execution error: {e}")
        
        # Aggregate using Bayesian fusion
        return self._bayesian_fusion(results)
    
    def _bayesian_fusion(self, specialist_results: Dict[str, Any]) -> AggregatedResult:
        """
        Aggregate specialist results using weighted Bayesian fusion.
        
        The fusion formula:
        - Overall risk = weighted sum of individual risks
        - Confidence adjusted by successful specialist count
        - Severity = max severity from all specialists
        
        Args:
            specialist_results: Results from all specialists
            
        Returns:
            AggregatedResult with fused risk assessment
        """
        weighted_risk = 0.0
        total_weight = 0.0
        max_severity = Severity.LOW
        all_findings = []
        successful_count = 0
        
        for name, result in specialist_results.items():
            weight = self.SPECIALIST_WEIGHTS.get(name, 0.1)
            risk = result.get("risk_score", 0.0)
            
            # Apply weight
            weighted_risk += risk * weight
            total_weight += weight
            
            # Track success
            if result.get("success", True):
                successful_count += 1
            
            # Collect findings
            findings = result.get("findings", [])
            for finding in findings:
                all_findings.append(f"[{name}] {finding}")
            
            # Track max severity
            severity_str = result.get("severity", "low")
            try:
                severity = Severity(severity_str)
                if self._severity_rank(severity) > self._severity_rank(max_severity):
                    max_severity = severity
            except ValueError:
                pass
        
        # Normalize risk
        overall_risk = weighted_risk / total_weight if total_weight > 0 else 0.0
        
        # Calculate confidence based on specialist success rate
        confidence = successful_count / len(specialist_results) if specialist_results else 0.0
        
        # Determine vote based on overall risk
        if overall_risk >= 0.7:
            vote = Vote.DANGER
        elif overall_risk >= 0.4:
            vote = Vote.WARNING
        else:
            vote = Vote.SAFE
        
        return AggregatedResult(
            overall_risk=overall_risk,
            severity=max_severity,
            vote=vote,
            findings=all_findings,
            specialist_results=specialist_results,
            confidence=confidence,
        )
    
    def _severity_rank(self, severity: Severity) -> int:
        """Get numeric rank for severity comparison."""
        ranks = {
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }
        return ranks.get(severity, 0)
    
    def _determine_oracle_status(self, aggregated: AggregatedResult) -> str:
        """
        Determine Oracle status string based on aggregated results.
        
        Status values:
        - SAFE_CHAIN: No significant risks detected
        - MINORITY_FORK_DETECTED: Fork or consensus issue detected
        - NETWORK_RISK_DETECTED: General network-level risks
        - GOVERNANCE_RISK_DETECTED: Governance-related risks
        
        Args:
            aggregated: Aggregated specialist results
            
        Returns:
            Status string for Sentinel
        """
        # Check specific findings for status determination
        findings_text = " ".join(aggregated.findings).lower()
        
        if "fork" in findings_text or "chain continuity" in findings_text:
            return "MINORITY_FORK_DETECTED"
        
        if "governance" in findings_text or "drep" in findings_text:
            if aggregated.overall_risk >= 0.5:
                return "GOVERNANCE_RISK_DETECTED"
        
        if aggregated.overall_risk >= 0.6:
            return "NETWORK_RISK_DETECTED"
        
        if aggregated.overall_risk >= 0.3:
            return "CAUTION_ADVISED"
        
        return "SAFE_CHAIN"
    
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
    
    # -------------------------------------------------------------------------
    # RESULT BUILDING
    # -------------------------------------------------------------------------
    
    def _build_result(
        self,
        policy_id: str,
        address: str,
        aggregated: AggregatedResult
    ) -> Dict[str, Any]:
        """Build the final result dictionary."""
        evidence_data = f"{policy_id}|{address}|{aggregated.vote.value}|{self.get_timestamp()}"
        evidence_hash = self.generate_hash(evidence_data)
        
        # Generate reason from findings
        reason = "; ".join(aggregated.findings[:3]) if aggregated.findings else "No significant risks detected"
        
        return {
            "agent": "oracle",
            "policy_id": policy_id,
            "address": address,
            "verdict": aggregated.vote.value,  # Fixed: was 'vote'
            "reason": reason,  # Fixed: added missing field
            "risk_score": aggregated.overall_risk,
            "severity": aggregated.severity.value,
            "confidence": aggregated.confidence,
            "findings": aggregated.findings,
            "specialist_results": aggregated.specialist_results,
            "evidence_hash": evidence_hash,
            "timestamp": self.get_timestamp(),
            "llm_enabled": self.has_llm,
        }
