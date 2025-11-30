"""
ProposalFetcher Agent
====================
Fetches governance proposal metadata from IPFS and Blockfrost.
"""

import httpx
import json
import logging
import os
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

from dotenv import load_dotenv
from ..llm_config import AgentLLM

@dataclass
class ProposalMetadata:
    """Structured proposal metadata"""
    title: str
    abstract: str
    motivation: str
    rationale: str
    amount: int  # In lovelace
    ipfs_hash: str
    references: List[str]
    error: Optional[str] = None

class ProposalFetcher:
    """
    Agent responsible for fetching proposal metadata from IPFS.
    Supports CIP-100/108 format.
    """
    
    # Multiple IPFS gateways for redundancy
    IPFS_GATEWAYS = [
        "https://ipfs.io/ipfs/",
        "https://cloudflare-ipfs.com/ipfs/",
        "https://gateway.pinata.cloud/ipfs/",
        "https://dweb.link/ipfs/"
    ]
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.logger = logging.getLogger("SON.ProposalFetcher")
        self.llm = AgentLLM("ProposalFetcher")
        self.logger.info("ProposalFetcher initialized with LLM capabilities")
    
    async def fetch_metadata(
        self,
        ipfs_hash: str,
        timeout: int = 15
    ) -> ProposalMetadata:
        """
        Fetch CIP-100/108 metadata from IPFS with fallback gateways.
        
        Args:
            ipfs_hash: IPFS content hash (e.g., "QmXyz...")
            timeout: Request timeout in seconds
            
        Returns:
            ProposalMetadata object with parsed data
        """
        # Validation
        if not ipfs_hash:
            raise ValueError("IPFS Hash is required")
            
        if ipfs_hash.startswith("gov_action"):
            raise ValueError(f"Invalid IPFS Hash: '{ipfs_hash}'. This looks like a Governance Action ID. Please enter a valid IPFS CID (starting with Qm... or bafy...).")
            
        # Basic CID validation (length check)
        if len(ipfs_hash) < 40:
             raise ValueError(f"Invalid IPFS Hash: '{ipfs_hash}'. Too short.")

        for gateway in self.IPFS_GATEWAYS:
            url = f"{gateway}{ipfs_hash}"
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        metadata = response.json()
                        
                        # Validate CIP-100 structure
                        if "body" in metadata:
                            body = metadata['body']
                            return ProposalMetadata(
                                title=body.get('title', 'Untitled Proposal'),
                                abstract=body.get('abstract', '')[:500],
                                motivation=body.get('motivation', '')[:2000],
                                rationale=body.get('rationale', '')[:2000],
                                amount=body.get('amount', 0),
                                references=body.get('references', [])[:5],
                                ipfs_hash=ipfs_hash
                            )
                        
            except Exception as e:
                self.logger.debug(f"Gateway {gateway} failed: {e}")
                continue
        
        # All gateways failed
        raise ValueError(f"IPFS Hash {ipfs_hash} not found or unreachable")
    
    async def analyze_proposal_content(
        self,
        metadata: ProposalMetadata
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to analyze proposal content for quality, risks, and feasibility.
        
        Args:
            metadata: The proposal metadata to analyze
            
        Returns:
            Dict with analysis results or None if LLM unavailable
        """
        if not self.llm.is_available:
            self.logger.debug("LLM not available for proposal analysis")
            return None
        
        if metadata.error:
            self.logger.debug("Skipping LLM analysis for failed metadata fetch")
            return None
        
        try:
            prompt = self._build_proposal_analysis_prompt(metadata)
            analysis_text = await self.llm._generate_content(prompt)
            
            # Parse the analysis into structured format
            return self._parse_proposal_analysis(analysis_text)
            
        except Exception as e:
            self.logger.error(f"LLM proposal analysis failed: {e}")
            return None
    
    def _build_proposal_analysis_prompt(self, metadata: ProposalMetadata) -> str:
        """Build prompt for proposal content analysis."""
        return f"""You are a Cardano governance expert analyzing a governance proposal.

**PROPOSAL ANALYSIS REQUEST**

Title: {metadata.title}
Abstract: {metadata.abstract}
Motivation: {metadata.motivation}
Rationale: {metadata.rationale}
Funding Amount: {metadata.amount / 1_000_000:,.0f} ADA
References: {len(metadata.references)} provided

**ANALYSIS REQUIREMENTS**

Provide a structured analysis covering:

1. **CONTENT QUALITY** (1-10 scale):
   - Completeness of proposal details
   - Clarity of objectives and rationale
   - Technical specification quality

2. **RISK ASSESSMENT** (LOW/MEDIUM/HIGH):
   - Financial risks (budget justification, sustainability)
   - Technical risks (implementation feasibility)
   - Governance risks (centralization concerns, community impact)

3. **ALIGNMENT WITH CARDANO PRINCIPLES** (1-10 scale):
   - Decentralization principles
   - Community governance values
   - Technical excellence standards

4. **OVERALL RECOMMENDATION** (APPROVE/CONDITIONAL/REJECT):
   - Brief justification for the recommendation

**FORMAT YOUR RESPONSE AS:**
CONTENT_QUALITY: [score]/10 - [brief explanation]
RISK_LEVEL: [LOW/MEDIUM/HIGH] - [key risks identified]
ALIGNMENT_SCORE: [score]/10 - [alignment assessment]
RECOMMENDATION: [APPROVE/CONDITIONAL/REJECT] - [justification]

Keep each section concise (1-2 sentences)."""
    
    def _parse_proposal_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the LLM analysis response into structured data."""
        result = {
            "content_quality": {"score": 5, "explanation": "Analysis unavailable"},
            "risk_assessment": {"level": "MEDIUM", "details": "Analysis unavailable"},
            "alignment_score": {"score": 5, "explanation": "Analysis unavailable"},
            "recommendation": {"decision": "CONDITIONAL", "justification": "Analysis unavailable"}
        }
        
        try:
            lines = analysis_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('CONTENT_QUALITY:'):
                    parts = line.replace('CONTENT_QUALITY:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        score_part = parts[0].strip()
                        if '/' in score_part:
                            score = int(score_part.split('/')[0])
                            result["content_quality"] = {"score": score, "explanation": parts[1].strip()}
                
                elif line.startswith('RISK_LEVEL:'):
                    parts = line.replace('RISK_LEVEL:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        level = parts[0].strip().upper()
                        if level in ['LOW', 'MEDIUM', 'HIGH']:
                            result["risk_assessment"] = {"level": level, "details": parts[1].strip()}
                
                elif line.startswith('ALIGNMENT_SCORE:'):
                    parts = line.replace('ALIGNMENT_SCORE:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        score_part = parts[0].strip()
                        if '/' in score_part:
                            score = int(score_part.split('/')[0])
                            result["alignment_score"] = {"score": score, "explanation": parts[1].strip()}
                
                elif line.startswith('RECOMMENDATION:'):
                    parts = line.replace('RECOMMENDATION:', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        decision = parts[0].strip().upper()
                        if decision in ['APPROVE', 'CONDITIONAL', 'REJECT']:
                            result["recommendation"] = {"decision": decision, "justification": parts[1].strip()}
        
        except Exception as e:
            self.logger.error(f"Failed to parse proposal analysis: {e}")
        
        return result
    
    def generate_log(self, metadata: ProposalMetadata, analysis: Optional[Dict[str, Any]] = None) -> str:
        """Generate Matrix-style terminal log output"""
        log_lines = [
            "[PROPOSAL FETCHER] Metadata Retrieved",
            f"├─ Title: {metadata.title[:50]}",
            f"├─ Amount: {metadata.amount / 1_000_000:,.0f} ADA",
            f"├─ IPFS Hash: {metadata.ipfs_hash[:16]}...",
            f"└─ Status: {'✓ Success' if not metadata.error else '✗ ' + metadata.error}"
        ]
        
        if analysis:
            log_lines.extend([
                "",
                "[PROPOSAL FETCHER] LLM Analysis",
                f"├─ Content Quality: {analysis.get('content_quality', {}).get('score', 'N/A')}/10",
                f"├─ Risk Level: {analysis.get('risk_assessment', {}).get('level', 'N/A')}",
                f"├─ Alignment Score: {analysis.get('alignment_score', {}).get('score', 'N/A')}/10",
                f"└─ Recommendation: {analysis.get('recommendation', {}).get('decision', 'N/A')}"
            ])
        
        return "\n".join(log_lines)
