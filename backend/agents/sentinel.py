"""
=============================================================================
Sentinel Orchestrator Network (SON) - AGENT A: Sentinel Agent (Detection)
=============================================================================

Role: Primary detector & analyzer
CrewAI Role Type: expert_detector
Masumi Pricing: Per scan (fixed)

This agent scans Cardano policy IDs for threats using heuristic patterns.
It's the first agent in the pipeline and produces findings for other agents.

=============================================================================
"""

import re
from typing import Any, Dict, List, Optional
from .base import BaseAgent, Vote, Severity


# =============================================================================
# THREAT PATTERNS - Regex patterns for detecting vulnerabilities
# =============================================================================

THREAT_PATTERNS = {
    "mint_unlimited": {
        "pattern": r"(mint|forge|create).*unlimited|no.*limit.*mint",
        "severity": Severity.CRITICAL,
        "description": "Contract allows unlimited token minting",
        "weight": 40  # How much this adds to risk score
    },
    "rugpull_pattern": {
        "pattern": r"(withdraw|drain|remove).*all|owner.*withdraw",
        "severity": Severity.CRITICAL,
        "description": "Potential rugpull - owner can withdraw all funds",
        "weight": 35
    },
    "honeypot": {
        "pattern": r"transfer.*disabled|no.*sell|only.*buy",
        "severity": Severity.HIGH,
        "description": "Honeypot pattern - users may not be able to sell",
        "weight": 30
    },
    "admin_backdoor": {
        "pattern": r"admin.*override|owner.*control|pause.*all",
        "severity": Severity.MEDIUM,
        "description": "Admin has excessive control over contract",
        "weight": 20
    },
    "hidden_fee": {
        "pattern": r"fee.*[5-9][0-9]|tax.*[1-9][0-9]",
        "severity": Severity.MEDIUM,
        "description": "Suspiciously high transaction fees detected",
        "weight": 15
    },
    "proxy_risk": {
        "pattern": r"delegatecall|proxy.*upgrade|implementation.*change",
        "severity": Severity.LOW,
        "description": "Upgradeable contract - logic can be changed",
        "weight": 10
    }
}


# =============================================================================
# SENTINEL AGENT CLASS
# =============================================================================

