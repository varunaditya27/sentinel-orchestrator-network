"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT B: Oracle Agent (Cross-Verification)
=============================================================================

Role: External data & liquidity verification
CrewAI Role Type: external_data_verifier
Masumi Pricing: Per external lookup

This agent verifies Sentinel findings using DEX liquidity and holder data.

=============================================================================
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from .base import BaseAgent, Vote, Severity


# =============================================================================
# VERIFICATION STATUS ENUM
# =============================================================================

class VerificationStatus(Enum):
    """Result of cross-verification against external data."""
    CONFIRMED = "CONFIRMED"      # External data confirms Sentinel's findings
    DENIED = "DENIED"            # External data contradicts Sentinel's findings
    UNCERTAIN = "UNCERTAIN"      # Insufficient data to verify


# =============================================================================
# LIQUIDITY THRESHOLDS - Used to assess risk from liquidity data
# =============================================================================

LIQUIDITY_THRESHOLDS = {
    "critical_low_ada": 1_000,       # < 1k ADA = extreme low liquidity
    "low_ada": 10_000,               # < 10k ADA = low liquidity
    "medium_ada": 100_000,           # < 100k ADA = medium liquidity
    "healthy_ada": 1_000_000,        # >= 1M ADA = healthy liquidity
    
    "concentration_danger": 80,      # > 80% held by top 10 = danger
    "concentration_warning": 50,     # > 50% held by top 10 = warning
    
    "min_holders": 10,               # < 10 holders = suspicious
    "healthy_holders": 100           # >= 100 holders = healthy distribution
}


# =============================================================================
# ORACLE AGENT CLASS
# =============================================================================

