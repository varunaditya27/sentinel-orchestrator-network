"""
SentimentAnalyzer Agent
=======================
Analyzes community sentiment from on-chain votes via Blockfrost.
"""

import os
import httpx
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

from ..llm_config import AgentLLM

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
        
        self.blockfrost_url = os.getenv("BLOCKFROST_API_URL", "https://cardano-preprod.blockfrost.io/api")
        self.koios_url = os.getenv("KOIOS_API_URL", "https://preprod.koios.rest/api/v1")
        self.blockfrost_key = os.getenv("BLOCKFROST_API_KEY", "")
        self.llm = AgentLLM("SentimentAnalyzer")
        self.logger.info("SentimentAnalyzer initialized with LLM capabilities")
    
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
                
                # Decode Bech32 if needed
                target_id = gov_action_id
                is_bech32 = False
                if gov_action_id.startswith("gov_action"):
                    try:
                        import bech32
                        hrp, data = bech32.bech32_decode(gov_action_id)
                        if data:
                            decoded = bech32.convertbits(data, 5, 8, False)
                            if len(decoded) >= 32:
                                tx_hash = bytes(decoded[:32]).hex()
                                target_id = tx_hash + "#0" 
                                is_bech32 = True
                    except:
                        pass
                
                # If not Bech32, check if it looks like a Hex ID (64 chars + optional index)
                if not is_bech32:
                    # Simple check: must be at least 64 chars
                    if len(gov_action_id) < 64:
                         raise ValueError(f"Invalid Governance Action ID format: {gov_action_id}")

                # Verify existence first
                exists = False
                
                # 1. Try Blockfrost
                try:
                    prop_resp = await client.get(
                        f"{self.blockfrost_url}/v0/governance/proposals/{target_id}",
                        headers=headers
                    )
                    if prop_resp.status_code == 200:
                        exists = True
                    elif prop_resp.status_code == 403:
                        logging.warning("Blockfrost access denied (403). Switching to Koios fallback.")
                except Exception as e:
                    logging.error(f"Blockfrost check failed: {e}")

                # 2. Fallback to Koios if not confirmed
                if not exists:
                    try:
                        # Koios needs Tx Hash (Hex)
                        # If target_id is hash#index, split it
                        tx_hash_hex = target_id.split('#')[0]
                        if len(tx_hash_hex) == 64:
                            # Use separate client for Koios to avoid auth header issues if any, 
                            # or just reuse but be careful with headers. 
                            # Koios doesn't need project_id.
                            async with httpx.AsyncClient(verify=False) as k_client:
                                payload = {"_tx_hashes": [tx_hash_hex]}
                                k_resp = await k_client.post(f"{self.koios_url}/tx_info", json=payload)
                                if k_resp.status_code == 200:
                                    data = k_resp.json()
                                    if data and len(data) > 0:
                                        exists = True
                    except Exception as e:
                        logging.error(f"Koios check failed: {e}")

                if not exists:
                    raise ValueError(f"Governance Action ID {gov_action_id} not found or invalid")
                
                # Get proposal votes
                response = await client.get(
                    f"{self.blockfrost_url}/v0/governance/proposals/{gov_action_id}/votes",
                    headers=headers
                )
                
                if response.status_code == 404 or response.status_code == 400:
                    raise ValueError(f"Governance Action ID {gov_action_id} not found or invalid")
                
                if response.status_code != 200:
                    return self._default_sentiment()
                
                votes = response.json()
                if not votes and len(gov_action_id) > 10: 
                     # If valid-looking ID returns empty votes, it might just have no votes, 
                     # but if it's a dummy ID, we want to flag it. 
                     # For this task, user wants to verify EXISTENCE. 
                     # Blockfrost returns [] for valid ID with no votes.
                     # To verify existence, we should fetch the proposal details first.
                     pass
                
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
                
        except ValueError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return self._default_sentiment()
    
    async def analyze_sentiment_patterns(
        self,
        sentiment: SentimentResult,
        gov_action_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to analyze voting patterns and provide deeper sentiment insights.
        
        Args:
            sentiment: The basic sentiment analysis result
            gov_action_id: Governance action ID for context
            
        Returns:
            Dict with advanced analysis or None if LLM unavailable
        """
        if not self.llm.is_available:
            self.logger.debug("LLM not available for sentiment pattern analysis")
            return None
        
        try:
            prompt = self._build_sentiment_analysis_prompt(sentiment, gov_action_id)
            analysis_text = await self.llm._generate_content(prompt)
            
            # Parse the analysis into structured format
            return self._parse_sentiment_analysis(analysis_text)
            
        except Exception as e:
            self.logger.error(f"LLM sentiment pattern analysis failed: {e}")
            return None
    
    def _build_sentiment_analysis_prompt(self, sentiment: SentimentResult, gov_action_id: str) -> str:
        """Build prompt for advanced sentiment pattern analysis."""
        return f"""You are a Cardano governance analyst examining voting patterns for governance action {gov_action_id}.

**VOTING DATA ANALYSIS**

Sentiment Category: {sentiment.sentiment}
Support Percentage: {sentiment.support_percentage:.1f}%
Total Votes Cast: {sentiment.sample_size}
Vote Breakdown:
- YES votes: {sentiment.vote_breakdown['yes']}
- NO votes: {sentiment.vote_breakdown['no']}
- ABSTAIN votes: {sentiment.vote_breakdown['abstain']}

**PATTERN ANALYSIS REQUIREMENTS**

Analyze this voting data and provide insights on:

1. **ENGAGEMENT LEVEL** (LOW/MEDIUM/HIGH):
   - Voter participation assessment
   - Community interest indicators

2. **CONSENSUS STRENGTH** (WEAK/MODERATE/STRONG):
   - Level of agreement among voters
   - Polarization indicators

3. **POTENTIAL CONCERNS** (NONE/MINOR/SIGNIFICANT):
   - Signs of vote manipulation or coordination
   - Unusual voting patterns
   - Abstention rate analysis

4. **COMMUNITY SENTIMENT INTERPRETATION**:
   - What this voting pattern suggests about community opinion
   - Implications for proposal success

**FORMAT YOUR RESPONSE AS:**
ENGAGEMENT: [LOW/MEDIUM/HIGH] - [participation assessment]
CONSENSUS: [WEAK/MODERATE/STRONG] - [agreement analysis]
CONCERNS: [NONE/MINOR/SIGNIFICANT] - [pattern concerns]
INSIGHT: [brief interpretation of community sentiment and implications]

Keep each section concise (1 sentence). Base analysis on the actual voting numbers provided."""
    
    def _parse_sentiment_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the LLM sentiment analysis response into structured data."""
        result = {
            "engagement": {"level": "MEDIUM", "assessment": "Analysis unavailable"},
            "consensus": {"strength": "MODERATE", "analysis": "Analysis unavailable"},
            "concerns": {"level": "NONE", "details": "Analysis unavailable"},
            "insight": "Analysis unavailable"
        }
        
        try:
            lines = analysis_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('ENGAGEMENT:'):
                    parts = line.replace('ENGAGEMENT:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        level = parts[0].strip().upper()
                        if level in ['LOW', 'MEDIUM', 'HIGH']:
                            result["engagement"] = {"level": level, "assessment": parts[1].strip()}
                
                elif line.startswith('CONSENSUS:'):
                    parts = line.replace('CONSENSUS:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        strength = parts[0].strip().upper()
                        if strength in ['WEAK', 'MODERATE', 'STRONG']:
                            result["consensus"] = {"strength": strength, "analysis": parts[1].strip()}
                
                elif line.startswith('CONCERNS:'):
                    parts = line.replace('CONCERNS:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        level = parts[0].strip().upper()
                        if level in ['NONE', 'MINOR', 'SIGNIFICANT']:
                            result["concerns"] = {"level": level, "details": parts[1].strip()}
                
                elif line.startswith('INSIGHT:'):
                    insight = line.replace('INSIGHT:', '').strip()
                    result["insight"] = insight
        
        except Exception as e:
            self.logger.error(f"Failed to parse sentiment analysis: {e}")
        
        return result
    
    def _default_sentiment(self) -> SentimentResult:
        """Default sentiment when data unavailable"""
        return SentimentResult(
            sentiment="UNKNOWN",
            support_percentage=50.0,
            vote_breakdown={"yes": 0, "no": 0, "abstain": 0},
            sample_size=0
        )
    
    def generate_log(self, sentiment: SentimentResult, analysis: Optional[Dict[str, Any]] = None) -> str:
        """Generate Matrix-style terminal log output"""
        log_lines = [
            "[SENTIMENT ANALYZER] Community Analysis",
            f"├─ Sentiment: {sentiment.sentiment}",
            f"├─ Support: {sentiment.support_percentage:.1f}%",
            f"├─ Votes Cast: {sentiment.sample_size}",
            f"│  ├─ YES: {sentiment.vote_breakdown['yes']}",
            f"│  ├─ NO: {sentiment.vote_breakdown['no']}",
            f"│  └─ ABSTAIN: {sentiment.vote_breakdown['abstain']}",
            f"└─ Source: On-chain voting data (Blockfrost)"
        ]
        
        if analysis:
            log_lines.extend([
                "",
                "[SENTIMENT ANALYZER] LLM Pattern Analysis",
                f"├─ Engagement: {analysis.get('engagement', {}).get('level', 'N/A')}",
                f"├─ Consensus: {analysis.get('consensus', {}).get('strength', 'N/A')}",
                f"├─ Concerns: {analysis.get('concerns', {}).get('level', 'N/A')}",
                f"└─ Insight: {analysis.get('insight', 'N/A')[:60]}..."
            ])
        
        return "\n".join(log_lines)
