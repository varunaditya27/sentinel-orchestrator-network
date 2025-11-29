"""
=============================================================================
Sentinel Orchestrator Network (SON) - LLM Configuration
=============================================================================

This module provides the Gemini LLM configuration for all SON agents.
It initializes the Google Generative AI client and provides helper functions
for agent reasoning capabilities.

Simplified Architecture (2 Agents):
- Sentinel: Uses LLM for compliance explanation and verdict reasoning
- Oracle: Uses LLM for fork detection analysis

=============================================================================
"""

import os
import logging
from typing import Any, Dict, List, Optional

# Try to import google.generativeai, handle gracefully if not installed
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() == "true"

logger = logging.getLogger("SON.llm")


# =============================================================================
# LLM CLIENT INITIALIZATION
# =============================================================================

def init_gemini_client() -> bool:
    """Initialize the Gemini API client."""
    if not GEMINI_AVAILABLE:
        logger.warning("google-generativeai package not installed. LLM features disabled.")
        return False
    
    if not GEMINI_API_KEY:
        logger.warning("GOOGLE_API_KEY not set in environment. LLM features disabled.")
        return False
    
    if not LLM_ENABLED:
        logger.info("LLM features disabled via LLM_ENABLED=false")
        return False
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info(f"Gemini client initialized with model: {GEMINI_MODEL}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return False


def get_gemini_model():
    """Get the configured Gemini model instance."""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY or not LLM_ENABLED:
        return None
    
    try:
        return genai.GenerativeModel(GEMINI_MODEL)
    except Exception as e:
        logger.error(f"Failed to get Gemini model: {e}")
        return None


# =============================================================================
# LLM HELPER CLASS
# =============================================================================

class AgentLLM:
    """
    LLM helper class for SON agents.
    
    Provides methods for:
    - Compliance analysis explanation (Sentinel)
    - Fork detection reasoning (Oracle)
    - Verdict explanation
    """
    
    def __init__(self, agent_name: str):
        """Initialize the LLM helper for a specific agent."""
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"SON.{agent_name}.llm")
        self.model = None
        self.enabled = False
        
        if init_gemini_client():
            self.model = get_gemini_model()
            self.enabled = self.model is not None
            if self.enabled:
                self.logger.info(f"LLM enabled for {agent_name} agent")
            else:
                self.logger.warning(f"LLM model not available for {agent_name} agent")
        else:
            self.logger.info(f"LLM disabled for {agent_name} agent - using rule-based logic only")
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available for use."""
        return self.enabled and self.model is not None
    
    async def explain_verdict(
        self,
        verdict: str,
        score: int,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate a natural language explanation for a verdict.
        
        Args:
            verdict: SAFE, WARNING, or DANGER
            score: Risk score (0-100)
            reason: The rule-based reason for the verdict
            context: Additional context (compliance checks, oracle result, etc.)
            
        Returns:
            str explanation or None if LLM unavailable
        """
        if not self.is_available:
            return None
        
        try:
            prompt = self._build_verdict_prompt(verdict, score, reason, context)
            response = await self._generate_content(prompt)
            return response
        except Exception as e:
            self.logger.error(f"LLM explanation generation failed: {e}")
            return None
    
    async def analyze_fork_detection(
        self,
        user_tip: int,
        mainnet_tip: int,
        delta: int,
        is_fork: bool
    ) -> Optional[str]:
        """
        Generate LLM analysis for fork detection result.
        
        Args:
            user_tip: User's node block height
            mainnet_tip: Mainnet block height
            delta: Block height difference
            is_fork: Whether a fork was detected
            
        Returns:
            str analysis or None if LLM unavailable
        """
        if not self.is_available:
            return None
        
        try:
            prompt = self._build_fork_analysis_prompt(user_tip, mainnet_tip, delta, is_fork)
            response = await self._generate_content(prompt)
            return response
        except Exception as e:
            self.logger.error(f"LLM fork analysis failed: {e}")
            return None
    
    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using the Gemini model."""
        if not self.model:
            raise RuntimeError("LLM model not initialized")
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini generation error: {e}")
            raise
    
    def _build_verdict_prompt(
        self,
        verdict: str,
        score: int,
        reason: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for verdict explanation."""
        context_str = ""
        if context:
            if "compliance" in context:
                checks = context["compliance"].get("checks_performed", [])
                context_str += f"\nCompliance checks: {len(checks)} performed"
            if "oracle_result" in context and context["oracle_result"]:
                oracle = context["oracle_result"]
                context_str += f"\nOracle status: {oracle.get('status', 'unknown')}"
        
        return f"""You are explaining a blockchain security scan result to a user.

**Verdict:** {verdict}
**Risk Score:** {score}/100
**Reason:** {reason}
{context_str}

Generate a clear, user-friendly explanation (2-3 sentences) of what this means.
- If SAFE: Reassure the user about security
- If WARNING: Explain caution needed
- If DANGER: Clearly explain the threat

Use simple language, be direct about any risks."""
    
    def _build_fork_analysis_prompt(
        self,
        user_tip: int,
        mainnet_tip: int,
        delta: int,
        is_fork: bool
    ) -> str:
        """Build prompt for fork detection analysis."""
        return f"""You are a blockchain network analyst explaining fork detection results.

**User's Node Block Height:** {user_tip:,}
**Mainnet Block Height:** {mainnet_tip:,}
**Block Difference (Delta):** {delta}
**Fork Detected:** {'Yes - MINORITY FORK' if is_fork else 'No - Chain is healthy'}

Generate a brief technical explanation (2-3 sentences):
1. What the block height difference means
2. Security implications for the user
3. Recommended action (if fork detected: do not proceed with transaction)

Be concise and technically accurate."""


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

_client_initialized = init_gemini_client()

if _client_initialized:
    logger.info(f"SON LLM module ready with Gemini model: {GEMINI_MODEL}")
else:
    logger.info("SON LLM module loaded in rule-based mode (no LLM)")