class OracleAgent(BaseAgent):
    """
    Agent B: External data verifier for cross-checking Sentinel findings.
    
    This agent:
    1. Queries DEX liquidity (WingRiders/Minswap - PLACEHOLDER)
    2. Checks token holder distribution
    3. Analyzes trading volume patterns
    4. Cross-verifies Sentinel's risk assessment
    5. Casts independent vote with confidence score
    
    Performance: Must complete in < 3 seconds
    """
    
    def __init__(
        self,
        wingriders_api: Optional[str] = None,
        minswap_api: Optional[str] = None
    ):
        """
        Initialize the Oracle Agent.
        
        Args:
            wingriders_api: WingRiders API endpoint (optional, uses mock if None)
            minswap_api: Minswap API endpoint (optional, uses mock if None)
        """
        super().__init__(agent_name="oracle", role="external_data_verifier")
        
        # DEX API configuration (PLACEHOLDER for production)
        self.wingriders_api = wingriders_api or "https://api.wingriders.com"
        self.minswap_api = minswap_api or "https://api.minswap.org"
        self.use_mock = (wingriders_api is None and minswap_api is None)
        
        if self.use_mock:
            self.logger.warning("Running in MOCK mode - using simulated DEX data")
    
    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - verify Sentinel's findings with external data.
        
        Args:
            input_data: {
                "sentinel_output": {...},  # Output from Sentinel Agent
                "policy_id": "<hex_string>",
                "timestamp": "<ISO 8601>"
            }
            
        Returns:
            Dict with liquidity_score, verification_status, and vote
        """
        # Extract inputs
        sentinel_output = input_data.get("sentinel_output", {})
        policy_id = input_data.get("policy_id", "")
        
        self.log_start(policy_id)
        
        # Step 1: Query DEX liquidity data
        liquidity_data = await self._query_dex_liquidity(policy_id)
        
        # Step 2: Fetch holder distribution
        holder_data = await self._fetch_holder_data(policy_id)
        
        # Step 3: Analyze trading patterns
        trading_data = await self._analyze_trading_patterns(policy_id)
        
        # Step 4: Cross-verify Sentinel findings
        verification = self._cross_verify_findings(
            sentinel_output, liquidity_data, holder_data
        )
        
        # Step 5: Calculate liquidity score
        liquidity_score = self._calculate_liquidity_score(
            liquidity_data, holder_data, trading_data
        )
        
        # Step 6: Determine our independent vote
        risk_score = self._calculate_oracle_risk(
            sentinel_output, liquidity_score, holder_data
        )
        vote = self.determine_vote(risk_score)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(liquidity_data, holder_data)
        
        self.log_complete(vote, risk_score)
        
        # Return structured output for Compliance Agent
        return {
            "agent": "oracle",
            "policy_id": policy_id,
            "liquidity_score": liquidity_score,
            "liquidity_depth_ada": liquidity_data.get("total_liquidity_ada", 0),
            "trading_volume_24h": trading_data.get("volume_24h", 0),
            "holder_count": holder_data.get("total_holders", 0),
            "holder_concentration": holder_data.get("top10_percentage", 0),
            "verification_status": verification.value,
            "data_sources": [
                {"source": "WingRiders", "timestamp": self.get_timestamp()},
                {"source": "Minswap", "timestamp": self.get_timestamp()}
            ],
            "vote": vote.value,
            "confidence": confidence,
            "risk_score": risk_score,
            "timestamp": self.get_timestamp()
        }
    
    # -------------------------------------------------------------------------
    # DEX LIQUIDITY METHODS
    # -------------------------------------------------------------------------
    
    async def _query_dex_liquidity(self, policy_id: str) -> Dict[str, Any]:
        """
        Query DEX APIs for liquidity pool data.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        
        Args:
            policy_id: The Cardano policy ID to look up
            
        Returns:
            Dict with liquidity_ada, pool info
        """
        self.logger.debug(f"Querying DEX liquidity for {policy_id[:16]}...")
        
        # =====================================================================
        # PLACEHOLDER - Mock DEX liquidity data
        # Replace with actual DEX API calls:
        #
        # async with httpx.AsyncClient() as client:
        #     wr_response = await client.get(
        #         f"{self.wingriders_api}/v1/pools?policyId={policy_id}"
        #     )
        #     ms_response = await client.get(
        #         f"{self.minswap_api}/v1/liquidity/{policy_id}"
        #     )
        # =====================================================================
        
        # Simulate liquidity based on policy_id patterns
        if policy_id.startswith("dead") or policy_id.startswith("bad"):
            # Low liquidity (suspicious)
            return {
                "total_liquidity_ada": 500,
                "pools": [
                    {"dex": "WingRiders", "liquidity_ada": 300},
                    {"dex": "Minswap", "liquidity_ada": 200}
                ],
                "has_data": True
            }
        elif policy_id.startswith("warn"):
            # Medium liquidity
            return {
                "total_liquidity_ada": 25_000,
                "pools": [
                    {"dex": "WingRiders", "liquidity_ada": 15_000},
                    {"dex": "Minswap", "liquidity_ada": 10_000}
                ],
                "has_data": True
            }
        else:
            # Healthy liquidity
            return {
                "total_liquidity_ada": 500_000,
                "pools": [
                    {"dex": "WingRiders", "liquidity_ada": 300_000},
                    {"dex": "Minswap", "liquidity_ada": 200_000}
                ],
                "has_data": True
            }
    
    async def _fetch_holder_data(self, policy_id: str) -> Dict[str, Any]:
        """
        Fetch token holder distribution data.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        
        Args:
            policy_id: The Cardano policy ID to look up
            
        Returns:
            Dict with holder counts and concentration
        """
        self.logger.debug(f"Fetching holder data for {policy_id[:16]}...")
        
        # Simulate holder data based on policy_id patterns
        if policy_id.startswith("dead") or policy_id.startswith("bad"):
            # Concentrated holdings (suspicious)
            return {
                "total_holders": 5,
                "top10_percentage": 95.0,
                "creator_percentage": 80.0,
                "has_data": True
            }
        elif policy_id.startswith("warn"):
            # Moderately concentrated
            return {
                "total_holders": 45,
                "top10_percentage": 60.0,
                "creator_percentage": 30.0,
                "has_data": True
            }
        else:
            # Healthy distribution
            return {
                "total_holders": 500,
                "top10_percentage": 25.0,
                "creator_percentage": 5.0,
                "has_data": True
            }
    
    async def _analyze_trading_patterns(self, policy_id: str) -> Dict[str, Any]:
        """
        Analyze recent trading volume and patterns.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        
        Args:
            policy_id: The Cardano policy ID to look up
            
        Returns:
            Dict with volume and pattern analysis
        """
        self.logger.debug(f"Analyzing trading patterns for {policy_id[:16]}...")
        
        # Simulate trading data based on policy_id patterns
        if policy_id.startswith("dead") or policy_id.startswith("bad"):
            return {
                "volume_24h": 100,
                "volume_7d": 500,
                "trade_count_24h": 3,
                "has_data": True
            }
        elif policy_id.startswith("warn"):
            return {
                "volume_24h": 5_000,
                "volume_7d": 25_000,
                "trade_count_24h": 25,
                "has_data": True
            }
        else:
            return {
                "volume_24h": 50_000,
                "volume_7d": 300_000,
                "trade_count_24h": 150,
                "has_data": True
            }
    
    # -------------------------------------------------------------------------
    # VERIFICATION & SCORING METHODS
    # -------------------------------------------------------------------------
    
    def _cross_verify_findings(
        self,
        sentinel_output: Dict[str, Any],
        liquidity_data: Dict[str, Any],
        holder_data: Dict[str, Any]
    ) -> VerificationStatus:
        """
        Cross-verify Sentinel's findings with our external data.
        
        Args:
            sentinel_output: Risk assessment from Sentinel Agent
            liquidity_data: DEX liquidity data
            holder_data: Token holder distribution
            
        Returns:
            VerificationStatus indicating agreement level
        """
        sentinel_vote = sentinel_output.get("vote", "SAFE")
        sentinel_score = sentinel_output.get("risk_score", 0)
        
        liquidity = liquidity_data.get("total_liquidity_ada", 0)
        holders = holder_data.get("total_holders", 0)
        concentration = holder_data.get("top10_percentage", 0)
        
        # Check if external data confirms high risk
        external_red_flags = 0
        
        if liquidity < LIQUIDITY_THRESHOLDS["low_ada"]:
            external_red_flags += 1
        if holders < LIQUIDITY_THRESHOLDS["min_holders"]:
            external_red_flags += 1
        if concentration > LIQUIDITY_THRESHOLDS["concentration_danger"]:
            external_red_flags += 1
        
        # Determine verification status
        if sentinel_vote == "DANGER" and external_red_flags >= 2:
            self.logger.info("CONFIRMED: Sentinel's DANGER assessment backed by external data")
            return VerificationStatus.CONFIRMED
        elif sentinel_vote == "SAFE" and external_red_flags == 0:
            self.logger.info("CONFIRMED: Sentinel's SAFE assessment backed by external data")
            return VerificationStatus.CONFIRMED
        elif sentinel_vote == "DANGER" and external_red_flags == 0:
            self.logger.warning("DENIED: Sentinel says DANGER but external data looks clean")
            return VerificationStatus.DENIED
        elif sentinel_vote == "SAFE" and external_red_flags >= 2:
            self.logger.warning("DENIED: Sentinel says SAFE but external data shows red flags")
            return VerificationStatus.DENIED
        else:
            self.logger.info("UNCERTAIN: Mixed signals from Sentinel and external data")
            return VerificationStatus.UNCERTAIN
    
    def _calculate_liquidity_score(
        self,
        liquidity_data: Dict[str, Any],
        holder_data: Dict[str, Any],
        trading_data: Dict[str, Any]
    ) -> int:
        """
        Calculate liquidity health score (0-100, higher = healthier).
        
        Unlike risk_score, this is inverted - 100 = very healthy.
        
        Args:
            liquidity_data: DEX liquidity information
            holder_data: Token holder distribution
            trading_data: Trading volume and patterns
            
        Returns:
            int: Liquidity health score from 0 to 100
        """
        score = 0
        
        # Liquidity depth scoring (40 points max)
        liquidity = liquidity_data.get("total_liquidity_ada", 0)
        if liquidity >= LIQUIDITY_THRESHOLDS["healthy_ada"]:
            score += 40
        elif liquidity >= LIQUIDITY_THRESHOLDS["medium_ada"]:
            score += 30
        elif liquidity >= LIQUIDITY_THRESHOLDS["low_ada"]:
            score += 15
        elif liquidity >= LIQUIDITY_THRESHOLDS["critical_low_ada"]:
            score += 5
        
        # Holder distribution scoring (30 points max)
        holders = holder_data.get("total_holders", 0)
        concentration = holder_data.get("top10_percentage", 100)
        
        if holders >= LIQUIDITY_THRESHOLDS["healthy_holders"]:
            score += 15
        elif holders >= LIQUIDITY_THRESHOLDS["min_holders"]:
            score += 8
        
        if concentration < LIQUIDITY_THRESHOLDS["concentration_warning"]:
            score += 15
        elif concentration < LIQUIDITY_THRESHOLDS["concentration_danger"]:
            score += 8
        
        # Trading volume scoring (30 points max)
        volume = trading_data.get("volume_24h", 0)
        trades = trading_data.get("trade_count_24h", 0)
        
        if volume >= 10_000:
            score += 15
        elif volume >= 1_000:
            score += 8
        elif volume >= 100:
            score += 3
        
        if trades >= 50:
            score += 15
        elif trades >= 10:
            score += 8
        elif trades >= 3:
            score += 3
        
        return min(score, 100)
    
    def _calculate_oracle_risk(
        self,
        sentinel_output: Dict[str, Any],
        liquidity_score: int,
        holder_data: Dict[str, Any]
    ) -> int:
        """
        Calculate Oracle's own risk assessment.
        
        Combines Sentinel's findings with liquidity analysis.
        
        Args:
            sentinel_output: Risk data from Sentinel
            liquidity_score: Our calculated liquidity health
            holder_data: Token holder distribution
            
        Returns:
            int: Risk score from 0 to 100
        """
        # Start with Sentinel's assessment (weighted 50%)
        sentinel_score = sentinel_output.get("risk_score", 0)
        
        # Invert liquidity score to risk (healthy liquidity = low risk)
        liquidity_risk = 100 - liquidity_score
        
        # Concentration risk
        concentration = holder_data.get("top10_percentage", 0)
        concentration_risk = concentration * 0.5  # Max 50 points
        
        # Weighted average
        oracle_risk = (
            sentinel_score * 0.4 +      # 40% weight to Sentinel
            liquidity_risk * 0.35 +     # 35% weight to liquidity
            concentration_risk * 0.25   # 25% weight to concentration
        )
        
        return min(int(oracle_risk), 100)
    
    def _calculate_confidence(
        self,
        liquidity_data: Dict[str, Any],
        holder_data: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence level in our assessment.
        
        Based on data availability and quality.
        
        Args:
            liquidity_data: DEX liquidity information
            holder_data: Token holder distribution
            
        Returns:
            float: Confidence from 0.0 to 1.0
        """
        confidence = 0.5  # Base confidence
        
        # Add confidence based on data availability
        if liquidity_data.get("has_data"):
            confidence += 0.2
        if holder_data.get("has_data"):
            confidence += 0.2
        
        # Add confidence based on data richness
        if len(liquidity_data.get("pools", [])) > 1:
            confidence += 0.05  # Multiple DEX sources
        if holder_data.get("total_holders", 0) > 50:
            confidence += 0.05  # Good sample size
        
        return min(confidence, 1.0)
#         pass
#
#     async def _get_holder_data(self, policy_id: str) -> dict:
#         """Fetch token holder distribution"""
#         pass
#
#     def _determine_verification_status(self, sentinel_findings: list, liquidity_data: dict) -> str:
#         """CONFIRMED, DENIED, or UNCERTAIN based on evidence"""
#         pass

# TODO: Implement WingRiders API client
# TODO: Implement Minswap API client
# TODO: Add caching for DEX responses (reduce API calls)
# TODO: Register with Masumi for per-lookup pricing
