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
        
        # Aggregate verdict
        verdict = self._aggregate_verdict(policy_analysis, sentiment, metadata)
        
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
            "verdict": verdict,
            "logs": logs
        }
    
    def _aggregate_verdict(self, policy, sentiment, metadata) -> Dict[str, Any]:
        """
        Agentic Logic: Combine agent recommendations.
        """
        
        # Rule 1: If 2+ policy flags, auto-reject
        if len(policy.flags) >= 2:
            return {
                "recommendation": "NO",
                "reason": f"Multiple compliance violations: {', '.join(policy.flags[:2])}",
                "confidence": 0.9,
                "auto_votable": True
            }
        
        # Rule 2: Strong community opposition overrides
        if sentiment.support_percentage < 30:
            return {
                "recommendation": "NO",
                "reason": f"Strong community opposition ({sentiment.support_percentage:.0f}% support)",
                "confidence": 0.85,
                "auto_votable": True
            }
        
        # Rule 3: High-value proposals require manual review
        amount = metadata.amount / 1_000_000
        if amount > 25_000_000:
            return {
                "recommendation": "ABSTAIN",
                "reason": f"High-value proposal ({amount:,.0f} ADA) requires manual review",
                "confidence": 0.7,
                "auto_votable": False
            }
        
        # Rule 4: Follow policy recommendation if confidence is high
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
