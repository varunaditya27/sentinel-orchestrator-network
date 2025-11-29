"""
SentimentAnalyzer Agent
=======================
Analyzes community sentiment from on-chain votes via Blockfrost.
"""

import os
import httpx
import logging
from typing import Dict
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class SentimentResult:
    """Community sentiment analysis result"""
    sentiment: str  # STRONG_SUPPORT, MODERATE_SUPPORT, DIVIDED, STRONG_OPPOSITION
    support_percentage: float
    vote_breakdown: Dict[str, int]
    sample_size: int

class SentimentAnalyzer:
    """
    Analyzes community sentiment from on-chain votes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SON.SentimentAnalyzer")
        
        # Load environment variables from .env file
        load_dotenv()
        
        self.blockfrost_url = os.getenv(
            "BLOCKFROST_API_URL",
            "https://cardano-preprod.blockfrost.io/api"
        )
        self.blockfrost_key = os.getenv("BLOCKFROST_API_KEY", "")
        self.logger.info("SentimentAnalyzer initialized")
    
    async def analyze(self, gov_action_id: str) -> SentimentResult:
        """
        Get vote sentiment from Blockfrost.
        
        Args:
            gov_action_id: Governance action ID
            
        Returns:
            SentimentResult with community analysis
        """
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"project_id": self.blockfrost_key}
                
                # Get proposal votes
                response = await client.get(
                    f"{self.blockfrost_url}/v0/governance/proposals/{gov_action_id}/votes",
                    headers=headers
                )
                
                if response.status_code != 200:
                    return self._default_sentiment()
                
                votes = response.json()
                
                # Count votes
                yes_count = len([v for v in votes if v.get('vote') == 'yes'])
                no_count = len([v for v in votes if v.get('vote') == 'no'])
                abstain_count = len([v for v in votes if v.get('vote') == 'abstain'])
                
                total = yes_count + no_count + abstain_count
                support_pct = (yes_count / total * 100) if total > 0 else 50.0
                
                # Determine sentiment category
                if support_pct > 70:
                    sentiment = "STRONG_SUPPORT"
                elif support_pct > 50:
                    sentiment = "MODERATE_SUPPORT"
                elif support_pct > 30:
                    sentiment = "DIVIDED"
                else:
                    sentiment = "STRONG_OPPOSITION"
                
                return SentimentResult(
                    sentiment=sentiment,
                    support_percentage=support_pct,
                    vote_breakdown={
                        "yes": yes_count,
                        "no": no_count,
                        "abstain": abstain_count
                    },
                    sample_size=total
                )
                
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return self._default_sentiment()
    
    def _default_sentiment(self) -> SentimentResult:
        """Default sentiment when data unavailable"""
        return SentimentResult(
            sentiment="UNKNOWN",
            support_percentage=50.0,
            vote_breakdown={"yes": 0, "no": 0, "abstain": 0},
            sample_size=0
        )
    
    def generate_log(self, sentiment: SentimentResult) -> str:
        """Generate Matrix-style terminal log output"""
        return f"""
[SENTIMENT ANALYZER] Community Analysis
├─ Sentiment: {sentiment.sentiment}
├─ Support: {sentiment.support_percentage:.1f}%
├─ Votes Cast: {sentiment.sample_size}
│  ├─ YES: {sentiment.vote_breakdown['yes']}
│  ├─ NO: {sentiment.vote_breakdown['no']}
│  └─ ABSTAIN: {sentiment.vote_breakdown['abstain']}
└─ Source: On-chain voting data (Blockfrost)
        """
