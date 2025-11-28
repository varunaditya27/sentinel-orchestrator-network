"""
=============================================================================
Sentinel Orchestrator Network (SON) - CrewAI Workflow Orchestrator
=============================================================================

This module orchestrates all 5 agents in the SON threat detection pipeline.
It runs the agents sequentially, passing data between them.

=============================================================================
WORKFLOW ORDER (Sequential):
=============================================================================

    Sentinel → Oracle → Compliance → ZK-Prover → Consensus
       (A)       (B)       (C)          (D)         (E)

=============================================================================
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .sentinel import SentinelAgent
from .oracle import OracleAgent
from .compliance import ComplianceAgent
from .consensus import ConsensusAgent
# Note: ZK-Prover is imported but uses mock for now


# =============================================================================
# WORKFLOW STATUS
# =============================================================================

class WorkflowStatus(Enum):
    """Status of the threat detection workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(Enum):
    """Status of an individual agent in the workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


# =============================================================================
# WORKFLOW RESULT
# =============================================================================

@dataclass
class WorkflowResult:
    """Complete result from the threat detection workflow."""
    
    # Core results
    policy_id: str
    final_verdict: str
    final_score: int
    
    # Status
    status: WorkflowStatus
    started_at: str
    completed_at: Optional[str] = None
    total_duration_ms: int = 0
    
    # Individual agent results
    sentinel_result: Dict[str, Any] = field(default_factory=dict)
    oracle_result: Dict[str, Any] = field(default_factory=dict)
    compliance_result: Dict[str, Any] = field(default_factory=dict)
    zk_prover_result: Dict[str, Any] = field(default_factory=dict)
    consensus_result: Dict[str, Any] = field(default_factory=dict)
    
    # Agent timing
    agent_durations: Dict[str, int] = field(default_factory=dict)
    
    # Capsule data
    capsule_id: Optional[str] = None
    capsule_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Error info
    error: Optional[str] = None
    failed_agent: Optional[str] = None


# =============================================================================
# EVENT CALLBACKS (for WebSocket updates)
# =============================================================================

@dataclass
class WorkflowEvent:
    """Event emitted during workflow execution for real-time updates."""
    event_type: str           # "agent_start", "agent_complete", "workflow_complete", "error"
    agent_name: Optional[str] # Which agent triggered this event
    data: Dict[str, Any]      # Event-specific data
    timestamp: str


# =============================================================================
# THREAT DETECTION CREW (Main Orchestrator)
# =============================================================================

class ThreatDetectionCrew:
    """
    The main orchestrator for the 5-agent threat detection workflow.
    
    This class:
    1. Initializes all 5 agents with configuration
    2. Runs them in sequence, passing data between agents
    3. Emits events for real-time WebSocket updates
    4. Handles errors and provides detailed results
    
    Usage:
        crew = ThreatDetectionCrew(config)
        result = await crew.run("policy_id_here")
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable[[WorkflowEvent], None]] = None
    ):
        """
        Initialize the Threat Detection Crew.
        
        Args:
            config: Configuration dict with API keys, endpoints, etc.
            event_callback: Optional callback for real-time event updates
        """
        self.config = config or {}
        self.event_callback = event_callback
        self.logger = logging.getLogger("son.crew")
        
        # Initialize all agents
        self._init_agents()
        
        self.logger.info("ThreatDetectionCrew initialized")
    
    def _init_agents(self) -> None:
        """Initialize all 5 agents with their configurations."""
        
        # Agent A: Sentinel (Threat Detection)
        self.sentinel = SentinelAgent(
            blockfrost_api_key=self.config.get("blockfrost_api_key")
        )
        
        # Agent B: Oracle (Cross-Verification)
        self.oracle = OracleAgent(
            wingriders_api=self.config.get("wingriders_api"),
            minswap_api=self.config.get("minswap_api")
        )
        
        # Agent C: Compliance (Sanctions/Risk)
        self.compliance = ComplianceAgent(
            sanctions_api=self.config.get("sanctions_api")
        )
        
        # Agent D: ZK-Prover (placeholder for now)
        # Will be implemented separately as per user request
        self.zk_prover = None  # Uses mock implementation
        
        # Agent E: Consensus (Final Arbiter)
        self.consensus = ConsensusAgent(
            hydra_endpoint=self.config.get("hydra_endpoint"),
            cardano_endpoint=self.config.get("cardano_endpoint")
        )
        
        self.logger.debug("All agents initialized")
    
    # -------------------------------------------------------------------------
    # MAIN WORKFLOW EXECUTION
    # -------------------------------------------------------------------------
    
    async def run(
        self,
        policy_id: str,
        creator_wallet: Optional[str] = None,
        scan_depth: str = "standard"
    ) -> WorkflowResult:
        """
        Execute the full threat detection workflow.
        
        This is the main entry point. It runs all 5 agents in sequence,
        passing data between them, and returns the complete result.
        
        Args:
            policy_id: The Cardano policy ID to analyze
            creator_wallet: Optional creator wallet address for compliance checks
            scan_depth: "standard" or "deep" scan
            
        Returns:
            WorkflowResult with all agent outputs and final verdict
        """
        start_time = time.time()
        started_at = datetime.utcnow().isoformat() + "Z"
        
        self.logger.info(f"Starting threat detection for {policy_id[:16]}...")
        
        # Initialize result
        result = WorkflowResult(
            policy_id=policy_id,
            final_verdict="UNKNOWN",
            final_score=0,
            status=WorkflowStatus.RUNNING,
            started_at=started_at
        )
        
        try:
            # -------------------------------------------------------------
            # STEP 1: Sentinel Agent (Threat Detection)
            # -------------------------------------------------------------
            self._emit_event("agent_start", "sentinel", {"policy_id": policy_id})
            
            agent_start = time.time()
            sentinel_output = await self.sentinel.process({
                "schema_version": "1.0",
                "policy_id": policy_id,
                "scan_depth": scan_depth,
                "timestamp": started_at
            })
            result.sentinel_result = sentinel_output
            result.agent_durations["sentinel"] = int((time.time() - agent_start) * 1000)
            
            self._emit_event("agent_complete", "sentinel", {
                "vote": sentinel_output.get("vote"),
                "risk_score": sentinel_output.get("risk_score"),
                "findings_count": len(sentinel_output.get("findings", []))
            })
            
            # -------------------------------------------------------------
            # STEP 2: Oracle Agent (Cross-Verification)
            # -------------------------------------------------------------
            self._emit_event("agent_start", "oracle", {"policy_id": policy_id})
            
            agent_start = time.time()
            oracle_output = await self.oracle.process({
                "sentinel_output": sentinel_output,
                "policy_id": policy_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            result.oracle_result = oracle_output
            result.agent_durations["oracle"] = int((time.time() - agent_start) * 1000)
            
            self._emit_event("agent_complete", "oracle", {
                "vote": oracle_output.get("vote"),
                "verification_status": oracle_output.get("verification_status"),
                "liquidity_score": oracle_output.get("liquidity_score")
            })
            
            # -------------------------------------------------------------
            # STEP 3: Compliance Agent (Sanctions/Risk)
            # -------------------------------------------------------------
            self._emit_event("agent_start", "compliance", {"policy_id": policy_id})
            
            # Use mock creator wallet if not provided
            wallet = creator_wallet or f"addr1{policy_id[:40]}"
            
            agent_start = time.time()
            compliance_output = await self.compliance.process({
                "sentinel_output": sentinel_output,
                "oracle_output": oracle_output,
                "policy_id": policy_id,
                "creator_wallet": wallet,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            result.compliance_result = compliance_output
            result.agent_durations["compliance"] = int((time.time() - agent_start) * 1000)
            
            self._emit_event("agent_complete", "compliance", {
                "vote": compliance_output.get("vote"),
                "sanctions_match": compliance_output.get("sanctions_match"),
                "risk_modifier": compliance_output.get("risk_modifier")
            })
            
            # -------------------------------------------------------------
            # STEP 4: ZK-Prover Agent (MOCK - to be implemented later)
            # -------------------------------------------------------------
            self._emit_event("agent_start", "zk_prover", {"policy_id": policy_id})
            
            agent_start = time.time()
            # PLACEHOLDER: Mock ZK-Prover output (real implementation pending)
            zk_prover_output = await self._mock_zk_prover(
                sentinel_output, oracle_output, compliance_output, policy_id
            )
            result.zk_prover_result = zk_prover_output
            result.agent_durations["zk_prover"] = int((time.time() - agent_start) * 1000)
            
            self._emit_event("agent_complete", "zk_prover", {
                "vote": zk_prover_output.get("vote"),
                "proof_hash": zk_prover_output.get("proof_hash", "")[:16] + "...",
                "mock_mode": zk_prover_output.get("mock_mode", True)
            })
            
            # -------------------------------------------------------------
            # STEP 5: Consensus Agent (Final Arbiter)
            # -------------------------------------------------------------
            self._emit_event("agent_start", "consensus", {"policy_id": policy_id})
            
            agent_start = time.time()
            consensus_output = await self.consensus.process({
                "sentinel_output": sentinel_output,
                "oracle_output": oracle_output,
                "compliance_output": compliance_output,
                "zk_prover_output": zk_prover_output,
                "policy_id": policy_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            result.consensus_result = consensus_output
            result.agent_durations["consensus"] = int((time.time() - agent_start) * 1000)
            
            self._emit_event("agent_complete", "consensus", {
                "final_verdict": consensus_output.get("final_verdict"),
                "final_score": consensus_output.get("final_score"),
                "capsule_id": consensus_output.get("capsule_id")
            })
            
            # -------------------------------------------------------------
            # FINALIZE RESULT
            # -------------------------------------------------------------
            result.final_verdict = consensus_output.get("final_verdict", "UNKNOWN")
            result.final_score = consensus_output.get("final_score", 0)
            result.capsule_id = consensus_output.get("capsule_id")
            result.capsule_metadata = consensus_output.get("capsule_metadata", {})
            result.status = WorkflowStatus.COMPLETED
            result.completed_at = datetime.utcnow().isoformat() + "Z"
            result.total_duration_ms = int((time.time() - start_time) * 1000)
            
            self._emit_event("workflow_complete", None, {
                "final_verdict": result.final_verdict,
                "final_score": result.final_score,
                "total_duration_ms": result.total_duration_ms
            })
            
            self.logger.info(
                f"Workflow completed: {result.final_verdict} "
                f"(score: {result.final_score}) in {result.total_duration_ms}ms"
            )
            
        except Exception as e:
            # Handle any errors during the workflow
            result.status = WorkflowStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.utcnow().isoformat() + "Z"
            result.total_duration_ms = int((time.time() - start_time) * 1000)
            
            self._emit_event("error", None, {"error": str(e)})
            self.logger.error(f"Workflow failed: {e}")
        
        return result
    
    # -------------------------------------------------------------------------
    # MOCK ZK-PROVER (placeholder until real implementation)
    # -------------------------------------------------------------------------
    
    async def _mock_zk_prover(
        self,
        sentinel_output: Dict[str, Any],
        oracle_output: Dict[str, Any],
        compliance_output: Dict[str, Any],
        policy_id: str
    ) -> Dict[str, Any]:
        """
        Mock ZK-Prover agent output.
        
        This is a placeholder until the real ZK-Prover is implemented.
        It generates mock proof data that follows the expected schema.
        
        Args:
            sentinel_output: Output from Sentinel Agent
            oracle_output: Output from Oracle Agent
            compliance_output: Output from Compliance Agent
            policy_id: The policy ID being analyzed
            
        Returns:
            Dict with mock proof_hash, verification_key, and vote
        """
        import hashlib
        
        # Combine all evidence for mock proof
        evidence = f"{sentinel_output}{oracle_output}{compliance_output}{policy_id}"
        proof_hash = hashlib.sha256(evidence.encode()).hexdigest()
        
        # Determine vote based on previous agents
        sentinel_score = sentinel_output.get("risk_score", 0)
        oracle_score = oracle_output.get("risk_score", 0)
        compliance_score = compliance_output.get("risk_score", 0)
        
        avg_score = (sentinel_score + oracle_score + compliance_score) / 3
        
        if avg_score <= 40:
            vote = "SAFE"
        elif avg_score <= 70:
            vote = "WARNING"
        else:
            vote = "DANGER"
        
        return {
            "agent": "zk_prover",
            "policy_id": policy_id,
            "proof_hash": proof_hash,
            "verification_key": f"vk_{proof_hash[:16]}",
            "proof_valid": True,
            "mock_mode": True,
            "vote": vote,
            "risk_score": int(avg_score),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # -------------------------------------------------------------------------
    # EVENT EMISSION
    # -------------------------------------------------------------------------
    
    def _emit_event(
        self,
        event_type: str,
        agent_name: Optional[str],
        data: Dict[str, Any]
    ) -> None:
        """
        Emit a workflow event for real-time updates.
        
        Args:
            event_type: Type of event (agent_start, agent_complete, etc.)
            agent_name: Which agent triggered the event (if applicable)
            data: Event-specific data
        """
        if self.event_callback is None:
            return
        
        event = WorkflowEvent(
            event_type=event_type,
            agent_name=agent_name,
            data=data,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        try:
            self.event_callback(event)
        except Exception as e:
            self.logger.warning(f"Failed to emit event: {e}")


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

async def analyze_policy(
    policy_id: str,
    config: Optional[Dict[str, Any]] = None,
    event_callback: Optional[Callable[[WorkflowEvent], None]] = None
) -> WorkflowResult:
    """
    Convenience function to run a full threat analysis.
    
    Creates a ThreatDetectionCrew and runs the workflow.
    
    Args:
        policy_id: The Cardano policy ID to analyze
        config: Optional configuration dict
        event_callback: Optional callback for real-time updates
        
    Returns:
        WorkflowResult with the complete analysis
        
    Example:
        result = await analyze_policy("abc123...")
        print(f"Verdict: {result.final_verdict}")
    """
    crew = ThreatDetectionCrew(config=config, event_callback=event_callback)
    return await crew.run(policy_id)