class SentinelAgent(BaseAgent):
    """
    Agent A: Primary threat detector for Cardano smart contracts.
    
    This agent:
    1. Fetches contract data from Blockfrost (PLACEHOLDER for now)
    2. Runs regex-based threat detection patterns
    3. Calculates a risk score (0-100)
    4. Generates an evidence hash of findings
    5. Casts a vote (SAFE/WARNING/DANGER)
    
    Performance: Must complete in < 2 seconds
    """
    
    def __init__(self, blockfrost_api_key: Optional[str] = None):
        """
        Initialize the Sentinel Agent.
        
        Args:
            blockfrost_api_key: API key for Blockfrost (optional, uses mock if None)
        """
        super().__init__(agent_name="sentinel", role="expert_detector")
        
        # Store API key for Blockfrost integration
        # PLACEHOLDER: In production, this would connect to real Blockfrost
        self.blockfrost_api_key = blockfrost_api_key
        self.use_mock = blockfrost_api_key is None
        
        if self.use_mock:
            self.logger.warning("Running in MOCK mode - using simulated contract data")
    
    # -------------------------------------------------------------------------
    # MAIN PROCESSING METHOD
    # -------------------------------------------------------------------------
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - analyze a policy ID for threats.
        
        Args:
            input_data: {
                "schema_version": "1.0",
                "policy_id": "<hex_string>",
                "scan_depth": "standard" | "deep" (optional),
                "timestamp": "<ISO 8601>"
            }
            
        Returns:
            Dict with risk_score, findings, evidence_hash, and vote
        """
        # Extract policy ID from input
        policy_id = input_data.get("policy_id", "")
        scan_depth = input_data.get("scan_depth", "standard")
        
        self.log_start(policy_id)
        
        # Step 1: Fetch contract data (PLACEHOLDER - returns mock data)
        contract_data = await self._fetch_contract_data(policy_id)
        
        # Step 2: Run threat detection heuristics
        findings = self._run_heuristics(contract_data)
        
        # Step 3: Calculate risk score from findings
        risk_score = self._calculate_risk_score(findings)
        
        # Step 4: Generate evidence hash
        evidence_hash = self._generate_evidence_hash(findings, policy_id)
        
        # Step 5: Determine vote based on score
        vote = self.determine_vote(risk_score)
        
        self.log_complete(vote, risk_score)
        
        # Return structured output for next agent (Oracle)
        return {
            "agent": "sentinel",
            "policy_id": policy_id,
            "risk_score": risk_score,
            "findings": findings,
            "evidence_hash": evidence_hash,
            "timestamp": self.get_timestamp(),
            "vote": vote.value
        }
    
    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------
    
    async def _fetch_contract_data(self, policy_id: str) -> Dict[str, Any]:
        """
        Fetch contract CBOR, metadata, and source from Blockfrost.
        
        PLACEHOLDER: Returns mock data for hackathon demo.
        In production, this would call Blockfrost API.
        
        Args:
            policy_id: The Cardano policy ID to look up
            
        Returns:
            Dict containing script_cbor, metadata, and other contract info
        """
        self.logger.debug(f"Fetching contract data for {policy_id[:16]}...")
        
        # =====================================================================
        # PLACEHOLDER - Mock contract data for demo
        # Replace with actual Blockfrost API call:
        # 
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"https://cardano-preview.blockfrost.io/api/v0/scripts/{policy_id}",
        #         headers={"project_id": self.blockfrost_api_key}
        #     )
        #     return response.json()
        # =====================================================================
        
        # Simulate different contract types based on policy_id patterns
        # This allows demo testing with different policy IDs
        
        if policy_id.startswith("dead") or policy_id.startswith("bad"):
            # Dangerous mock contract
            mock_source = """
                mint unlimited tokens allowed
                owner can withdraw all funds
                transfer disabled for non-owner
                admin override enabled
            """
        elif policy_id.startswith("warn"):
            # Warning-level mock contract
            mock_source = """
                standard token contract
                admin pause all capability
                fee 15 percent on transfer
            """
        else:
            # Safe mock contract
            mock_source = """
                standard CIP-68 token implementation
                no special admin privileges
                normal transfer functionality
            """
        
        return {
            "policy_id": policy_id,
            "script_cbor": "PLACEHOLDER_CBOR_DATA",
            "source_code": mock_source,
            "metadata": {
                "name": "Mock Token",
                "ticker": "MOCK"
            },
            "created_at": self.get_timestamp()
        }
    
    def _run_heuristics(self, contract_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run threat detection patterns against contract source code.
        
        Uses regex patterns defined in THREAT_PATTERNS to identify
        potential vulnerabilities and malicious code patterns.
        
        Args:
            contract_data: Contract information including source_code
            
        Returns:
            List of finding dicts with type, severity, description
        """
        findings = []
        source_code = contract_data.get("source_code", "").lower()
        
        self.logger.debug("Running heuristic threat detection...")
        
        # Check each threat pattern against the source code
        for threat_type, pattern_info in THREAT_PATTERNS.items():
            pattern = pattern_info["pattern"]
            
            # Use regex to search for the pattern
            if re.search(pattern, source_code, re.IGNORECASE):
                finding = {
                    "type": threat_type,
                    "severity": pattern_info["severity"].value,
                    "description": pattern_info["description"],
                    "weight": pattern_info["weight"],
                    "matched": True
                }
                findings.append(finding)
                self.logger.warning(f"THREAT DETECTED: {threat_type} ({pattern_info['severity'].value})")
        
        if not findings:
            self.logger.info("No threats detected in contract")
        else:
            self.logger.info(f"Detected {len(findings)} potential threat(s)")
        
        return findings
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> int:
        """
        Calculate overall risk score from findings.
        
        Aggregates weights from all findings, capped at 100.
        Empty findings = 0 (safe).
        
        Args:
            findings: List of threat findings with weights
            
        Returns:
            int: Risk score from 0 to 100
        """
        if not findings:
            return 0
        
        # Sum all finding weights
        total_weight = sum(f.get("weight", 0) for f in findings)
        
        # Cap at 100
        risk_score = min(total_weight, 100)
        
        self.logger.debug(f"Calculated risk score: {risk_score}")
        return risk_score
    
    def _generate_evidence_hash(self, findings: List[Dict[str, Any]], policy_id: str) -> str:
        """
        Generate SHA-256 hash of all findings for immutability.
        
        This hash can be verified later to prove findings weren't tampered with.
        
        Args:
            findings: List of threat findings
            policy_id: The policy ID being analyzed
            
        Returns:
            str: 64-character hex hash
        """
        # Create a deterministic string from findings
        evidence_string = f"{policy_id}|{self.get_timestamp()}|"
        
        for finding in sorted(findings, key=lambda x: x.get("type", "")):
            evidence_string += f"{finding.get('type', '')}:{finding.get('severity', '')}|"
        
        return self.generate_hash(evidence_string)
