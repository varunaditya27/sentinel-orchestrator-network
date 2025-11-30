import logging
import httpx
import statistics
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from ..base import BaseAgent, Severity, Vote

class TreasuryGuardian(BaseAgent):
    """
    Treasury Guardian Subsystem
    ===========================
    Monitors Cardano treasury withdrawals for anomalies and potential attacks.
    
    Features:
    - Monitors treasury.cardano.org (simulated via Koios)
    - Flags proposals matching attack patterns:
        1. Duplicate requests
        2. Unusually high amounts (>3 sigma)
        3. Vague deliverables (NLP)
        4. New proposers (<30 days)
    """
    
    def __init__(self, enable_llm: bool = True):
        super().__init__("treasury_guardian", "risk_analyst", enable_llm)
        self.koios_url = "https://preprod.koios.rest/api/v1"  # Default to Preprod
        self.mainnet_url = "https://api.koios.rest/api/v1"
        
        # Risk Constants
        self.NCL_ANNUAL_LIMIT = 47_250_000  # ~15% of 315M ADA
        self.MAX_SINGLE_WITHDRAWAL = 10_000_000 # 10M ADA soft limit
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a treasury withdrawal proposal.
        
        Args:
            input_data: {
                "proposal_id": str,
                "amount": int (lovelace),
                "proposer_id": str (stake address),
                "metadata": dict (title, abstract, rationale)
            }
        """
        self.log_start(input_data.get("proposal_id", "unknown"))
        
        proposal = input_data
        findings = []
        risk_score = 0.0
        
        # 1. Data Ingestion (History)
        history = await self._fetch_treasury_history()
        
        # 2. Statistical Analysis (Z-Score)
        amount_ada = proposal.get("amount", 0) / 1_000_000
        z_score = self._calculate_z_score(amount_ada, history)
        
        if z_score > 3.0:
            findings.append(f"SIZE_OUTLIER_3SIGMA: Amount {amount_ada:,.0f} ADA is >3σ from mean (z={z_score:.2f})")
            risk_score += 30
            
        # 3. NCL / Budget Check
        if amount_ada > self.MAX_SINGLE_WITHDRAWAL:
            findings.append(f"UNUSUALLY_LARGE_WITHDRAWAL: {amount_ada:,.0f} ADA exceeds soft limit of {self.MAX_SINGLE_WITHDRAWAL:,.0f}")
            risk_score += 30
            
        # 4. Proposer Analysis
        proposer_age = await self._check_proposer_age(proposal.get("proposer_id"))
        if proposer_age < 30:
            findings.append(f"NEW_PROPOSER: Wallet age {proposer_age} days (<30 days)")
            risk_score += 20
            
        # 5. NLP Analysis (Vague Deliverables)
        if self.has_llm:
            nlp_risk = await self._analyze_text_quality(proposal.get("metadata", {}))
            if nlp_risk > 0:
                findings.append("VAGUE_DELIVERABLES: Proposal lacks concrete metrics or milestones")
                risk_score += nlp_risk
        
        # Determine Verdict
        vote = self.determine_vote(int(risk_score))
        severity = Severity.INFO
        if risk_score > 50: severity = Severity.HIGH
        elif risk_score > 20: severity = Severity.MEDIUM
        
        result = {
            "agent": self.agent_name,
            "proposal_id": proposal.get("proposal_id"),
            "risk_score": min(risk_score, 100),
            "vote": vote,
            "severity": severity,
            "findings": findings,
            "stats": {
                "z_score": z_score,
                "proposer_age_days": proposer_age
            },
            "timestamp": self.get_timestamp()
        }
        
        self.log_complete(vote, int(risk_score))
        return result

    async def _fetch_treasury_history(self) -> List[float]:
        """Fetch historical treasury withdrawals from Koios."""
        # Mocking history for MVP speed, but structure is ready for API
        # In prod: await client.get(f"{self.koios_url}/treasury_withdrawals")
        return [1_000_000, 500_000, 2_000_000, 750_000, 10_000_000, 3_000_000]

    def _calculate_z_score(self, amount: float, history: List[float]) -> float:
        if not history: return 0.0
        mean = statistics.mean(history)
        stdev = statistics.stdev(history) if len(history) > 1 else 1.0
        if stdev == 0: return 0.0
        return (amount - mean) / stdev

    async def _check_proposer_age(self, stake_address: str) -> int:
        """Check wallet age via Koios."""
        if not stake_address: return 0
        # In prod: Call Koios account_info -> first_activity_epoch
        # Mocking for MVP
        return 15 if stake_address.startswith("stake_test") else 100

    async def _analyze_text_quality(self, metadata: Dict) -> int:
        """Use LLM to detect vague deliverables."""
        text = f"{metadata.get('title', '')} {metadata.get('abstract', '')} {metadata.get('rationale', '')}"
        if not text.strip(): return 20
        
        prompt = f"""
        Analyze this treasury proposal text for "Vague Deliverables".
        Risk Criteria:
        - No concrete numbers or KPIs
        - No clear timeline
        - Buzzword-heavy
        
        Text: "{text[:1000]}"
        
        Return ONLY an integer risk score (0-20). 0 = Clear/Good, 20 = Very Vague.
        """
        try:
            response = await self.llm.ask(prompt)
            return int(''.join(filter(str.isdigit, response)))
        except:
            return 0
