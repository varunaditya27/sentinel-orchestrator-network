"""
PolicyAnalyzer Agent
===================
Checks proposal compliance with Cardano Constitution using Gemini AI.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

@dataclass
class PolicyAnalysis:
    """Result from policy analysis"""
    summary: str
    technical_summary: str
    flags: List[str]
    recommendation: str  # YES, NO, ABSTAIN
    reasoning: str
    confidence: float
    complexity_score: int

class PolicyAnalyzer:
    """
    Agent that analyzes proposals using Gemini 2.0 Flash.
    Checks against hardcoded constitutional rules.
    """
    
    CONSTITUTIONAL_RULES = """
CARDANO GOVERNANCE RULES (Simplified for Demo):

1. TREASURY CAP: Single proposal cannot exceed 50,000,000 ADA
2. DELIVERABLES REQUIRED: Must contain specific milestones/outputs
3. PROPOSER IDENTITY: Must link to verifiable GitHub/forum profile
4. NO DUPLICATES: Cannot request funds for same purpose as recent proposal
5. MARKETING CAP: Marketing budgets capped at 5,000,000 ADA per quarter
6. PROTOCOL CHANGES: Must include technical specification document
7. SPO CONSENSUS: Infrastructure changes require >60% SPO approval

These rules are derived from the Cardano Constitution (simplified).
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SON.PolicyAnalyzer")
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize Gemini
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    'gemini-2.0-flash-exp',
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.3
                    }
                )
                self.logger.info("PolicyAnalyzer initialized with Gemini")
            else:
                self.model = None
                self.logger.warning("GOOGLE_API_KEY not set")
        else:
            self.model = None
            self.logger.warning("google-generativeai not installed")
    
    async def analyze(self, metadata: Dict) -> PolicyAnalysis:
        """
        Analyze proposal for constitutional compliance.
        
        Args:
            metadata: Proposal metadata dict
            
        Returns:
            PolicyAnalysis object with verdict
        """
        
        if not self.model:
            return self._fallback_analysis(metadata)
        
        prompt = f"""
You are a Cardano governance analyst AI. Analyze this proposal for compliance.

PROPOSAL DETAILS:
Title: {metadata['title']}
Abstract: {metadata['abstract']}
Motivation: {metadata['motivation'][:1000]}
Rationale: {metadata['rationale'][:1000]}
Amount Requested: {metadata.get('amount', 0) / 1_000_000:,.0f} ADA

RULES TO CHECK:
{self.CONSTITUTIONAL_RULES}

OUTPUT FORMAT (strict JSON):
{{
  "summary": "3-sentence plain English summary for non-technical users",
  "technical_summary": "2-sentence technical assessment for developers",
  "flags": [
    "FLAG_NAME_1: Brief explanation",
    "FLAG_NAME_2: Brief explanation"
  ],
  "recommendation": "YES" | "NO" | "ABSTAIN",
  "reasoning": "Why you chose this recommendation (max 2 sentences)",
  "confidence": 0.0-1.0,
  "complexity_score": 1-10
}}

CRITICAL: If amount > 50M ADA, FLAG it. If no deliverables mentioned, FLAG it.
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis_dict = json.loads(response.text)
            
            return PolicyAnalysis(
                summary=analysis_dict.get('summary', 'Analysis unavailable'),
                technical_summary=analysis_dict.get('technical_summary', ''),
                flags=analysis_dict.get('flags', []),
                recommendation=analysis_dict.get('recommendation', 'ABSTAIN'),
                reasoning=analysis_dict.get('reasoning', ''),
                confidence=analysis_dict.get('confidence', 0.5),
                complexity_score=analysis_dict.get('complexity_score', 5)
            )
            
        except Exception as e:
            self.logger.error(f"Gemini analysis failed: {e}")
            return self._fallback_analysis(metadata)
    
    def _fallback_analysis(self, metadata: Dict) -> PolicyAnalysis:
        """Rule-based fallback when Gemini unavailable"""
        amount = metadata.get('amount', 0)
        flags = []
        
        # Check treasury cap
        if amount > 50_000_000_000_000:  # 50M ADA in lovelace
            flags.append("TREASURY_CAP_VIOLATION: Amount exceeds 50M ADA limit")
        
        # Check for deliverables
        text = (metadata.get('motivation', '') + metadata.get('rationale', '')).lower()
        if 'deliverable' not in text and 'milestone' not in text:
            flags.append("VAGUE_DELIVERABLES: No specific milestones mentioned")
        
        recommendation = "NO" if len(flags) >= 2 else ("ABSTAIN" if flags else "YES")
        
        return PolicyAnalysis(
            summary="Automated rule-based analysis (Gemini unavailable)",
            technical_summary="Checked treasury cap and deliverables presence",
            flags=flags,
            recommendation=recommendation,
            reasoning=f"Found {len(flags)} compliance issues",
            confidence=0.6,
            complexity_score=5
        )
    
    def generate_log(self, analysis: PolicyAnalysis) -> str:
        """Generate Matrix-style terminal log output"""
        flags_str = "\n".join([f"   ⚠️  {flag}" for flag in analysis.flags])
        
        return f"""
[POLICY ANALYZER] Analysis Complete
├─ Recommendation: {analysis.recommendation}
├─ Confidence: {analysis.confidence:.0%}
├─ Flags Raised: {len(analysis.flags)}
{flags_str if flags_str else '   ✓ No compliance issues detected'}
└─ Reasoning: {analysis.reasoning}
        """
