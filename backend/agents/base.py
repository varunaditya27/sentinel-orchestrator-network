"""
=============================================================================
Sentinel Orchestrator Network (SON) - Base Agent Class
=============================================================================

This module provides the base class that all SON agents inherit from.
It defines common functionality like logging, timing, and output formatting.

Simplified Architecture (2 Agents):
- Sentinel: Orchestrator, compliance checker, verdict issuer
- Oracle: Blockchain verifier, fork detection

LLM Integration:
- Uses Gemini (gemini-2.5-flash) as the AI reasoning engine
- LLM is optional - agents fall back to rule-based logic if unavailable
- Configure via GEMINI_API_KEY in .env

=============================================================================
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

# Import LLM configuration
from .llm_config import AgentLLM, GEMINI_MODEL, LLM_ENABLED


# =============================================================================
# ENUMS - Standard vote types used across all agents
# =============================================================================

class Vote(str, Enum):
    """Standard vote values that agents can cast"""
    SAFE = "SAFE"
    WARNING = "WARNING"
    DANGER = "DANGER"


class Severity(str, Enum):
    """Severity levels for findings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    INFO = "info"


# =============================================================================
# BASE AGENT CLASS
# =============================================================================

class BaseAgent(ABC):
    """
    Abstract base class for all SON agents.
    
    Every agent (Sentinel, Oracle) inherits from this class to get 
    common functionality like:
    - Logging with agent name prefix
    - Timestamp generation (ISO 8601)
    - Hash generation for evidence
    - Standard output formatting
    - LLM integration via Gemini API
    
    LLM Configuration:
    - Model: gemini-2.5-flash (configurable via GEMINI_MODEL env var)
    - The LLM enhances agent reasoning but is not required
    - Agents use rule-based fallback when LLM is unavailable
    """
    
    def __init__(self, agent_name: str, role: str, enable_llm: bool = True):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Human-readable name (e.g., "sentinel", "oracle")
            role: CrewAI role type (e.g., "expert_detector")
            enable_llm: Whether to enable LLM capabilities for this agent
        """
        self.agent_name = agent_name
        self.role = role
        
        # Setup logging with agent-specific prefix
        self.logger = logging.getLogger(f"SON.{agent_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                f'[%(asctime)s] [{agent_name.upper()}] %(levelname)s: %(message)s'
            ))
            self.logger.addHandler(handler)
        
        # Initialize LLM helper for enhanced reasoning
        self.llm: Optional[AgentLLM] = None
        if enable_llm and LLM_ENABLED:
            self.llm = AgentLLM(agent_name)
            if self.llm.is_available:
                self.logger.info(f"LLM brain enabled (model: {GEMINI_MODEL})")
            else:
                self.logger.debug("LLM not available - using rule-based logic")
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS - Used by all agents
    # -------------------------------------------------------------------------
    
    def get_timestamp(self) -> str:
        """
        Get current UTC timestamp in ISO 8601 format.
        
        Returns:
            str: Timestamp like "2025-11-28T10:30:00Z"
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def generate_hash(self, data: str) -> str:
        """
        Generate SHA-256 hash of input data.
        Used for evidence hashes and proof references.
        
        Args:
            data: String to hash
            
        Returns:
            str: 64-character hex hash
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def determine_vote(self, score: int) -> Vote:
        """
        Convert a numeric risk score (0-100) to a vote.
        
        Score thresholds:
        - 0-40: SAFE
        - 41-70: WARNING  
        - 71-100: DANGER
        
        Args:
            score: Risk score from 0 to 100
            
        Returns:
            Vote: SAFE, WARNING, or DANGER
        """
        if score <= 40:
            return Vote.SAFE
        elif score <= 70:
            return Vote.WARNING
        else:
            return Vote.DANGER
    
    def log_start(self, policy_id: str) -> None:
        """Log that the agent is starting processing"""
        self.logger.info(f"Starting analysis for policy_id: {policy_id[:16]}...")
    
    def log_complete(self, vote: Vote, score: int) -> None:
        """Log that the agent completed processing"""
        self.logger.info(f"Analysis complete. Vote: {vote.value}, Score: {score}")
    
    @property
    def has_llm(self) -> bool:
        """Check if LLM is available for this agent."""
        return self.llm is not None and self.llm.is_available
    
    # -------------------------------------------------------------------------
    # ABSTRACT METHOD - Must be implemented by each agent
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that each agent must implement.
        
        Args:
            input_data: Dictionary containing input from previous agent or orchestrator
            
        Returns:
            Dict containing agent's output (vote, findings, etc.)
        """
        pass
