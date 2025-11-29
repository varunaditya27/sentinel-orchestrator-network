"""
GovernanceOrchestrator
=====================
Orchestrates the 3-agent analysis pipeline and aggregates verdicts.
"""

import logging
from typing import Dict, Any
from dotenv import load_dotenv
from .proposal_fetcher import ProposalFetcher
from .policy_analyzer import PolicyAnalyzer
from .sentiment_analyzer import SentimentAnalyzer
from .treasury_guardian import TreasuryGuardian

class GovernanceOrchestrator:
    """
    Orchestrates the 3-agent analysis pipeline.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SON.GovernanceOrchestrator")
        
        # Load environment variables from .env file
        load_dotenv()
        
        self.fetcher = ProposalFetcher()
        self.policy = PolicyAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.treasury = TreasuryGuardian()
        self.logger.info("GovernanceOrchestrator initialized")
    
    async def analyze_proposal(
        self,
        gov_action_id: str,
        ipfs_hash: str
    ) -> Dict[str, Any]:
        """
        Full analysis pipeline for a governance proposal.
        
        Args:
            gov_action_id: Governance action ID
            ipfs_hash: IPFS hash containing proposal metadata
            
        Returns:
            Dict with complete analysis and verdict
        """
        
        logs = []
        
        # Agent 1: Fetch metadata
        self.logger.info(f"Fetching metadata for {gov_action_id}")
        metadata = await self.fetcher.fetch_metadata(ipfs_hash)
        logs.append(self.fetcher.generate_log(metadata))
        
        # Agent 2: Policy analysis
        self.logger.info("Running policy compliance check")
        policy_analysis = await self.policy.analyze({
            'title': metadata.title,
            'abstract': metadata.abstract,
            'motivation': metadata.motivation,
            'rationale': metadata.rationale,
            'amount': metadata.amount
        })
        logs.append(self.policy.generate_log(policy_analysis))
        
        # Agent 3: Sentiment analysis
        self.logger.info("Analyzing community sentiment")
        sentiment = await self.sentiment.analyze(gov_action_id)
        logs.append(self.sentiment.generate_log(sentiment))

        # Agent 4: Treasury risk analysis
        self.logger.info("Analyzing treasury withdrawal risks")
        treasury_analysis = await self.treasury.analyze({
            'proposer': getattr(metadata, 'proposer', 'unknown'),
            'amount': metadata.amount,
            'title': metadata.title,
            'abstract': metadata.abstract
        })
        logs.append(self.treasury.generate_log(treasury_analysis))

        # Aggregate verdict
        verdict = self._aggregate_verdict(policy_analysis, sentiment, metadata, treasury_analysis)
        
        return {
            "gov_action_id": gov_action_id,
            "metadata": {
                "title": metadata.title,
                "amount_ada": metadata.amount / 1_000_000
            },
            "policy_analysis": {
                "recommendation": policy_analysis.recommendation,
                "flags": policy_analysis.flags,
                "reasoning": policy_analysis.reasoning,
                "confidence": policy_analysis.confidence
            },
            "sentiment": {
                "category": sentiment.sentiment,
                "support": sentiment.support_percentage,
                "sample_size": sentiment.sample_size
            },
            "treasury_analysis": {
                "risk_score": treasury_analysis.risk_score,
                "z_score": treasury_analysis.z_score,
                "gnn_anomaly": treasury_analysis.gnn_anomaly,
                "ncl_violation": treasury_analysis.ncl_violation,
                "flags": treasury_analysis.flags,
                "graph_stats": treasury_analysis.graph_stats
            },
            "verdict": verdict,
            "logs": logs
        }
    
    def _aggregate_verdict(self, policy, sentiment, metadata, treasury) -> Dict[str, Any]:
        """
        Agentic Logic: Combine agent recommendations.
        """
        
        # Rule 1: Treasury risk override - high risk proposals auto-reject
        if treasury.risk_score > 80:
            return {
                "recommendation": "NO",
                "reason": f"High treasury risk detected ({treasury.risk_score:.1f}/100) - Z-score: {treasury.z_score:.2f}, GNN: {treasury.gnn_anomaly:.3f}",
                "confidence": 0.95,
                "auto_votable": True
            }

        # Rule 2: If 2+ policy flags, auto-reject
        if len(policy.flags) >= 2:
            return {
                "recommendation": "NO",
                "reason": f"Multiple compliance violations: {', '.join(policy.flags[:2])}",
                "confidence": 0.9,
                "auto_votable": True
            }

        # Rule 4: Strong community opposition overrides
        if sentiment.support_percentage < 30:
            return {
                "recommendation": "NO",
                "reason": f"Strong community opposition ({sentiment.support_percentage:.0f}% support)",
                "confidence": 0.85,
                "auto_votable": True
            }

        # Rule 5: High-value proposals require manual review
        amount = metadata.amount / 1_000_000
        if amount > 25_000_000:
            return {
                "recommendation": "ABSTAIN",
                "reason": f"High-value proposal ({amount:,.0f} ADA) requires manual review",
                "confidence": 0.7,
                "auto_votable": False
            }

        # Rule 6: Follow policy recommendation if confidence is high
        if policy.confidence > 0.7:
            return {
                "recommendation": policy.recommendation,
                "reason": policy.reasoning,
                "confidence": policy.confidence,
                "auto_votable": policy.recommendation in ['YES', 'NO']
            }
        
        # Default: Abstain if uncertain
        return {
            "recommendation": "ABSTAIN",
            "reason": "Insufficient data for confident recommendation",
            "confidence": 0.5,
            "auto_votable": False
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for BaseAgent compatibility.
        Expects input_data with 'proposal_id' and optionally 'ipfs_hash'.
        """
        proposal_id = input_data.get("proposal_id", "")
        ipfs_hash = input_data.get("ipfs_hash", "")

        if not proposal_id:
            return {
                "error": "Missing proposal_id",
                "status": "failed"
            }

        # For now, use a mock IPFS hash if not provided
        if not ipfs_hash:
            # Mock IPFS hash for demonstration
            ipfs_hash = "QmXyz1234567890abcdef"

        return await self.analyze_proposal(proposal_id, ipfs_hash)
