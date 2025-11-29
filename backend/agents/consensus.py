"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT E: Consensus Agent
=============================================================================

Role: Final arbiter, vote aggregator, Hydra consensus, capsule writer
Masumi Pricing: Per finalization
Runs as: Final orchestrator in the 5-agent workflow

Based on SON Bible v6:
- Collects votes from all 4 previous agents
- Calculates weighted final score
- Submits to Hydra for L2 consensus
- Produces CIP-25 ThreatProof Capsule
- Writes capsule to Cardano L1

Vote Weights (from Bible):
- Sentinel: 40%
- Oracle: 25%
- Compliance: 20%
- ZK-Prover: 15%

Verdict Thresholds:
- 0-40: SAFE
- 41-70: WARNING
- 71-100: DANGER

=============================================================================
"""

import asyncio
import json
import base64
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from .base import BaseAgent, Vote


class ConsensusStatus(str, Enum):
    """Status of the consensus process."""
    GATHERING_VOTES = "gathering_votes"
    CALCULATING_SCORE = "calculating_score"
    HYDRA_CONSENSUS = "hydra_consensus"
    MINTING_CAPSULE = "minting_capsule"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AgentVote:
    """Represents a vote from an individual agent."""
    agent_name: str
    vote: Vote
    risk_score: float
    weight: float
    evidence_hash: str
    timestamp: str


@dataclass
class ConsensusResult:
    """Final consensus result."""
    final_score: float
    final_verdict: Vote
    agent_votes: List[AgentVote]
    weighted_breakdown: Dict[str, float]
    confidence: float
    capsule_id: Optional[str] = None
    hydra_tx_id: Optional[str] = None


class ConsensusAgent(BaseAgent):
    """
    Agent E: Final consensus aggregator and capsule minter.

    Responsibilities:
    - Collect votes from Sentinel, Oracle, Compliance, ZK-Prover
    - Apply weighted scoring algorithm
    - Submit to Hydra for L2 consensus confirmation
    - Mint ThreatProof Capsule on Cardano L1
    - Provide immutable audit trail

    Performance: Should complete within 5 seconds
    """

    # Vote weights as defined in SON Bible v6
    AGENT_WEIGHTS = {
        "sentinel": 0.40,     # 40% - Primary detector
        "oracle": 0.25,       # 25% - External verification
        "compliance": 0.20,   # 20% - Regulatory risk
        "zk_prover": 0.15,    # 15% - Privacy & integrity
    }

    # Verdict thresholds
    VERDICT_THRESHOLDS = {
        Vote.SAFE: (0, 40),
        Vote.WARNING: (41, 70),
        Vote.DANGER: (71, 100),
    }

    def __init__(self, enable_llm: bool = True):
        """
        Initialize the Consensus Agent.

        Args:
            enable_llm: Whether to enable LLM-enhanced analysis
        """
        super().__init__(agent_name="consensus", role="arbiter", enable_llm=enable_llm)

        # Generate cryptographic keypair
        self.private_key = self._generate_keypair()
        self.public_key = self.private_key.verify_key

        # Consensus state
        self.pending_consensus: Dict[str, List[AgentVote]] = {}

        self.logger.info("Consensus Agent initialized as final arbiter")

    def get_public_key_b64(self) -> str:
        """Get base64-encoded public key for verification."""
        import base64
        return base64.b64encode(bytes(self.public_key)).decode()

    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - aggregate votes and reach final consensus.

        Args:
            input_data: {
                "task_id": "<unique_task_id>",
                "agent_votes": [
                    {
                        "agent": "sentinel",
                        "vote": "DANGER",
                        "risk_score": 85,
                        "evidence_hash": "<hash>",
                        "timestamp": "<iso>"
                    },
                    // ... other agent votes
                ],
                "context": {}
            }

        Returns:
            Dict with final consensus result and capsule info
        """
        task_id = input_data.get("task_id", "")
        agent_votes_data = input_data.get("agent_votes", [])
        context = input_data.get("context", {})

        self.log_start(task_id)

        try:
            # Parse agent votes
            agent_votes = self._parse_agent_votes(agent_votes_data)

            # Validate we have all required votes
            validation_result = self._validate_votes(agent_votes)
            if not validation_result["valid"]:
                return self._build_error_result(
                    task_id,
                    f"Invalid votes: {validation_result['reason']}",
                    agent_votes
                )

            # Calculate weighted consensus
            consensus = self._calculate_consensus(agent_votes)

            # Submit to Hydra for L2 consensus (mock for now)
            hydra_result = await self._submit_hydra_consensus(consensus, context)

            # Mint ThreatProof capsule
            capsule_result = await self._mint_threatproof_capsule(
                consensus, hydra_result, context
            )

            # Update consensus with capsule info
            consensus.capsule_id = capsule_result.get("capsule_id")
            consensus.hydra_tx_id = hydra_result.get("tx_id")

            self.log_complete(consensus.final_verdict, int(consensus.final_score))

            return self._build_success_result(task_id, consensus, capsule_result)

        except Exception as e:
            self.logger.error(f"Consensus processing failed: {e}")
            return self._build_error_result(task_id, str(e), [])

    # -------------------------------------------------------------------------
    # VOTE PARSING AND VALIDATION
    # -------------------------------------------------------------------------

    def _parse_agent_votes(self, votes_data: List[Dict[str, Any]]) -> List[AgentVote]:
        """Parse raw vote data into AgentVote objects."""
        agent_votes = []

        for vote_data in votes_data:
            try:
                agent_name = vote_data.get("agent", "")
                vote_str = vote_data.get("vote", "").upper()
                risk_score = float(vote_data.get("risk_score", 0))
                evidence_hash = vote_data.get("evidence_hash", "")
                timestamp = vote_data.get("timestamp", self.get_timestamp())

                # Parse vote enum
                try:
                    vote = Vote(vote_str)
                except ValueError:
                    vote = Vote.WARNING  # Default to warning on invalid vote

                # Get weight
                weight = self.AGENT_WEIGHTS.get(agent_name, 0.1)

                agent_vote = AgentVote(
                    agent_name=agent_name,
                    vote=vote,
                    risk_score=risk_score,
                    weight=weight,
                    evidence_hash=evidence_hash,
                    timestamp=timestamp
                )

                agent_votes.append(agent_vote)

            except Exception as e:
                self.logger.warning(f"Failed to parse vote from {vote_data}: {e}")
                continue

        return agent_votes

    def _validate_votes(self, agent_votes: List[AgentVote]) -> Dict[str, Any]:
        """Validate that we have all required agent votes."""
        required_agents = set(self.AGENT_WEIGHTS.keys())
        present_agents = {vote.agent_name for vote in agent_votes}

        missing_agents = required_agents - present_agents

        if missing_agents:
            return {
                "valid": False,
                "reason": f"Missing votes from: {', '.join(missing_agents)}"
            }

        if len(agent_votes) < 4:
            return {
                "valid": False,
                "reason": f"Only {len(agent_votes)} votes received, need 4"
            }

        return {"valid": True}

    # -------------------------------------------------------------------------
    # CONSENSUS CALCULATION
    # -------------------------------------------------------------------------

    def _calculate_consensus(self, agent_votes: List[AgentVote]) -> ConsensusResult:
        """
        Calculate weighted consensus from all agent votes.

        Algorithm:
        1. Convert each vote to numeric score (SAFE=0, WARNING=50, DANGER=100)
        2. Apply agent weights
        3. Sum weighted scores
        4. Determine final verdict based on thresholds
        """
        # Convert votes to numeric scores
        vote_scores = {
            Vote.SAFE: 0,
            Vote.WARNING: 50,
            Vote.DANGER: 100,
        }

        weighted_sum = 0.0
        total_weight = 0.0
        weighted_breakdown = {}

        for agent_vote in agent_votes:
            # Get base score from vote
            base_score = vote_scores.get(agent_vote.vote, 50)

            # Adjust score based on agent's risk_score (0-100 scale)
            adjusted_score = (base_score + agent_vote.risk_score) / 2

            # Apply weight
            weighted_score = adjusted_score * agent_vote.weight
            weighted_sum += weighted_score
            total_weight += agent_vote.weight

            weighted_breakdown[agent_vote.agent_name] = weighted_score

            self.logger.debug(
                f"{agent_vote.agent_name}: vote={agent_vote.vote.value}, "
                f"risk_score={agent_vote.risk_score:.1f}, "
                f"weight={agent_vote.weight:.2f}, "
                f"weighted_score={weighted_score:.1f}"
            )

        # Calculate final score
        final_score = weighted_sum / total_weight if total_weight > 0 else 50

        # Determine final verdict based on thresholds
        final_verdict = self._determine_verdict(final_score)

        # Calculate confidence based on vote agreement
        confidence = self._calculate_confidence(agent_votes, final_verdict)

        return ConsensusResult(
            final_score=final_score,
            final_verdict=final_verdict,
            agent_votes=agent_votes,
            weighted_breakdown=weighted_breakdown,
            confidence=confidence
        )

    def _determine_verdict(self, final_score: float) -> Vote:
        """Determine final verdict based on score thresholds."""
        for verdict, (min_score, max_score) in self.VERDICT_THRESHOLDS.items():
            if min_score <= final_score <= max_score:
                return verdict

        # Default fallback
        return Vote.WARNING

    def _calculate_confidence(self, agent_votes: List[AgentVote], final_verdict: Vote) -> float:
        """
        Calculate confidence in the consensus result.

        Confidence factors:
        - Agreement level among agents
        - Weight of agreeing agents
        - Risk score consistency
        """
        agreeing_votes = [v for v in agent_votes if v.vote == final_verdict]
        agreeing_weight = sum(v.weight for v in agreeing_votes)
        total_weight = sum(v.weight for v in agent_votes)

        # Base confidence on weight agreement
        agreement_ratio = agreeing_weight / total_weight if total_weight > 0 else 0

        # Bonus for strong consensus (all agents agree)
        if len(agreeing_votes) == len(agent_votes):
            agreement_ratio *= 1.2

        return min(agreement_ratio, 1.0)

    # -------------------------------------------------------------------------
    # HYDRA CONSENSUS SUBMISSION
    # -------------------------------------------------------------------------

    async def _submit_hydra_consensus(
        self,
        consensus: ConsensusResult,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit consensus result to Hydra for L2 confirmation.

        In production, this would:
        1. Connect to Hydra WebSocket
        2. Submit consensus data
        3. Wait for L2 confirmation
        4. Return transaction ID

        For now: Mock implementation
        """
        self.logger.info("Submitting consensus to Hydra L2...")

        # Simulate Hydra submission delay
        await asyncio.sleep(0.2)

        # Mock Hydra response
        mock_tx_id = f"hydra_tx_{hashlib.sha256(json.dumps({
            'final_score': consensus.final_score,
            'final_verdict': consensus.final_verdict.value,
            'timestamp': self.get_timestamp()
        }).encode()).hexdigest()[:16]}"

        return {
            "tx_id": mock_tx_id,
            "confirmed": True,
            "latency_ms": 150,
            "hydra_head_id": "hydra-head-001",
            "status": "confirmed"
        }

    # -------------------------------------------------------------------------
    # THREATPROOF CAPSULE MINTING
    # -------------------------------------------------------------------------

    async def _mint_threatproof_capsule(
        self,
        consensus: ConsensusResult,
        hydra_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mint ThreatProof capsule on Cardano L1.

        In production, this would:
        1. Build CIP-25 metadata
        2. Construct minting transaction
        3. Submit to Cardano network
        4. Return capsule ID

        For now: Mock implementation
        """
        self.logger.info("Minting ThreatProof capsule on Cardano L1...")

        # Simulate minting delay
        await asyncio.sleep(0.3)

        # Generate capsule ID
        capsule_data = {
            "verdict": consensus.final_verdict.value,
            "risk_score": consensus.final_score,
            "agent_votes": [
                {
                    "agent": v.agent_name,
                    "vote": v.vote.value,
                    "weight": v.weight
                }
                for v in consensus.agent_votes
            ],
            "hydra_tx_id": hydra_result.get("tx_id"),
            "timestamp": self.get_timestamp()
        }

        capsule_id = f"CAPSULE_{hashlib.sha256(json.dumps(capsule_data).encode()).hexdigest()[:16].upper()}_{self.get_timestamp()[:10].replace('-', '')}"

        # Mock CIP-25 metadata
        cip25_metadata = {
            "721": {
                "d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf0abb9efb1c650668": {  # Policy ID
                    capsule_id: {
                        "name": f"ThreatProof Capsule #{capsule_id.split('_')[1]}",
                        "description": f"SON threat analysis verdict: {consensus.final_verdict.value}",
                        "verdict": consensus.final_verdict.value,
                        "risk_score": consensus.final_score,
                        "vote_weights": {v.agent_name: v.weight for v in consensus.agent_votes},
                        "vote_summary": {v.agent_name: v.vote.value for v in consensus.agent_votes},
                        "evidence_merkle_root": self._generate_merkle_root(consensus.agent_votes),
                        "hydra_tx_id": hydra_result.get("tx_id"),
                        "zk_proof_hash": "mock_zk_proof_hash",  # Would come from ZK-Prover
                        "version": "2.0",
                        "timestamp": self.get_timestamp()
                    }
                }
            }
        }

        return {
            "capsule_id": capsule_id,
            "policy_id": "d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf0abb9efb1c650668",
            "cip25_metadata": cip25_metadata,
            "tx_hash": f"cardano_tx_{hashlib.sha256(capsule_id.encode()).hexdigest()[:32]}",
            "status": "minted"
        }

    def _generate_merkle_root(self, agent_votes: List[AgentVote]) -> str:
        """Generate Merkle root from agent evidence hashes."""
        if not agent_votes:
            return "0x" + "0" * 64

        # Simple hash concatenation for demo
        combined = "|".join(v.evidence_hash for v in agent_votes)
        return hashlib.sha256(combined.encode()).hexdigest()

    # -------------------------------------------------------------------------
    # RESULT BUILDING
    # -------------------------------------------------------------------------

    def _build_success_result(
        self,
        task_id: str,
        consensus: ConsensusResult,
        capsule_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build successful consensus result."""
        evidence_data = f"{task_id}|{consensus.final_score}|{consensus.final_verdict.value}|{self.get_timestamp()}"
        evidence_hash = self.generate_hash(evidence_data)

        return {
            "agent": "consensus",
            "task_id": task_id,
            "status": ConsensusStatus.COMPLETE,
            "final_verdict": consensus.final_verdict.value,
            "final_score": round(consensus.final_score, 2),
            "confidence": round(consensus.confidence, 3),
            "agent_votes": [
                {
                    "agent": v.agent_name,
                    "vote": v.vote.value,
                    "risk_score": v.risk_score,
                    "weight": v.weight,
                    "evidence_hash": v.evidence_hash
                }
                for v in consensus.agent_votes
            ],
            "weighted_breakdown": consensus.weighted_breakdown,
            "capsule": {
                "id": consensus.capsule_id,
                "policy_id": capsule_result.get("policy_id"),
                "tx_hash": capsule_result.get("tx_hash"),
                "metadata": capsule_result.get("cip25_metadata")
            },
            "hydra": {
                "tx_id": consensus.hydra_tx_id,
                "status": "confirmed"
            },
            "evidence_hash": evidence_hash,
            "timestamp": self.get_timestamp(),
            "llm_enabled": self.has_llm
        }

    def _build_error_result(
        self,
        task_id: str,
        error: str,
        agent_votes: List[AgentVote]
    ) -> Dict[str, Any]:
        """Build error result."""
        return {
            "agent": "consensus",
            "task_id": task_id,
            "status": ConsensusStatus.FAILED,
            "error": error,
            "final_verdict": Vote.WARNING.value,
            "final_score": 50,
            "confidence": 0.0,
            "agent_votes": [
                {
                    "agent": v.agent_name,
                    "vote": v.vote.value,
                    "risk_score": v.risk_score,
                    "weight": v.weight
                }
                for v in agent_votes
            ],
            "timestamp": self.get_timestamp(),
            "llm_enabled": self.has_llm
        }

    def _generate_keypair(self):
        """Generate Ed25519 keypair for signing."""
        import nacl.signing
        return nacl.signing.SigningKey.generate()
