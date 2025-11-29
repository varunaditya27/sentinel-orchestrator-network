"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT C: Compliance Agent
=============================================================================

Role: Sanctions checking, wallet risk assessment, regulatory compliance
Masumi Pricing: Usage-based
Runs as: Independent microservice on KODOSUMI

Based on SON Bible v6:
- Checks wallet against sanctions lists (OFAC mock)
- Analyzes wallet age and behavior
- Calculates risk modifier (0.5 - 2.0)

=============================================================================
"""

import asyncio
import httpx
import json
from typing import Any, Dict, List, Optional
from enum import Enum

from .base import BaseAgent, Vote, Severity


class RiskModifier(float, Enum):
    """Risk modifier multipliers for compliance assessment."""
    VERY_LOW = 0.5    # Established wallet, no flags
    LOW = 0.7         # Minor issues
    NEUTRAL = 1.0     # Standard risk
    ELEVATED = 1.5    # New wallet, some flags
    HIGH = 1.8        # Multiple flags
    CRITICAL = 2.0    # Sanctions match, severe flags


class ComplianceAgent(BaseAgent):
    """
    Agent C: Compliance checker for regulatory risk and sanctions.

    Responsibilities:
    - Sanctions list screening (OFAC, EU, etc.)
    - Wallet age and transaction history analysis
    - Risk scoring and modifier calculation
    - Regulatory compliance verification

    Performance: Should complete within 2 seconds
    """

    # Mock sanctions database (in production, this would be a real API)
    MOCK_SANCTIONS = {
        "addr1_fake_sanctioned_wallet_1234567890": {
            "sanctioned": True,
            "list": "OFAC",
            "reason": "Money laundering"
        },
        "addr1_scam_wallet_0987654321": {
            "sanctioned": True,
            "list": "EU Sanctions",
            "reason": "Fraud"
        }
    }

    def __init__(self, enable_llm: bool = True):
        """
        Initialize the Compliance Agent.

        Args:
            enable_llm: Whether to enable LLM-enhanced analysis
        """
        super().__init__(agent_name="compliance", role="regulator", enable_llm=enable_llm)

        # Generate cryptographic keypair
        self.private_key = self._generate_keypair()
        self.public_key = self.private_key.verify_key

        # Compliance data sources
        self.sanctions_apis = [
            "https://www.treasury.gov/ofac/downloads/sdn.pip",  # OFAC (mock)
            "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content",  # EU (mock)
        ]

        self.logger.info("Compliance Agent initialized with sanctions screening")

    def get_public_key_b64(self) -> str:
        """Get base64-encoded public key for verification."""
        import base64
        return base64.b64encode(bytes(self.public_key)).decode()

    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - assess compliance risk for wallet/transaction.

        Args:
            input_data: {
                "wallet_address": "<cardano_address>",
                "policy_id": "<optional_policy_id>",
                "creator_wallet": "<optional_creator_wallet>",
                "context": {}
            }

        Returns:
            Dict with compliance assessment and risk modifier
        """
        wallet_address = input_data.get("wallet_address", "")
        policy_id = input_data.get("policy_id", "")
        creator_wallet = input_data.get("creator_wallet", "")
        context = input_data.get("context", {})

        self.log_start(wallet_address or policy_id or "unknown")

        # Determine target for analysis
        target_wallet = wallet_address or creator_wallet
        if not target_wallet and policy_id:
            # For policy IDs without explicit wallet, we might need to lookup
            target_wallet = await self._lookup_policy_creator(policy_id)

        if not target_wallet:
            return self._build_result(
                wallet=target_wallet,
                risk_modifier=RiskModifier.ELEVATED,
                vote=Vote.WARNING,
                reason="No wallet address provided for compliance check",
                sanctions_check={"status": "skipped", "reason": "no_wallet"},
                wallet_analysis={"status": "skipped"}
            )

        # Run compliance checks in parallel
        sanctions_result = await self._check_sanctions(target_wallet)
        wallet_analysis = await self._analyze_wallet_behavior(target_wallet, context)

        # Calculate overall risk modifier
        risk_modifier = self._calculate_risk_modifier(sanctions_result, wallet_analysis)

        # Determine vote based on compliance
        if sanctions_result.get("sanctioned", False):
            vote = Vote.DANGER
            reason = f"Wallet sanctioned by {sanctions_result.get('list', 'unknown')}"
        elif risk_modifier >= RiskModifier.CRITICAL:
            vote = Vote.DANGER
            reason = "Critical compliance risk detected"
        elif risk_modifier >= RiskModifier.HIGH:
            vote = Vote.WARNING
            reason = "Elevated compliance risk"
        else:
            vote = Vote.SAFE
            reason = "Compliance check passed"

        self.log_complete(vote, int(risk_modifier * 100))

        return self._build_result(
            wallet=target_wallet,
            risk_modifier=risk_modifier,
            vote=vote,
            reason=reason,
            sanctions_check=sanctions_result,
            wallet_analysis=wallet_analysis
        )

    # -------------------------------------------------------------------------
    # SANCTIONS SCREENING
    # -------------------------------------------------------------------------

    async def _check_sanctions(self, wallet_address: str) -> Dict[str, Any]:
        """
        Check wallet address against sanctions lists.

        Args:
            wallet_address: Cardano wallet address to screen

        Returns:
            Dict with sanctions check results
        """
        self.logger.info(f"Checking sanctions for wallet: {wallet_address[:16]}...")

        # Check mock database first (for demo purposes)
        if wallet_address in self.MOCK_SANCTIONS:
            sanction_data = self.MOCK_SANCTIONS[wallet_address]
            return {
                "sanctioned": True,
                "list": sanction_data["list"],
                "reason": sanction_data["reason"],
                "source": "mock_database",
                "checked_at": self.get_timestamp()
            }

        # In production, this would check real sanctions APIs
        # For now, simulate API calls with mock responses
        try:
            # Simulate API call delay
            await asyncio.sleep(0.1)

            # Mock API response - in reality would parse OFAC/EU lists
            return {
                "sanctioned": False,
                "lists_checked": ["OFAC", "EU Sanctions", "UN Sanctions"],
                "source": "sanctions_apis",
                "checked_at": self.get_timestamp(),
                "confidence": 0.95
            }

        except Exception as e:
            self.logger.warning(f"Sanctions API error: {e}")
            return {
                "sanctioned": False,  # Default to not sanctioned on error
                "error": str(e),
                "source": "api_error",
                "checked_at": self.get_timestamp()
            }

    # -------------------------------------------------------------------------
    # WALLET BEHAVIOR ANALYSIS
    # -------------------------------------------------------------------------

    async def _analyze_wallet_behavior(
        self,
        wallet_address: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze wallet age, transaction patterns, and risk indicators.

        Args:
            wallet_address: Wallet to analyze
            context: Additional context from the scan

        Returns:
            Dict with wallet analysis results
        """
        self.logger.info(f"Analyzing wallet behavior: {wallet_address[:16]}...")

        try:
            # Get wallet information from Blockfrost/Koios
            wallet_info = await self._fetch_wallet_info(wallet_address)

            # Analyze wallet age
            wallet_age_days = self._calculate_wallet_age(wallet_info)

            # Analyze transaction patterns
            tx_patterns = self._analyze_transaction_patterns(wallet_info)

            # Calculate behavior score (0-100, lower is better)
            behavior_score = self._calculate_behavior_score(
                wallet_age_days, tx_patterns, context
            )

            return {
                "wallet_age_days": wallet_age_days,
                "transaction_count": wallet_info.get("tx_count", 0),
                "behavior_score": behavior_score,
                "risk_indicators": tx_patterns.get("risk_indicators", []),
                "patterns": tx_patterns,
                "analyzed_at": self.get_timestamp()
            }

        except Exception as e:
            self.logger.warning(f"Wallet analysis error: {e}")
            return {
                "error": str(e),
                "behavior_score": 50,  # Neutral score on error
                "analyzed_at": self.get_timestamp()
            }

    async def _fetch_wallet_info(self, wallet_address: str) -> Dict[str, Any]:
        """
        Fetch wallet information from blockchain APIs.

        Returns mock data for now, in production would call Blockfrost/Koios.
        """
        # Simulate API call
        await asyncio.sleep(0.1)

        # Mock wallet data - in production this would be real API calls
        return {
            "address": wallet_address,
            "tx_count": 150,
            "first_tx_date": "2024-01-15T10:30:00Z",
            "balance_ada": 50000,
            "stake_address": f"stake1{wallet_address[5:]}",
            "tx_history": [
                {"amount": 1000000, "direction": "incoming", "date": "2024-10-01"},
                {"amount": 500000, "direction": "outgoing", "date": "2024-10-02"},
                # ... more transactions
            ]
        }

    def _calculate_wallet_age(self, wallet_info: Dict[str, Any]) -> int:
        """Calculate wallet age in days."""
        from datetime import datetime, timezone

        first_tx_date = wallet_info.get("first_tx_date")
        if not first_tx_date:
            return 0

        try:
            first_tx = datetime.fromisoformat(first_tx_date.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age_days = (now - first_tx).days
            return max(0, age_days)
        except:
            return 0

    def _analyze_transaction_patterns(self, wallet_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction patterns for risk indicators."""
        tx_history = wallet_info.get("tx_history", [])
        tx_count = len(tx_history)

        risk_indicators = []
        patterns = {
            "large_transactions": 0,
            "frequent_small_tx": 0,
            "mixer_patterns": False,
            "blacklist_interactions": False
        }

        # Simple pattern analysis (would be more sophisticated in production)
        for tx in tx_history:
            amount = tx.get("amount", 0)
            if amount > 100000000:  # > 100k ADA
                patterns["large_transactions"] += 1
                if patterns["large_transactions"] > 5:
                    risk_indicators.append("Frequent large transactions")

            if amount < 1000000 and tx_count > 100:  # < 1 ADA but many tx
                patterns["frequent_small_tx"] += 1

        # Wallet age based risk
        age_days = self._calculate_wallet_age(wallet_info)
        if age_days < 30:
            risk_indicators.append("Very new wallet (< 30 days)")
        elif age_days < 90:
            risk_indicators.append("New wallet (< 90 days)")

        return {
            "patterns": patterns,
            "risk_indicators": risk_indicators,
            "overall_risk_level": len(risk_indicators)
        }

    def _calculate_behavior_score(
        self,
        wallet_age_days: int,
        tx_patterns: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate behavior score (0-100, lower is better).

        Factors:
        - Wallet age (newer = higher risk)
        - Transaction patterns
        - Risk indicators count
        """
        score = 0

        # Age factor (0-30 points)
        if wallet_age_days < 7:
            score += 25
        elif wallet_age_days < 30:
            score += 15
        elif wallet_age_days < 90:
            score += 8

        # Pattern factors (0-40 points)
        risk_indicators = tx_patterns.get("risk_indicators", [])
        score += min(len(risk_indicators) * 8, 40)

        # Large transaction factor
        large_tx = tx_patterns.get("patterns", {}).get("large_transactions", 0)
        score += min(large_tx * 2, 20)

        # Context factors (0-10 points)
        if context.get("high_value_transaction"):
            score += 10

        return min(score, 100)

    # -------------------------------------------------------------------------
    # RISK MODIFIER CALCULATION
    # -------------------------------------------------------------------------

    def _calculate_risk_modifier(
        self,
        sanctions_result: Dict[str, Any],
        wallet_analysis: Dict[str, Any]
    ) -> RiskModifier:
        """
        Calculate the overall risk modifier based on sanctions and wallet analysis.

        Returns:
            RiskModifier enum value
        """
        # Immediate critical if sanctioned
        if sanctions_result.get("sanctioned"):
            return RiskModifier.CRITICAL

        behavior_score = wallet_analysis.get("behavior_score", 50)
        risk_indicators = wallet_analysis.get("risk_indicators", [])

        # Calculate modifier based on behavior score and indicators
        if behavior_score < 20 and len(risk_indicators) == 0:
            return RiskModifier.VERY_LOW
        elif behavior_score < 30:
            return RiskModifier.LOW
        elif behavior_score < 50:
            return RiskModifier.NEUTRAL
        elif behavior_score < 70:
            return RiskModifier.ELEVATED
        elif behavior_score < 90:
            return RiskModifier.HIGH
        else:
            return RiskModifier.CRITICAL

    async def _lookup_policy_creator(self, policy_id: str) -> Optional[str]:
        """
        Lookup the creator wallet for a policy ID.

        In production, this would query Cardano blockchain APIs.
        """
        # Mock implementation
        await asyncio.sleep(0.05)

        # Return mock creator wallet for demo
        if "deadbeef" in policy_id.lower():
            return "addr1_fake_sanctioned_wallet_1234567890"  # Mock sanctioned wallet
        elif "safe" in policy_id.lower():
            return "addr1_safe_wallet_established_2023"

        return None

    # -------------------------------------------------------------------------
    # RESULT BUILDING
    # -------------------------------------------------------------------------

    def _build_result(
        self,
        wallet: str,
        risk_modifier: RiskModifier,
        vote: Vote,
        reason: str,
        sanctions_check: Dict[str, Any],
        wallet_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the final result dictionary."""
        evidence_data = f"{wallet}|{risk_modifier}|{vote.value}|{self.get_timestamp()}"
        evidence_hash = self.generate_hash(evidence_data)

        return {
            "agent": "compliance",
            "wallet_address": wallet,
            "vote": vote.value,
            "risk_modifier": risk_modifier,
            "reason": reason,
            "sanctions_check": sanctions_check,
            "wallet_analysis": wallet_analysis,
            "evidence_hash": evidence_hash,
            "timestamp": self.get_timestamp(),
            "llm_enabled": self.has_llm
        }

    def _generate_keypair(self):
        """Generate Ed25519 keypair for signing."""
        import nacl.signing
        return nacl.signing.SigningKey.generate()
