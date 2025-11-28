"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT E: Consensus Agent (Final Arbiter)
=============================================================================

Role: Final decision + Hydra consensus + CIP-25 Capsule generation
CrewAI Role Type: consensus_mediator
Masumi Pricing: Paid per finalization

This agent aggregates all votes and produces the final ThreatProof Capsule.

=============================================================================
"""

import json
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from .base import BaseAgent, Vote, Severity


# =============================================================================
# CONSENSUS CONFIGURATION
# =============================================================================

# Vote weights for each agent (must sum to 1.0)
VOTE_WEIGHTS = {
    "sentinel": 0.40,       # Primary detector gets highest weight
    "oracle": 0.25,         # Cross-verification is important
    "compliance": 0.20,     # Regulatory risk matters
    "zk_prover": 0.15       # Proof verification confirmation
}

# Vote numeric values for weighted calculation
VOTE_VALUES = {
    Vote.SAFE.value: 0,
    Vote.WARNING.value: 50,
    Vote.DANGER.value: 100
}

# Final verdict thresholds
VERDICT_THRESHOLDS = {
    "safe_max": 40,         # 0-40 = SAFE
    "warning_max": 70       # 41-70 = WARNING, 71-100 = DANGER
}


# =============================================================================
# CONSENSUS AGENT CLASS
# =============================================================================

class ConsensusAgent(BaseAgent):
    """
    Agent E: Final consensus and ThreatProof Capsule generator.
    
    This agent:
    1. Collects votes from all previous agents (A/B/C/D)
    2. Calculates weighted final score
    3. Submits to Hydra for L2 consensus (PLACEHOLDER)
    4. Produces CIP-25 compliant ThreatProof Capsule
    5. Records to Cardano L1 (PLACEHOLDER)
    
    Performance: Must complete in < 5 seconds (including Hydra)
    """
    
    def __init__(
        self,
        hydra_endpoint: Optional[str] = None,
        cardano_endpoint: Optional[str] = None
    ):
        """
        Initialize the Consensus Agent.
        
        Args:
            hydra_endpoint: Hydra node WebSocket endpoint (uses mock if None)
            cardano_endpoint: Cardano node endpoint for L1 (uses mock if None)
        """
        super().__init__(agent_name="consensus", role="consensus_mediator")
        
        # Blockchain endpoints (PLACEHOLDER for production)
        self.hydra_endpoint = hydra_endpoint or "ws://localhost:4001"
        self.cardano_endpoint = cardano_endpoint or "http://localhost:3000"
        self.use_mock = (hydra_endpoint is None)
        
        if self.use_mock:
            self.logger.warning("Running in MOCK mode - using simulated Hydra/Cardano")
    
    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - aggregate votes and finalize verdict.
        
        Args:
            input_data: {
                "sentinel_output": {...},
                "oracle_output": {...},
                "compliance_output": {...},
                "zk_prover_output": {...},
                "policy_id": "<hex_string>",
                "timestamp": "<ISO 8601>"
            }
            
        Returns:
            Dict with final_verdict, capsule_id, tx hashes
        """
        # Extract all agent outputs
        sentinel_output = input_data.get("sentinel_output", {})
        oracle_output = input_data.get("oracle_output", {})
        compliance_output = input_data.get("compliance_output", {})
        zk_prover_output = input_data.get("zk_prover_output", {})
        policy_id = input_data.get("policy_id", "")
        
        self.log_start(policy_id)
        
        # Step 1: Aggregate votes from all agents
        vote_breakdown, final_score = self._aggregate_votes(
            sentinel_output, oracle_output, compliance_output, zk_prover_output
        )
        
        # Step 2: Determine final verdict
        final_verdict = self._determine_verdict(final_score)
        
        # Step 3: Submit to Hydra for L2 consensus
        hydra_result = await self._submit_to_hydra(
            policy_id, final_verdict, final_score, vote_breakdown
        )
        
        # Step 4: Build CIP-25 ThreatProof Capsule
        capsule_metadata = self._build_capsule_metadata(
            policy_id=policy_id,
            verdict=final_verdict,
            score=final_score,
            vote_breakdown=vote_breakdown,
            zk_proof=zk_prover_output,
            hydra_result=hydra_result
        )
        
        # Step 5: Write capsule to Cardano L1
        l1_result = await self._write_to_l1(capsule_metadata)
        
        # Generate capsule ID
        capsule_id = self._generate_capsule_id(policy_id)
        
        self.log_complete(Vote(final_verdict), final_score)
        
        # Return final structured output
        return {
            "agent": "consensus",
            "policy_id": policy_id,
            "final_verdict": final_verdict,
            "final_score": final_score,
            "vote_breakdown": vote_breakdown,
            "capsule_id": capsule_id,
            "capsule_metadata": capsule_metadata,
            "hydra_tx_id": hydra_result.get("tx_id"),
            "hydra_confirmed": hydra_result.get("confirmed", False),
            "l1_tx_id": l1_result.get("tx_id"),
            "l1_confirmed": l1_result.get("confirmed", False),
            "timestamp": self.get_timestamp()
        }
    
    # -------------------------------------------------------------------------
    # VOTE AGGREGATION
    # -------------------------------------------------------------------------
    
    def _aggregate_votes(
        self,
        sentinel_output: Dict[str, Any],
        oracle_output: Dict[str, Any],
        compliance_output: Dict[str, Any],
        zk_prover_output: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Aggregate votes from all agents using weighted calculation.
        
        Args:
            sentinel_output: Output from Sentinel Agent
            oracle_output: Output from Oracle Agent
            compliance_output: Output from Compliance Agent
            zk_prover_output: Output from ZK-Prover Agent
            
        Returns:
            Tuple of (vote_breakdown dict, final weighted score)
        """
        self.logger.debug("Aggregating votes from all agents...")
        
        # Collect votes and scores from each agent
        votes = {
            "sentinel": {
                "vote": sentinel_output.get("vote", Vote.SAFE.value),
                "score": sentinel_output.get("risk_score", 0),
                "weight": VOTE_WEIGHTS["sentinel"]
            },
            "oracle": {
                "vote": oracle_output.get("vote", Vote.SAFE.value),
                "score": oracle_output.get("risk_score", 0),
                "weight": VOTE_WEIGHTS["oracle"]
            },
            "compliance": {
                "vote": compliance_output.get("vote", Vote.SAFE.value),
                "score": compliance_output.get("risk_score", 0),
                "weight": VOTE_WEIGHTS["compliance"]
            },
            "zk_prover": {
                "vote": zk_prover_output.get("vote", Vote.SAFE.value),
                "score": zk_prover_output.get("risk_score", 0),
                "weight": VOTE_WEIGHTS["zk_prover"]
            }
        }
        
        # Calculate weighted final score
        weighted_score = 0.0
        for agent, data in votes.items():
            agent_score = data["score"]
            weight = data["weight"]
            weighted_score += agent_score * weight
            self.logger.debug(f"{agent}: score={agent_score}, weight={weight}")
        
        final_score = int(weighted_score)
        self.logger.info(f"Aggregated final score: {final_score}")
        
        return votes, final_score
    
    def _determine_verdict(self, final_score: int) -> str:
        """
        Determine final verdict based on aggregated score.
        
        Args:
            final_score: Weighted aggregate score (0-100)
            
        Returns:
            str: "SAFE", "WARNING", or "DANGER"
        """
        if final_score <= VERDICT_THRESHOLDS["safe_max"]:
            verdict = Vote.SAFE.value
        elif final_score <= VERDICT_THRESHOLDS["warning_max"]:
            verdict = Vote.WARNING.value
        else:
            verdict = Vote.DANGER.value
        
        self.logger.info(f"Final verdict: {verdict} (score: {final_score})")
        return verdict
    
    # -------------------------------------------------------------------------
    # HYDRA CONSENSUS
    # -------------------------------------------------------------------------
    
    async def _submit_to_hydra(
        self,
        policy_id: str,
        verdict: str,
        score: int,
        vote_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit final vote to Hydra for L2 consensus.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        
        Args:
            policy_id: The policy ID being analyzed
            verdict: Final verdict (SAFE/WARNING/DANGER)
            score: Final risk score
            vote_breakdown: All agent votes and weights
            
        Returns:
            Dict with tx_id, confirmed status, signatures
        """
        self.logger.debug("Submitting to Hydra for consensus...")
        
        # =====================================================================
        # PLACEHOLDER - Mock Hydra submission
        # Replace with actual Hydra WebSocket call:
        #
        # async with websockets.connect(self.hydra_endpoint) as ws:
        #     payload = {
        #         "tag": "NewTx",
        #         "transaction": {
        #             "policyId": policy_id,
        #             "verdict": verdict,
        #             "score": score
        #         }
        #     }
        #     await ws.send(json.dumps(payload))
        #     response = await ws.recv()
        #     return json.loads(response)
        # =====================================================================
        
        # Mock Hydra response
        mock_tx_id = self.generate_hash(f"hydra_{policy_id}_{self.get_timestamp()}")[:64]
        
        self.logger.info(f"Hydra consensus achieved: {mock_tx_id[:16]}...")
        
        return {
            "tx_id": mock_tx_id,
            "confirmed": True,
            "consensus_time_ms": 150,  # Hydra is fast!
            "signatures": [
                self.generate_hash(f"sig_1_{policy_id}")[:32],
                self.generate_hash(f"sig_2_{policy_id}")[:32]
            ]
        }
    
    # -------------------------------------------------------------------------
    # CIP-25 CAPSULE GENERATION
    # -------------------------------------------------------------------------
    
    def _build_capsule_metadata(
        self,
        policy_id: str,
        verdict: str,
        score: int,
        vote_breakdown: Dict[str, Any],
        zk_proof: Dict[str, Any],
        hydra_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build CIP-25 compliant ThreatProof Capsule metadata.
        
        This metadata structure follows CIP-25 NFT standard and can be
        minted as an NFT on Cardano L1.
        
        Args:
            policy_id: The analyzed policy ID
            verdict: Final verdict
            score: Final risk score
            vote_breakdown: All agent votes
            zk_proof: ZK proof data from prover agent
            hydra_result: Hydra consensus result
            
        Returns:
            Dict: CIP-25 compliant metadata structure
        """
        self.logger.debug("Building CIP-25 ThreatProof Capsule...")
        
        # Generate scan ID for this capsule
        scan_id = uuid.uuid4().hex[:8].upper()
        
        # Build evidence Merkle root from all votes
        evidence_string = json.dumps(vote_breakdown, sort_keys=True)
        evidence_merkle_root = self.generate_hash(evidence_string)
        
        # CIP-25 compliant structure
        capsule = {
            "721": {
                policy_id: {
                    f"ThreatProof_{scan_id}": {
                        # Core verdict data
                        "name": f"ThreatProof Capsule #{scan_id}",
                        "description": f"SON threat analysis verdict: {verdict}",
                        "verdict": verdict,
                        "risk_score": score,
                        
                        # Vote transparency
                        "vote_weights": {
                            agent: data["weight"]
                            for agent, data in vote_breakdown.items()
                        },
                        "vote_summary": {
                            agent: data["vote"]
                            for agent, data in vote_breakdown.items()
                        },
                        
                        # Cryptographic proofs
                        "evidence_merkle_root": evidence_merkle_root,
                        "hydra_tx_id": hydra_result.get("tx_id"),
                        "hydra_signatures": hydra_result.get("signatures", []),
                        "zk_proof_hash": zk_proof.get("proof_hash"),
                        
                        # Metadata
                        "version": "1.0",
                        "timestamp": self.get_timestamp(),
                        "analyzed_policy_id": policy_id,
                        
                        # Media (for NFT display)
                        "image": "ipfs://placeholder_capsule_image",
                        "mediaType": "image/png"
                    }
                }
            }
        }
        
        self.logger.info(f"Built ThreatProof Capsule: ThreatProof_{scan_id}")
        return capsule
    
    # -------------------------------------------------------------------------
    # CARDANO L1 WRITE
    # -------------------------------------------------------------------------
    
    async def _write_to_l1(self, capsule_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write ThreatProof Capsule to Cardano L1 as NFT.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        
        Args:
            capsule_metadata: CIP-25 compliant metadata
            
        Returns:
            Dict with tx_id, confirmed status
        """
        self.logger.debug("Writing capsule to Cardano L1...")
        
        # =====================================================================
        # PLACEHOLDER - Mock L1 write
        # Replace with actual Cardano transaction building:
        #
        # from pycardano import TransactionBuilder, TransactionOutput
        # 
        # builder = TransactionBuilder(self.context)
        # builder.add_output(TransactionOutput(
        #     address=minting_address,
        #     amount=2_000_000,  # 2 ADA minimum
        #     datum=capsule_metadata
        # ))
        # tx = builder.build_and_sign(...)
        # result = self.context.submit_tx(tx)
        # =====================================================================
        
        # Mock L1 response
        metadata_hash = self.generate_hash(json.dumps(capsule_metadata))
        mock_tx_id = metadata_hash[:64]
        
        self.logger.info(f"L1 capsule written: {mock_tx_id[:16]}...")
        
        return {
            "tx_id": mock_tx_id,
            "confirmed": True,
            "block_height": 12345678,  # Mock block height
            "fees_lovelace": 200_000   # ~0.2 ADA fee
        }
    
    def _generate_capsule_id(self, policy_id: str) -> str:
        """
        Generate unique capsule asset ID.
        
        Args:
            policy_id: The analyzed policy ID
            
        Returns:
            str: Unique capsule identifier
        """
        timestamp = self.get_timestamp().replace(":", "").replace("-", "")
        return f"CAPSULE_{policy_id[:8]}_{timestamp[:14]}"
#
#     async def _mint_capsule_nft(self, metadata: dict) -> str:
#         """Mint ThreatProof NFT on Cardano L1"""
#         pass
#
#     async def _trigger_masumi_payout(self, task_id: str):
#         """Distribute payments to all agents via Masumi"""
#         pass

# TODO: Integrate with infrastructure/hydra_client.py
# TODO: Implement Cardano transaction builder (Lucid/PyCardano)
# TODO: Add Masumi payment trigger
# TODO: Implement local fallback (ledger.json)
