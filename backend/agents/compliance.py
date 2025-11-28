"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT C: Compliance Agent (Risk Policies)
=============================================================================

Role: Sanctions + wallet risk + compliance-based reasoning
CrewAI Role Type: compliance_checker
Masumi Pricing: Usage-based

This agent assesses regulatory and AML risk for wallets and tokens.

=============================================================================
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from .base import BaseAgent, Vote, Severity


# =============================================================================
# MOCK SANCTIONS DATABASE - For hackathon demo only
# =============================================================================

# In production, this would connect to OFAC, Chainalysis, Elliptic, etc.
MOCK_SANCTIONS_LIST: Set[str] = {
    "addr1_sanctioned_wallet_example_1",
    "addr1_sanctioned_wallet_example_2",
    "addr1_known_scammer_wallet_001",
    "addr1_known_scammer_wallet_002",
}

# Known high-risk wallet patterns (prefixes for demo)
HIGH_RISK_PREFIXES = ["dead", "bad", "scam", "hack"]


# =============================================================================
# RISK INDICATOR DEFINITIONS
# =============================================================================

class RiskLevel(Enum):
    """Severity levels for wallet risk indicators."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


WALLET_AGE_THRESHOLDS = {
    "critical_new": 1,      # < 1 day old = critical
    "high_risk": 7,         # < 7 days old = high risk
    "medium_risk": 30,      # < 30 days old = medium risk
    "low_risk": 90,         # < 90 days old = low risk
    "established": 180      # >= 180 days = established
}

# Risk modifier ranges
RISK_MODIFIERS = {
    "very_low": 0.5,        # Established wallet, no flags
    "low": 0.75,            # Minor concerns
    "neutral": 1.0,         # Default
    "elevated": 1.25,       # Some red flags
    "high": 1.5,            # Multiple red flags
    "critical": 2.0         # Sanctions match or severe flags
}


# =============================================================================
# COMPLIANCE AGENT CLASS
# =============================================================================

class ComplianceAgent(BaseAgent):
    """
    Agent C: Compliance and sanctions risk assessor.
    
    This agent:
    1. Checks wallets against sanctions lists (OFAC, etc.)
    2. Analyzes wallet age and transaction patterns
    3. Identifies behavioral red flags
    4. Calculates compliance risk modifier (0.5 - 2.0)
    5. Casts compliance-weighted vote
    
    Performance: Must complete in < 2 seconds
    """
    
    def __init__(self, sanctions_api: Optional[str] = None):
        """
        Initialize the Compliance Agent.
        
        Args:
            sanctions_api: External sanctions API endpoint (uses mock if None)
        """
        super().__init__(agent_name="compliance", role="compliance_checker")
        
        # Sanctions API configuration (PLACEHOLDER for production)
        self.sanctions_api = sanctions_api
        self.use_mock = sanctions_api is None
        
        if self.use_mock:
            self.logger.warning("Running in MOCK mode - using simulated sanctions data")
    
    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - assess compliance and sanctions risk.
        
        Args:
            input_data: {
                "sentinel_output": {...},
                "oracle_output": {...},
                "policy_id": "<hex_string>",
                "creator_wallet": "<addr...>",
                "timestamp": "<ISO 8601>"
            }
            
        Returns:
            Dict with sanctions_match, wallet_risk, risk_modifier, and vote
        """
        # Extract inputs
        sentinel_output = input_data.get("sentinel_output", {})
        oracle_output = input_data.get("oracle_output", {})
        policy_id = input_data.get("policy_id", "")
        creator_wallet = input_data.get("creator_wallet", "")
        
        self.log_start(policy_id)
        
        # Step 1: Check sanctions lists
        sanctions_result = await self._check_sanctions(creator_wallet)
        
        # Step 2: Analyze wallet age and behavior
        wallet_analysis = await self._analyze_wallet(creator_wallet)
        
        # Step 3: Identify risk indicators
        risk_indicators = self._identify_risk_indicators(
            sanctions_result, wallet_analysis, policy_id
        )
        
        # Step 4: Calculate risk modifier
        risk_modifier = self._calculate_risk_modifier(
            sanctions_result, wallet_analysis, risk_indicators
        )
        
        # Step 5: Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            sentinel_output, oracle_output, risk_modifier
        )
        
        # Step 6: Determine vote based on compliance assessment
        risk_score = self._calculate_final_risk(
            sentinel_output, oracle_output, risk_modifier
        )
        vote = self.determine_vote(risk_score)
        
        self.log_complete(vote, risk_score)
        
        # Return structured output for ZK-Prover Agent
        return {
            "agent": "compliance",
            "policy_id": policy_id,
            "creator_wallet": creator_wallet,
            "sanctions_match": sanctions_result.get("is_match", False),
            "sanctions_details": {
                "list_name": sanctions_result.get("list_name"),
                "match_confidence": sanctions_result.get("confidence", 0.0)
            },
            "wallet_age_days": wallet_analysis.get("age_days", 0),
            "wallet_risk_indicators": risk_indicators,
            "risk_modifier": risk_modifier,
            "compliance_score": compliance_score,
            "vote": vote.value,
            "risk_score": risk_score,
            "timestamp": self.get_timestamp()
        }
    
    # -------------------------------------------------------------------------
    # SANCTIONS CHECKING
    # -------------------------------------------------------------------------
    
    async def _check_sanctions(self, wallet_address: str) -> Dict[str, Any]:
        """
        Check wallet against sanctions and blacklists.
        
        PLACEHOLDER: Uses mock database for hackathon demo.
        
        Args:
            wallet_address: The Cardano wallet address to check
            
        Returns:
            Dict with is_match, list_name, confidence
        """
        self.logger.debug(f"Checking sanctions for {wallet_address[:20]}...")
        
        # =====================================================================
        # PLACEHOLDER - Mock sanctions check
        # Replace with actual API calls:
        #
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.sanctions_api}/v1/screen",
        #         json={"address": wallet_address, "chain": "cardano"}
        #     )
        #     return response.json()
        # =====================================================================
        
        # Check mock sanctions database
        if wallet_address in MOCK_SANCTIONS_LIST:
            self.logger.critical(f"SANCTIONS MATCH: {wallet_address[:20]}...")
            return {
                "is_match": True,
                "list_name": "OFAC_SDN_MOCK",
                "confidence": 1.0,
                "match_type": "exact"
            }
        
        # Check high-risk prefixes (for demo simulation)
        for prefix in HIGH_RISK_PREFIXES:
            if wallet_address.lower().startswith(f"addr1{prefix}"):
                self.logger.warning(f"High-risk pattern match: {prefix}")
                return {
                    "is_match": True,
                    "list_name": "KNOWN_SCAMMER_DB_MOCK",
                    "confidence": 0.85,
                    "match_type": "pattern"
                }
        
        self.logger.info("No sanctions match found")
        return {
            "is_match": False,
            "list_name": None,
            "confidence": 0.0,
            "match_type": None
        }
    
    # -------------------------------------------------------------------------
    # WALLET ANALYSIS
    # -------------------------------------------------------------------------
    
    async def _analyze_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """
        Analyze wallet age and transaction history.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        
        Args:
            wallet_address: The Cardano wallet address to analyze
            
        Returns:
            Dict with age_days, first_tx, tx_count, behavior patterns
        """
        self.logger.debug(f"Analyzing wallet {wallet_address[:20]}...")
        
        # =====================================================================
        # PLACEHOLDER - Mock wallet analysis
        # Replace with Blockfrost API call:
        #
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"https://cardano-preview.blockfrost.io/api/v0/addresses/{wallet_address}",
        #         headers={"project_id": self.blockfrost_api_key}
        #     )
        #     # Calculate age from first transaction
        # =====================================================================
        
        # Simulate wallet data based on address patterns
        if wallet_address.lower().startswith("addr1dead") or wallet_address.lower().startswith("addr1bad"):
            # New suspicious wallet
            return {
                "age_days": 2,
                "first_tx_timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "tx_count": 5,
                "unique_interactions": 2,
                "has_data": True
            }
        elif wallet_address.lower().startswith("addr1warn"):
            # Moderately new wallet
            return {
                "age_days": 21,
                "first_tx_timestamp": (datetime.utcnow() - timedelta(days=21)).isoformat(),
                "tx_count": 45,
                "unique_interactions": 12,
                "has_data": True
            }
        else:
            # Established wallet
            return {
                "age_days": 365,
                "first_tx_timestamp": (datetime.utcnow() - timedelta(days=365)).isoformat(),
                "tx_count": 500,
                "unique_interactions": 100,
                "has_data": True
            }
    
    def _identify_risk_indicators(
        self,
        sanctions_result: Dict[str, Any],
        wallet_analysis: Dict[str, Any],
        policy_id: str
    ) -> List[Dict[str, Any]]:
        """
        Identify specific risk indicators from analysis.
        
        Args:
            sanctions_result: Sanctions check results
            wallet_analysis: Wallet behavior analysis
            policy_id: The token's policy ID
            
        Returns:
            List of risk indicator dicts
        """
        indicators = []
        
        # Sanctions indicator
        if sanctions_result.get("is_match"):
            indicators.append({
                "indicator": "sanctions_match",
                "severity": RiskLevel.CRITICAL.value,
                "description": f"Wallet matched sanctions list: {sanctions_result.get('list_name')}",
                "weight": 50
            })
        
        # Wallet age indicators
        age_days = wallet_analysis.get("age_days", 0)
        
        if age_days < WALLET_AGE_THRESHOLDS["critical_new"]:
            indicators.append({
                "indicator": "extremely_new_wallet",
                "severity": RiskLevel.CRITICAL.value,
                "description": f"Wallet created < 1 day ago ({age_days} days)",
                "weight": 35
            })
        elif age_days < WALLET_AGE_THRESHOLDS["high_risk"]:
            indicators.append({
                "indicator": "new_wallet",
                "severity": RiskLevel.HIGH.value,
                "description": f"Wallet created < 7 days ago ({age_days} days)",
                "weight": 25
            })
        elif age_days < WALLET_AGE_THRESHOLDS["medium_risk"]:
            indicators.append({
                "indicator": "recent_wallet",
                "severity": RiskLevel.MEDIUM.value,
                "description": f"Wallet created < 30 days ago ({age_days} days)",
                "weight": 15
            })
        
        # Transaction count indicators
        tx_count = wallet_analysis.get("tx_count", 0)
        if tx_count < 10:
            indicators.append({
                "indicator": "low_activity",
                "severity": RiskLevel.MEDIUM.value,
                "description": f"Wallet has very low transaction count ({tx_count})",
                "weight": 10
            })
        
        # Unique interactions
        unique = wallet_analysis.get("unique_interactions", 0)
        if unique < 5:
            indicators.append({
                "indicator": "limited_interactions",
                "severity": RiskLevel.LOW.value,
                "description": f"Wallet has interacted with few unique addresses ({unique})",
                "weight": 5
            })
        
        self.logger.info(f"Identified {len(indicators)} risk indicator(s)")
        return indicators
    
    # -------------------------------------------------------------------------
    # RISK CALCULATION METHODS
    # -------------------------------------------------------------------------
    
    def _calculate_risk_modifier(
        self,
        sanctions_result: Dict[str, Any],
        wallet_analysis: Dict[str, Any],
        risk_indicators: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate the compliance risk modifier (0.5 - 2.0).
        
        This modifier is applied to the base risk score.
        
        Args:
            sanctions_result: Sanctions check results
            wallet_analysis: Wallet behavior analysis
            risk_indicators: List of identified risk indicators
            
        Returns:
            float: Risk modifier from 0.5 to 2.0
        """
        # Start with neutral modifier
        modifier = RISK_MODIFIERS["neutral"]
        
        # Sanctions match = maximum modifier
        if sanctions_result.get("is_match"):
            self.logger.warning("Applying CRITICAL risk modifier due to sanctions match")
            return RISK_MODIFIERS["critical"]
        
        # Calculate indicator weight
        total_weight = sum(ind.get("weight", 0) for ind in risk_indicators)
        
        # Adjust modifier based on total weight
        if total_weight >= 40:
            modifier = RISK_MODIFIERS["high"]
        elif total_weight >= 25:
            modifier = RISK_MODIFIERS["elevated"]
        elif total_weight >= 10:
            modifier = RISK_MODIFIERS["neutral"]
        elif total_weight > 0:
            modifier = RISK_MODIFIERS["low"]
        else:
            # Check if wallet is established
            age_days = wallet_analysis.get("age_days", 0)
            if age_days >= WALLET_AGE_THRESHOLDS["established"]:
                modifier = RISK_MODIFIERS["very_low"]
        
        self.logger.debug(f"Calculated risk modifier: {modifier}")
        return modifier
    
    def _calculate_compliance_score(
        self,
        sentinel_output: Dict[str, Any],
        oracle_output: Dict[str, Any],
        risk_modifier: float
    ) -> int:
        """
        Calculate compliance score (0-100, lower = more compliant).
        
        Args:
            sentinel_output: Risk data from Sentinel
            oracle_output: Risk data from Oracle
            risk_modifier: Our calculated risk modifier
            
        Returns:
            int: Compliance risk score from 0 to 100
        """
        # Get base scores
        sentinel_score = sentinel_output.get("risk_score", 0)
        oracle_score = oracle_output.get("risk_score", 0)
        
        # Average the previous scores
        base_score = (sentinel_score + oracle_score) / 2
        
        # Apply our risk modifier
        compliance_score = base_score * risk_modifier
        
        # Cap at 100
        return min(int(compliance_score), 100)
    
    def _calculate_final_risk(
        self,
        sentinel_output: Dict[str, Any],
        oracle_output: Dict[str, Any],
        risk_modifier: float
    ) -> int:
        """
        Calculate final risk score incorporating all previous agents.
        
        Args:
            sentinel_output: Risk data from Sentinel
            oracle_output: Risk data from Oracle
            risk_modifier: Our compliance risk modifier
            
        Returns:
            int: Final risk score from 0 to 100
        """
        # Weighted combination of all inputs
        sentinel_score = sentinel_output.get("risk_score", 0)
        oracle_score = oracle_output.get("risk_score", 0)
        
        # Combined base (equal weight to both)
        combined_base = (sentinel_score * 0.5) + (oracle_score * 0.5)
        
        # Apply compliance modifier
        final_risk = combined_base * risk_modifier
        
        return min(int(final_risk), 100)
